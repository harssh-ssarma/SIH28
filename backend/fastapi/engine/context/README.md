# Context Engine - EXPERIMENTAL / OFFLINE USE ONLY

**Status**: ⚠️ **NOT USED IN PRODUCTION RUNTIME**  
**Purpose**: Research, offline analysis, historical signal aggregation  
**Last Used**: Never imported in production code (as of Feb 9, 2026)

---

## ⚠️ WARNING

This directory contains **EXPERIMENTAL CODE** that is:
- ❌ **NOT imported** anywhere in the production codebase
- ❌ **NOT used** during timetable generation
- ❌ **NOT tested** in CI/CD pipeline
- ⚠️ **MAY BE DEPRECATED** in future releases

---

## What is the Context Engine?

The Context Engine was designed as a **read-only signal provider** to aggregate:
- Faculty effectiveness by time slot (historical data)
- Co-enrollment patterns between courses
- Slot popularity metrics
- Semester-level features

**Role**: "Feature provider, not decision maker" (per DESIGN FREEZE)

---

## Why is it Unused?

As of the **DESIGN FREEZE (Feb 9, 2026)**, we simplified the architecture to:
1. **CP-SAT** for hard feasibility
2. **Domain Reduction** for performance
3. **Frozen RL** (optional) for local refinement

The Context Engine was deemed:
- Too complex for production needs
- Not critical for schedule correctness
- Can be added later if proven valuable

---

## Files in This Directory

- `feature_store.py` - Feature storage and retrieval
- `signal_extractor.py` - Extract signals from historical data
- `__init__.py` - Module exports

**Total Usage**: 0 imports across the entire FastAPI codebase

---

## Future Plans

**Option 1**: Keep for offline analysis  
- Use in research notebooks
- Generate reports on historical patterns
- Analyze semester trends

**Option 2**: Remove if unused after 3+ months  
- Archive to `experimental/` folder
- Document in deprecation log

**Option 3**: Integrate if proven valuable  
- Add as optional signal provider
- Use in advanced RL training (offline)
- Document integration strategy

---

## For Developers

**If you're considering using this code:**
1. Review DESIGN_FREEZE.md first
2. Discuss with team (this is frozen architecture)
3. Write tests before integration
4. Ensure it remains read-only (no constraint modifications)

**If you're removing this code:**
1. Delete entire `engine/context/` directory
2. Update DESIGN_FREEZE.md
3. Update CODE_CLEANUP_AUDIT.md
4. No production code will break (verified)

---

**Last Updated**: February 9, 2026  
**Status**: EXPERIMENTAL - Use at your own risk
