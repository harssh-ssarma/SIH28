# Migration: Recalculate Variants with New Academic Formula

**Type**: Data Migration (One-time operation)  
**Purpose**: Recalculate all existing variants with new formula and save permanently  
**Status**: Ready to execute  

---

## Problem It Solves

```
BEFORE Migration:
├─ Old variants: Scored with weighted-average formula (old)
├─ New variants: Scored with academic formula (new)
└─ ❌ INCONSISTENT: Same schedule gets different scores!

AFTER Migration:
├─ All variants: Scored with academic formula (new)
├─ Scores SAVED in database (formula_version='2')
└─ ✅ CONSISTENT: Every score recalculated once, then reused
```

---

## How It Works

### Step 1: Migration Execution
```bash
python manage.py migrate academics 0XXX_recalculate_variants_academic_formula
```

**What happens**:
1. ✅ Reads all GenerationJob records with timetable_data
2. ✅ For each variant in timetable_data:
   - Extracts conflict_count, total_classes, scores
   - Recalculates using NEW academic formula
   - Saves the score back to database
   - Marks with formula_version='2' and recalculated_at timestamp
3. ✅ Prints summary: total jobs, variants, updates, errors

### Step 2: Persistent Storage
```python
# In database (timetable_data JSONB):
{
  "variants": [
    {
      "id": "...",
      "timetable_entries": [...],
      "quality_metrics": {...},
      "overall_score": 85,                    # ← NEW: Recalculated value
      "formula_version": "2",                 # ← NEW: Marks as migrated
      "recalculated_at": "2026-04-29T10:00Z", # ← NEW: Timestamp
      "old_score": 78                         # ← NEW: Backup of old value
    }
  ]
}
```

### Step 3: API Usage (No Recalculation)
```python
# In _build_variant_summary():

# Check if already recalculated
if formula_version == "2" and "overall_score" in variant:
    # ✅ Use saved score (FAST - no calculation)
    score_overall = variant.get("overall_score")
else:
    # ⚠️ Calculate on-the-fly (SLOW - for new variants)
    score_overall = self._compute_overall_score(...)
```

---

## Data Structure Changes

### Before Migration
```json
{
  "variants": [
    {
      "quality_metrics": {
        "overall_score": 78,
        "total_conflicts": 3
        // ... other metrics
      },
      "timetable_entries": [...]
    }
  ]
}
```

### After Migration
```json
{
  "variants": [
    {
      "quality_metrics": {
        "overall_score": 85,  // ← Recalculated with new formula
        "total_conflicts": 3
        // ... other metrics
      },
      "timetable_entries": [...],
      // ← NEW FIELDS:
      "formula_version": "2",
      "recalculated_at": "2026-04-29T10:00:00Z",
      "old_score": 78  // ← Optional: backup of old score
    }
  ]
}
```

---

## Migration Safety Features

### ✅ Error Handling
```python
try:
    # Recalculate
    new_score = calculate_academic_score(...)
    variant['overall_score'] = new_score
    variant['formula_version'] = '2'
except Exception as e:
    # ⚠️ Log error but keep original variant
    print(f"Error recalculating variant: {e}")
    # Do NOT mark as migrated (formula_version stays '1')
    # Next run will retry
```

### ✅ Idempotent (Safe to Run Multiple Times)
```python
# Check: if already migrated, skip
if variant.get('formula_version') == '2':
    # Already done, don't recalculate again
    updated_variants.append(variant)
    continue
```

### ✅ Rollback Capability
```bash
# If needed:
python manage.py migrate academics 0XXX_previous_migration

# This removes formula_version and recalculated_at fields
# Variants will be recalculated on-the-fly (but scores won't recover)
```

---

## Performance Impact

### During Migration
```
Execution Time: Depends on variant count
  - 100 variants:   ~100ms
  - 1,000 variants: ~1s
  - 10,000 variants: ~10s
  - 100,000 variants: ~2 minutes

Database I/O: Significant (reading/writing timetable_data)
Memory: O(1) per variant (processed sequentially)
```

### After Migration
```
✅ API Response Time: FASTER (uses saved scores)
   - Before: Recalculate + return (milliseconds)
   - After: Just return (microseconds)

✅ No Performance Penalty: formula_version check is O(1) dict lookup
```

---

## Verification

### Immediate Checks
```bash
# 1. Count migrated variants
python manage.py shell
>>> from academics.models import GenerationJob
>>> jobs = GenerationJob.objects.filter(timetable_data__isnull=False)
>>> migrated = sum(1 for j in jobs for v in j.timetable_data.get('variants', []) if v.get('formula_version') == '2')
>>> print(f"Migrated: {migrated} variants")

# 2. Check for errors
>>> errors = sum(1 for j in jobs for v in j.timetable_data.get('variants', []) if v.get('formula_version') != '2' and 'overall_score' in v.get('quality_metrics', {}))
>>> print(f"Potential errors: {errors}")
```

### Score Comparison
```bash
# 2. Compare old vs new scores
python manage.py shell
>>> from academics.models import GenerationJob
>>> for job in GenerationJob.objects.filter(timetable_data__isnull=False)[:1]:
...     for variant in job.timetable_data['variants'][:1]:
...         old = variant.get('old_score')
...         new = variant.get('overall_score')
...         diff = new - old if old else None
...         print(f"Old: {old}, New: {new}, Diff: {diff:+.1f}")
```

### Timestamp Verification
```bash
# 3. Verify migration timestamp
python manage.py shell
>>> from academics.models import GenerationJob
>>> job = GenerationJob.objects.filter(timetable_data__isnull=False).first()
>>> variant = job.timetable_data['variants'][0]
>>> print(variant.get('recalculated_at'))
# Should be: 2026-04-29T10:XX:XXZ (or whenever migration ran)
```

---

## API Response Changes

### Variant Summary Response
```json
{
  "id": "job-123-variant-1",
  "overall_score": 85,
  "quality_metrics": {
    "overall_score": 85,
    // ... other metrics
  },
  "scoring_metadata": {
    "formula_version": "2",
    "recalculated_at": "2026-04-29T10:00:00Z",
    "is_persistent_score": true
  }
}
```

**What this means for frontend**:
- `is_persistent_score=true`: Score came from database (migrated)
- `is_persistent_score=false`: Score calculated on-the-fly (new variant)
- Can display "⚙️ Recalculated Apr 29" badge if needed

---

## Usage in Code

### Django ViewSet
```python
# Already handled in _build_variant_summary():

formula_version = v.get("formula_version", "1")
if formula_version == "2" and "overall_score" in v:
    score_overall = v.get("overall_score")  # ← FAST: Use saved score
else:
    score_overall = self._compute_overall_score(...)  # ← Calculate if needed
```

### Python Management Command
```bash
# If you want to recalculate specific variants:
python manage.py migrate academics 0XXX_recalculate_variants_academic_formula

# Or rollback:
python manage.py migrate academics 0XXX_previous_migration
```

---

## Common Questions

**Q: Will old variants lose their original scores?**  
A: No. Old scores are backed up in `variant['old_score']` for reference.

**Q: What if migration fails halfway through?**  
A: It's safe. Partially migrated variants will have `formula_version='2'`, others will have `'1'`. Rerunning migration will skip done ones and fix failures.

**Q: Can I have both formula versions in database?**  
A: Yes! Migration marks variants as `formula_version='1'` (old) or `'2'` (new), so mixed databases are fine.

**Q: Will scores change after migration?**  
A: Only if old and new formulas are different (which they are). After migration, scores won't change anymore (unless you regenerate variants).

**Q: How do I verify migration worked?**  
A: Check the printed summary during migration, or run verification queries above.

**Q: Is it safe to delete old_score field later?**  
A: Yes, once you're confident the new formula is correct, you can delete the `old_score` field to save space.

---

## Rollback Plan

### If You Need to Revert
```bash
# 1. Rollback migration
python manage.py migrate academics 0XXX_previous_migration

# 2. This removes:
#    - formula_version field
#    - recalculated_at field
#    - old_score field (optional)

# 3. Variants will recalculate on-the-fly using old formula
#    (Note: actual old scores are lost after rollback)
```

### If You Find Bugs in New Formula
```bash
# 1. Fix bug in TimetableVariantViewSet._compute_overall_score()
# 2. Create new migration to recalculate
# 3. Run new migration (idempotent check prevents double-calc)
```

---

## Migration Checklist

Before running:
- [ ] Backup database
- [ ] Test on staging environment first
- [ ] Verify formula logic is correct
- [ ] Check estimated time (count variants)
- [ ] Schedule during maintenance window if needed

After running:
- [ ] Verify migration completed (check printed summary)
- [ ] Spot-check scores (compare old vs new)
- [ ] Test API endpoints
- [ ] Monitor application logs for errors
- [ ] Verify performance is good (scores should be faster now)

---

## File Details

**Migration File**: `backend/django/academics/migrations/0XXX_recalculate_variants_academic_formula.py`

**Key Functions**:
- `recalculate_variants_forward()` - Executes migration
- `recalculate_variants_backward()` - Rollback migration
- `extract_faculty_score()` - Helper
- `extract_student_score()` - Helper
- `calculate_academic_score()` - Core formula

**Dependencies**: None (self-contained migration)

---

**Created**: 2026-04-29  
**Status**: Ready to execute  
**Estimated Impact**: One-time data transformation, permanent score storage
