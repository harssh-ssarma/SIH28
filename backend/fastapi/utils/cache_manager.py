"""
Enterprise-grade caching system for timetable scheduling.
Provides intelligent caching with Redis and database synchronization.

Wire protocol for Redis values (1-byte tag + payload):
    _TAG_RAW     = 0x00  — raw UTF-8 JSON bytes
    _TAG_ZSTD    = 0x01  — zstd-compressed UTF-8 JSON bytes
    _TAG_CHUNKED = 0x02  — chunked manifest; chunk keys = {key}:{i}
                          manifest payload = JSON {"n": N, "a": "<hex algo tag>"}
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import hashlib

# ── Wire-protocol tags (single leading byte in every Redis value) ─────────────
_TAG_RAW     = b'\x00'   # raw UTF-8 JSON
_TAG_ZSTD    = b'\x01'   # zstd-compressed UTF-8 JSON
_TAG_CHUNKED = b'\x02'   # main key holds chunk manifest; chunks at {key}:{i}

# Shard into chunks when the compressed payload exceeds this threshold.
# 10 MB is a generous practical ceiling (Redis theoretical max = 512 MB);
# zstd typically shrinks 5 MB student JSON to ~400 KB so chunking is a
# last-resort safety net, not the hot path.
_MAX_STORE_BYTES = 10 * 1024 * 1024   # 10 MB
_CHUNK_SIZE      = 512 * 1024          # 512 KB per chunk shard

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Intelligent cache manager with Redis backend and database fallback.
    
    Features:
    - Multi-level caching (Redis + in-memory)
    - Automatic cache invalidation
    - Smart cache warming
    - Database synchronization
    """
    
    def __init__(self, redis_client=None, db_conn=None):
        self.redis_client = redis_client
        self.db_conn = db_conn
        self.memory_cache = {}  # Fallback in-memory cache
        self.cache_ttl = {
            'courses': 1800,      # 30 minutes
            'faculty': 3600,      # 1 hour
            'rooms': 3600,        # 1 hour
            'students': 1800,     # 30 minutes
            'time_slots': 7200,   # 2 hours
            'config': 86400,      # 24 hours
            'departments': 7200,  # 2 hours
        }

        # ── zstd compression context (level 3 = Google hot-path sweet spot) ──
        try:
            import zstandard as zstd
            # threads=-1 → auto-detect CPU count for multi-threaded compression
            self._zctx = zstd.ZstdCompressor(level=3, threads=-1)
            self._dctx = zstd.ZstdDecompressor()
            self._zstd_available = True
            logger.info("[CACHE] zstd compression enabled (level=3, threads=auto)")
        except ImportError:
            self._zstd_available = False
            logger.warning(
                "[CACHE] zstandard not installed — large payloads stored as raw JSON. "
                "Run: pip install zstandard>=0.23.0"
            )
    
    def _generate_cache_key(self, resource_type: str, org_id: str, **kwargs) -> str:
        """Generate unique cache key with hash for complex parameters"""
        key_parts = [resource_type, org_id]
        
        # Add additional parameters
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")
        
        key = ":".join(str(p) for p in key_parts)
        
        # If key is too long, use hash
        if len(key) > 200:
            key_hash = hashlib.md5(key.encode()).hexdigest()
            key = f"{resource_type}:{org_id}:{key_hash}"
        
        return key
    
    async def get(self, resource_type: str, org_id: str, **kwargs) -> Optional[Any]:
        """
        Get cached data with multi-level fallback.
        Transparently handles raw, zstd-compressed, and chunked Redis values.

        Args:
            resource_type: Type of resource (courses, faculty, rooms, etc.)
            org_id: Organization ID
            **kwargs: Additional parameters for cache key generation

        Returns:
            Cached data if found, None otherwise
        """
        cache_key = self._generate_cache_key(resource_type, org_id, **kwargs)

        # ── L1: Redis (compressed / chunked) ─────────────────────────────────
        if self.redis_client:
            try:
                data = self._redis_get_smart(cache_key)
                if data is not None:
                    logger.debug(f"[CACHE] Redis HIT: {cache_key}")
                    return data
            except Exception as e:
                logger.warning(f"[CACHE] Redis read error: {e}")

        # ── L2: in-process memory cache ───────────────────────────────────────
        if cache_key in self.memory_cache:
            cache_entry = self.memory_cache[cache_key]
            if cache_entry['expires_at'] > datetime.now():
                logger.debug(f"[CACHE] Memory HIT: {cache_key}")
                return cache_entry['data']
            del self.memory_cache[cache_key]

        logger.debug(f"[CACHE] MISS: {cache_key}")
        return None
    
    async def set(self, resource_type: str, org_id: str, data: Any, ttl: Optional[int] = None, **kwargs):
        """
        Cache data in Redis (compressed + optionally chunked) and in-process memory.

        Pipeline:
            1. json.dumps  — compact separators (saves ~10% vs default whitespace)
            2. zstd level-3 — typically 85-92% size reduction on repetitive JSON
            3. if compressed <= 10 MB: single Redis SETEX
               else: shard into 512 KB chunk keys via pipelined SETEX
            4. always mirror to in-process dict for zero-network reads

        Args:
            resource_type: Type of resource
            org_id: Organization ID
            data: Data to cache
            ttl: Time to live in seconds (uses default if not provided)
            **kwargs: Additional parameters for cache key generation
        """
        cache_key = self._generate_cache_key(resource_type, org_id, **kwargs)
        ttl = ttl or self.cache_ttl.get(resource_type, 3600)

        # ── Serialize ─────────────────────────────────────────────────────────
        try:
            raw_bytes: bytes = json.dumps(data, separators=(',', ':')).encode('utf-8')
        except Exception as e:
            logger.error(f"[CACHE] Serialization error for {cache_key}: {e}")
            return

        # ── Compress ──────────────────────────────────────────────────────────
        algo_tag, compressed = self._compress(raw_bytes)
        ratio = len(raw_bytes) / max(len(compressed), 1)
        logger.debug(
            f"[CACHE] {resource_type}: {len(raw_bytes)/1024:.0f} KB → "
            f"{len(compressed)/1024:.0f} KB (×{ratio:.1f} {'zstd' if algo_tag == _TAG_ZSTD else 'raw'})"
        )

        # ── Write to Redis ────────────────────────────────────────────────────
        if self.redis_client:
            try:
                self._redis_set_smart(cache_key, algo_tag, compressed, ttl)
                logger.debug(f"[CACHE] Redis SET: {cache_key} (TTL: {ttl}s, {len(compressed)/1024:.0f} KB)")
            except Exception as e:
                logger.warning(f"[CACHE] Redis write error for {cache_key}: {e}")

        # ── Mirror to in-process memory cache ────────────────────────────────
        self.memory_cache[cache_key] = {
            'data': data,
            'expires_at': datetime.now() + timedelta(seconds=ttl),
        }

        # Evict oldest 20 entries once the dict exceeds 100 keys
        if len(self.memory_cache) > 100:
            sorted_keys = sorted(
                self.memory_cache.keys(),
                key=lambda k: self.memory_cache[k]['expires_at'],
            )
            for old_key in sorted_keys[:20]:
                del self.memory_cache[old_key]
    
    async def invalidate(self, resource_type: str, org_id: str, **kwargs):
        """
        Invalidate cache for specific resource.
        Also cleans up any chunk keys created by _redis_set_smart.

        Args:
            resource_type: Type of resource to invalidate
            org_id: Organization ID
            **kwargs: Additional parameters for cache key generation
        """
        cache_key = self._generate_cache_key(resource_type, org_id, **kwargs)

        if self.redis_client:
            try:
                self._redis_delete_smart(cache_key)
                logger.debug(f"[CACHE] Redis INVALIDATE: {cache_key}")
            except Exception as e:
                logger.warning(f"[CACHE] Redis delete error: {e}")

        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
    
    async def invalidate_pattern(self, pattern: str):
        """
        Invalidate all cache keys matching pattern.
        Also cleans chunk keys (pattern:* wildcard picks them up automatically
        because chunk keys use the base key as a prefix).

        Args:
            pattern: Pattern to match (e.g., "courses:*")
        """
        if self.redis_client:
            try:
                # A single KEYS call using pattern:* also captures chunk keys
                # because they are named {base_key}:{i} — naturally a subset.
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    logger.debug(
                        f"[CACHE] Redis INVALIDATE PATTERN: {pattern} ({len(keys)} keys)"
                    )
            except Exception as e:
                logger.warning(f"[CACHE] Redis pattern delete error: {e}")

        matching_keys = [
            k for k in self.memory_cache.keys() if self._matches_pattern(k, pattern)
        ]
        for key in matching_keys:
            del self.memory_cache[key]
        if matching_keys:
            logger.debug(
                f"[CACHE] Memory INVALIDATE PATTERN: {pattern} ({len(matching_keys)} keys)"
            )
    
    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches pattern (simple * wildcard support)"""
        import re
        regex_pattern = pattern.replace('*', '.*').replace('?', '.')
        return bool(re.match(f"^{regex_pattern}$", key))

    # ── Compression helpers ───────────────────────────────────────────────────

    def _compress(self, data: bytes) -> tuple:
        """
        Compress bytes with zstd level-3.
        Returns (algo_tag, payload) where algo_tag is _TAG_ZSTD or _TAG_RAW.
        Falls back to _TAG_RAW if zstd is unavailable or compression expands data.
        """
        if self._zstd_available:
            try:
                compressed = self._zctx.compress(data)
                if len(compressed) < len(data):
                    return _TAG_ZSTD, compressed
            except Exception as e:
                logger.debug(f"[CACHE] zstd compress error (falling back to raw): {e}")
        return _TAG_RAW, data

    def _decompress(self, algo_tag: bytes, data: bytes) -> bytes:
        """
        Decompress bytes using algo_tag to select the algorithm.
        _TAG_RAW  → return as-is
        _TAG_ZSTD → zstd decompress
        """
        if algo_tag == _TAG_ZSTD and self._zstd_available:
            try:
                return self._dctx.decompress(data)
            except Exception as e:
                logger.warning(f"[CACHE] zstd decompress error: {e}")
                raise
        return data  # raw

    # ── Redis smart read / write / delete (handles chunking transparently) ────

    def _redis_set_smart(self, key: str, algo_tag: bytes, compressed: bytes, ttl: int):
        """
        Store (algo_tag + compressed) in Redis.
        If the payload exceeds _MAX_STORE_BYTES it is sharded into
        _CHUNK_SIZE-byte chunks stored at {key}:{i}, and a manifest is
        written to the main key so _redis_get_smart can reassemble them.
        """
        payload = algo_tag + compressed

        if len(payload) <= _MAX_STORE_BYTES:
            # ── Fast path: single SETEX ──────────────────────────────────────
            self.redis_client.setex(key, ttl, payload)
            return

        # ── Chunked path ─────────────────────────────────────────────────────
        # Split the *compressed* bytes (not the full payload — the algo_tag is
        # recorded in the manifest so chunk bytes need no header).
        chunks = [
            compressed[i : i + _CHUNK_SIZE]
            for i in range(0, len(compressed), _CHUNK_SIZE)
        ]
        n = len(chunks)
        manifest = json.dumps({"n": n, "a": algo_tag.hex()}).encode('utf-8')

        # Write manifest first so readers can't see a partial write
        self.redis_client.setex(key, ttl, _TAG_CHUNKED + manifest)

        # Batch all chunk writes in a single pipeline round-trip (Google-style
        # pipelined writes — avoids N sequential RTTs for N chunks)
        pipe = self.redis_client.pipeline(transaction=False)
        for i, chunk in enumerate(chunks):
            pipe.setex(f"{key}:{i}", ttl, chunk)
        pipe.execute()

        logger.info(
            f"[CACHE] Chunked write: {key} → {n} chunks × "
            f"{_CHUNK_SIZE//1024} KB (total compressed: {len(compressed)/1024:.0f} KB)"
        )

    def _redis_get_smart(self, key: str) -> Optional[Any]:
        """
        Read from Redis and transparently decompress / reassemble chunks.
        Returns the deserialized Python object, or None on cache miss.
        """
        raw = self.redis_client.get(key)
        if raw is None:
            return None

        tag     = raw[:1]
        payload = raw[1:]

        if tag == _TAG_CHUNKED:
            # ── Reassemble chunks via pipelined GET ──────────────────────────
            manifest  = json.loads(payload)
            n         = manifest["n"]
            algo_tag  = bytes.fromhex(manifest["a"])

            pipe = self.redis_client.pipeline(transaction=False)
            for i in range(n):
                pipe.get(f"{key}:{i}")
            chunk_values = pipe.execute()

            if any(c is None for c in chunk_values):
                # Partial expiry — treat as a full cache miss so the caller
                # re-fetches from the DB (consistent read semantics).
                logger.warning(
                    f"[CACHE] Chunked key {key}: {sum(c is None for c in chunk_values)}/{n} "
                    "chunks missing — treating as MISS"
                )
                return None

            compressed = b"".join(chunk_values)
        else:
            algo_tag   = tag
            compressed = payload

        decompressed = self._decompress(algo_tag, compressed)
        return json.loads(decompressed)

    def _redis_delete_smart(self, key: str):
        """
        Delete a Redis key and any associated chunk keys.
        Uses a single pipeline call to avoid multiple round-trips.
        """
        # Check if the key is a chunked manifest before deleting so we can
        # also remove the shard keys.
        try:
            raw = self.redis_client.get(key)
        except Exception:
            raw = None

        pipe = self.redis_client.pipeline(transaction=False)
        pipe.delete(key)

        if raw and raw[:1] == _TAG_CHUNKED:
            try:
                manifest = json.loads(raw[1:])
                for i in range(manifest.get("n", 0)):
                    pipe.delete(f"{key}:{i}")
            except Exception:
                pass  # manifest corrupt — main key deletion is sufficient

        pipe.execute()
    
    async def warm_cache(self, org_id: str, client):
        """
        Pre-load frequently accessed data into cache.
        
        Args:
            org_id: Organization ID
            client: DjangoAPIClient instance for fetching data
        """
        logger.info(f"[CACHE] Warming cache for org {org_id}")
        
        try:
            # Fetch and cache configuration
            config = await self._fetch_and_cache_config(org_id, client)
            
            # Fetch and cache departments
            departments = await self._fetch_and_cache_departments(org_id, client)
            
            logger.debug(f"[CACHE] Cache warmed: config={bool(config)}, departments={len(departments) if departments else 0}")
            
            return {
                'config': config,
                'departments': departments
            }
            
        except Exception as e:
            logger.error(f"[CACHE] Cache warming failed: {e}")
            return None
    
    async def _fetch_and_cache_config(self, org_id: str, client) -> Optional[Dict]:
        """Fetch configuration from database and cache it"""
        try:
            cursor = client.db_conn.cursor()
            cursor.execute("""
                SELECT working_days, slots_per_day, start_time, end_time,
                       slot_duration_minutes, lunch_break_enabled, 
                       lunch_break_start, lunch_break_end
                FROM timetable_config
                WHERE org_id = %s AND is_active = true
                ORDER BY created_at DESC
                LIMIT 1
            """, (org_id,))
            
            config_row = cursor.fetchone()
            cursor.close()
            
            if config_row:
                config = {
                    'working_days': config_row['working_days'],
                    'slots_per_day': config_row['slots_per_day'],
                    'start_time': config_row['start_time'],
                    'end_time': config_row['end_time'],
                    'slot_duration_minutes': config_row['slot_duration_minutes'],
                    'lunch_break_enabled': config_row['lunch_break_enabled'],
                    'lunch_break_start': config_row['lunch_break_start'],
                    'lunch_break_end': config_row['lunch_break_end'],
                }
                
                # Cache for 24 hours
                await self.set('config', org_id, config, ttl=86400)
                logger.debug(f"[CACHE] Cached config: {config['working_days']} days, {config['slots_per_day']} slots/day")
                return config
            
            logger.warning(f"[CACHE] No config found for org {org_id}")
            return None
            
        except Exception as e:
            logger.error(f"[CACHE] Config fetch error: {e}")
            return None
    
    async def _fetch_and_cache_departments(self, org_id: str, client) -> Optional[List[str]]:
        """Fetch departments from database and cache them"""
        try:
            cursor = client.db_conn.cursor()
            cursor.execute("""
                SELECT DISTINCT dept_id 
                FROM courses 
                WHERE org_id = %s
                AND is_active = true
                ORDER BY dept_id
            """, (org_id,))
            
            dept_rows = cursor.fetchall()
            cursor.close()
            
            departments = [row['dept_id'] for row in dept_rows]
            
            # Cache for 2 hours
            await self.set('departments', org_id, departments, ttl=7200)
            logger.debug(f"[CACHE] Cached {len(departments)} departments")
            return departments
            
        except Exception as e:
            logger.error(f"[CACHE] Departments fetch error: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        stats = {
            'memory_cache_size': len(self.memory_cache),
            'memory_cache_keys': list(self.memory_cache.keys())[:10],  # First 10 keys
            'redis_available': self.redis_client is not None,
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info('stats')
                stats['redis_keys'] = self.redis_client.dbsize()
                stats['redis_hits'] = info.get('keyspace_hits', 0)
                stats['redis_misses'] = info.get('keyspace_misses', 0)
                stats['redis_hit_rate'] = (
                    stats['redis_hits'] / (stats['redis_hits'] + stats['redis_misses'])
                    if (stats['redis_hits'] + stats['redis_misses']) > 0 else 0
                )
            except Exception as e:
                logger.warning(f"[CACHE] Stats fetch error: {e}")
        
        return stats
    
    def clear_memory_cache(self) -> int:
        """
        Clear in-memory cache (for memory pressure relief)
        
        Returns:
            Approximate bytes freed
        
        Use case: Called by MemoryMonitor during cleanup
        """
        count = len(self.memory_cache)
        # Estimate size (rough approximation)
        size_bytes = sum(len(str(v)) for v in self.memory_cache.values()) * 2
        
        self.memory_cache.clear()
        logger.info(f"[CACHE] Cleared {count} in-memory cache entries (~{size_bytes/(1024**2):.1f} MB)")
        
        return size_bytes
    
    def clear_all(self) -> int:
        """
        Clear ALL caches (memory + Redis)
        
        Returns:
            Approximate bytes freed
        
        WARNING: This clears everything. Use only for:
        - Manual admin action
        - Critical memory pressure
        - Testing
        """
        total_freed = 0
        
        # Clear memory cache
        total_freed += self.clear_memory_cache()
        
        # Clear Redis cache
        if self.redis_client:
            try:
                keys_deleted = 0
                # Delete only our namespace keys (careful!)
                for pattern in ['courses:*', 'faculty:*', 'rooms:*', 'students:*', 'time_slots:*', 'config:*', 'departments:*']:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                        keys_deleted += len(keys)
                
                logger.debug(f"[CACHE] Cleared {keys_deleted} Redis keys")
                # Rough estimate: assume 10KB per key
                total_freed += keys_deleted * 10 * 1024
            except Exception as e:
                logger.error(f"[CACHE] Redis clear error: {e}")
        
        return total_freed
