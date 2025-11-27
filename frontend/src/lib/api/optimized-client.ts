/**
 * Optimized API Client - Minimal Requests, Maximum Caching
 */

const API_BASE = process.env.NEXT_PUBLIC_DJANGO_API_URL || 'http://localhost:8000/api';

// In-memory cache with TTL
const cache = new Map<string, { data: any; expires: number }>();

function getCached(key: string) {
  const cached = cache.get(key);
  if (cached && cached.expires > Date.now()) {
    return cached.data;
  }
  cache.delete(key);
  return null;
}

function setCache(key: string, data: any, ttlMs: number) {
  cache.set(key, { data, expires: Date.now() + ttlMs });
}

/**
 * Fetch with automatic caching and retry
 */
async function fetchWithCache(url: string, options: RequestInit = {}, ttlMs: number = 120000) {
  const cacheKey = `${url}:${JSON.stringify(options)}`;
  
  // Check cache first
  const cached = getCached(cacheKey);
  if (cached) return cached;
  
  // Fetch with timeout
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 5000); // 5s timeout
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
      credentials: 'include'
    });
    
    clearTimeout(timeout);
    
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const data = await response.json();
    setCache(cacheKey, data, ttlMs);
    return data;
  } catch (error) {
    clearTimeout(timeout);
    throw error;
  }
}

/**
 * Optimized timetables list - minimal data
 */
export async function fetchTimetablesOptimized() {
  return fetchWithCache(`${API_BASE}/optimized/timetables/`, {}, 120000); // 2 min cache
}

/**
 * Optimized faculty list - only names
 */
export async function fetchFacultyOptimized(pageSize: number = 20) {
  return fetchWithCache(
    `${API_BASE}/optimized/faculty/?page_size=${pageSize}`,
    {},
    300000 // 5 min cache
  );
}

/**
 * Optimized departments - heavily cached
 */
export async function fetchDepartmentsOptimized(orgId: string) {
  return fetchWithCache(
    `${API_BASE}/optimized/departments/?organization=${orgId}`,
    {},
    600000 // 10 min cache
  );
}

/**
 * Clear all caches
 */
export function clearCache() {
  cache.clear();
}
