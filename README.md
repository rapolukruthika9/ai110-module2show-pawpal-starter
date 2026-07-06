# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

```
Owner: Jordan (2 pets, 5 tasks)

All tasks sorted by time (sort_by_time)
---------------------------------------
  08:00  Morning walk         (30 min, HIGH, Biscuit) [pending] due 2026-07-06
  08:00  Feeding              (10 min, HIGH, Biscuit) [pending]
  09:00  Litter box cleaning  (10 min, MEDIUM, Whiskers) [pending]
  14:00  Vet checkup          (45 min, HIGH, Whiskers) [pending]
  18:00  Playtime             (15 min, LOW, Biscuit) [pending]

Tasks for Biscuit only (filter_tasks)
-------------------------------------
  18:00  Playtime             (15 min, LOW, Biscuit) [pending]
  08:00  Morning walk         (30 min, HIGH, Biscuit) [pending] due 2026-07-06
  08:00  Feeding              (10 min, HIGH, Biscuit) [pending]

Conflict warnings
------------------
  Warning: 'Morning walk' (Biscuit) overlaps with 'Feeding' (Biscuit)

Marked 'Morning walk' complete (was due 2026-07-06).
Next occurrence auto-created: due 2026-07-07, is_complete=False
Owner now has 6 tasks (was 5, now includes the new occurrence).

Today's Schedule (fits in 90 minutes)
-------------------------------------
  08:00  Morning walk         (30 min, HIGH, Biscuit) [done] due 2026-07-06
  14:00  Vet checkup          (45 min, HIGH, Whiskers) [pending]
  09:00  Litter box cleaning  (10 min, MEDIUM, Whiskers) [pending]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
collected 2 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 50%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [100%]

============================== 2 passed in 0.01s ===============================
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()`, `Scheduler.sort_tasks()` | `sort_by_time()` is pure chronological order; `sort_tasks()` sorts by priority first, then time. Unscheduled tasks sort to the end. |
| Filtering | `Scheduler.filter_tasks(pet_name=..., is_complete=...)` | Either filter is optional; can filter by pet, by completion status, or both at once. |
| Conflict handling | `Scheduler.detect_conflicts()`, `Scheduler.get_conflict_warnings()` | `detect_conflicts()` returns raw overlapping task pairs; `get_conflict_warnings()` wraps that into human-readable warning strings so the UI/CLI can display a warning instead of crashing. |
| Recurring tasks | `Task.next_occurrence_date()`, `Scheduler.mark_task_complete()` | Marking a recurring task complete via `mark_task_complete()` automatically creates the next occurrence (`due_date + timedelta(days=1)` for daily, `+7` for weekly) and adds it to the schedule. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
