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

**What's covered:**
- **Basic behaviors** — marking a task complete, adding a task increases a pet's task count, a fresh pet starts with zero tasks
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological order, unscheduled tasks sort last, an empty task list doesn't error
- **Conflict detection** — overlapping same-time tasks are flagged (both the raw pairs and the human-readable warning strings), back-to-back tasks (one ending exactly when the next starts) are correctly treated as *not* conflicting, and zero tasks produces zero conflicts
- **Recurrence logic** — completing a daily task creates a new occurrence due exactly 1 day later, completing a weekly task creates one due 7 days later, and completing a one-off (non-recurring) task creates no follow-up
- **Filtering** — filtering by pet name and by completion status each return the correct subset
- **Validation** — adding a task for a pet the owner doesn't have raises a `ValueError` instead of silently corrupting data

Sample test output:

```
collected 16 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  6%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 12%]
tests/test_pawpal.py::test_pet_with_no_tasks_has_zero_count PASSED       [ 18%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 25%]
tests/test_pawpal.py::test_sort_by_time_puts_unscheduled_tasks_last PASSED [ 31%]
tests/test_pawpal.py::test_sort_by_time_on_empty_task_list_returns_empty PASSED [ 37%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlapping_same_time_tasks PASSED [ 43%]
tests/test_pawpal.py::test_get_conflict_warnings_returns_readable_strings_not_a_crash PASSED [ 50%]
tests/test_pawpal.py::test_back_to_back_tasks_do_not_conflict PASSED     [ 56%]
tests/test_pawpal.py::test_no_conflicts_when_no_tasks_exist PASSED       [ 62%]
tests/test_pawpal.py::test_completing_daily_task_creates_next_day_occurrence PASSED [ 68%]
tests/test_pawpal.py::test_completing_weekly_task_creates_next_week_occurrence PASSED [ 75%]
tests/test_pawpal.py::test_completing_non_recurring_task_creates_no_follow_up PASSED [ 81%]
tests/test_pawpal.py::test_filter_tasks_by_pet_name PASSED               [ 87%]
tests/test_pawpal.py::test_filter_tasks_by_completion_status PASSED      [ 93%]
tests/test_pawpal.py::test_adding_task_for_unknown_pet_raises_value_error PASSED [100%]

16 passed in 0.11s
```

**Confidence Level:** ⭐⭐⭐⭐☆ (4/5) — the core scheduling logic (sorting, conflicts, recurrence, filtering) is well covered including boundary cases like back-to-back tasks and empty task lists. I'd want to add tests around `build_daily_schedule`'s time-budget behavior (e.g. a task that alone exceeds `available_minutes`) and multi-pet conflict scenarios before calling this 5/5.

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
