"""
Automated test suite for PawPal+.

Covers:
- Task completion / pet task counts (basic Phase 2 behaviors)
- Sorting correctness (happy path + all-unscheduled edge case)
- Conflict detection (happy path + back-to-back boundary + no-tasks edge case)
- Recurrence logic (daily, weekly, and non-recurring edge case)
- Filtering by pet and by completion status
- Owner/Scheduler validation (task added for an unknown pet)
"""

from datetime import date, timedelta

import pytest

from pawpal_system import Owner, Pet, Priority, Scheduler, Task


def make_task(
    title="Walk",
    pet_name="Biscuit",
    priority=Priority.MEDIUM,
    duration_minutes=20,
    preferred_time=None,
    is_recurring=False,
    frequency="",
    due_date=None,
) -> Task:
    return Task(
        title=title,
        duration_minutes=duration_minutes,
        priority=priority,
        pet_name=pet_name,
        preferred_time=preferred_time,
        is_recurring=is_recurring,
        frequency=frequency,
        due_date=due_date,
    )


@pytest.fixture
def owner_with_pets() -> Owner:
    """An owner with two pets and no tasks yet."""
    owner = Owner(name="Jordan", email="jordan@example.com")
    owner.add_pet(Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3))
    owner.add_pet(Pet(name="Whiskers", species="cat", breed="Tabby", age=5))
    return owner


@pytest.fixture
def scheduler(owner_with_pets) -> Scheduler:
    return Scheduler(owner=owner_with_pets)


# ---------------------------------------------------------------------------
# Basic Task / Pet behaviors
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = make_task()
    assert task.is_complete is False

    task.mark_complete()

    assert task.is_complete is True


def test_adding_task_increases_pet_task_count():
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    assert pet.task_count() == 0

    pet.add_task(make_task(pet_name="Biscuit"))

    assert pet.task_count() == 1


def test_pet_with_no_tasks_has_zero_count():
    """Edge case: a freshly created pet has no tasks."""
    pet = Pet(name="Ghost", species="dog", breed="Unknown", age=1)
    assert pet.task_count() == 0
    assert pet.tasks == []


# ---------------------------------------------------------------------------
# Sorting correctness
# ---------------------------------------------------------------------------

def test_sort_by_time_returns_chronological_order(scheduler):
    scheduler.add_task(make_task(title="Evening", pet_name="Biscuit", preferred_time=18 * 60))
    scheduler.add_task(make_task(title="Morning", pet_name="Biscuit", preferred_time=8 * 60))
    scheduler.add_task(make_task(title="Afternoon", pet_name="Biscuit", preferred_time=14 * 60))

    ordered = scheduler.sort_by_time()

    assert [t.title for t in ordered] == ["Morning", "Afternoon", "Evening"]


def test_sort_by_time_puts_unscheduled_tasks_last(scheduler):
    """Edge case: a task with no preferred_time shouldn't break sorting."""
    scheduler.add_task(make_task(title="No time set", pet_name="Biscuit", preferred_time=None))
    scheduler.add_task(make_task(title="Morning", pet_name="Biscuit", preferred_time=8 * 60))

    ordered = scheduler.sort_by_time()

    assert [t.title for t in ordered] == ["Morning", "No time set"]


def test_sort_by_time_on_empty_task_list_returns_empty(scheduler):
    """Edge case: no tasks at all shouldn't raise an error."""
    assert scheduler.sort_by_time() == []


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_detect_conflicts_flags_overlapping_same_time_tasks(scheduler):
    scheduler.add_task(
        make_task(title="Walk", pet_name="Biscuit", duration_minutes=30, preferred_time=8 * 60)
    )
    scheduler.add_task(
        make_task(title="Feeding", pet_name="Biscuit", duration_minutes=10, preferred_time=8 * 60)
    )

    conflicts = scheduler.detect_conflicts()

    assert len(conflicts) == 1
    titles = {conflicts[0][0].title, conflicts[0][1].title}
    assert titles == {"Walk", "Feeding"}


def test_get_conflict_warnings_returns_readable_strings_not_a_crash(scheduler):
    scheduler.add_task(
        make_task(title="Walk", pet_name="Biscuit", duration_minutes=30, preferred_time=8 * 60)
    )
    scheduler.add_task(
        make_task(title="Feeding", pet_name="Biscuit", duration_minutes=10, preferred_time=8 * 60)
    )

    warnings = scheduler.get_conflict_warnings()

    assert len(warnings) == 1
    assert "Walk" in warnings[0] and "Feeding" in warnings[0]


def test_back_to_back_tasks_do_not_conflict(scheduler):
    """Edge case: one task ending exactly when the next starts is NOT an overlap."""
    scheduler.add_task(
        make_task(title="First", pet_name="Biscuit", duration_minutes=30, preferred_time=8 * 60)
    )
    scheduler.add_task(
        make_task(title="Second", pet_name="Biscuit", duration_minutes=30, preferred_time=8 * 60 + 30)
    )

    assert scheduler.detect_conflicts() == []


def test_no_conflicts_when_no_tasks_exist(scheduler):
    """Edge case: an owner with pets but zero tasks shouldn't error."""
    assert scheduler.detect_conflicts() == []
    assert scheduler.get_conflict_warnings() == []


# ---------------------------------------------------------------------------
# Recurrence logic
# ---------------------------------------------------------------------------

def test_completing_daily_task_creates_next_day_occurrence(scheduler):
    today = date.today()
    daily_walk = make_task(
        title="Morning walk",
        pet_name="Biscuit",
        is_recurring=True,
        frequency="daily",
        due_date=today,
    )
    scheduler.add_task(daily_walk)

    follow_up = scheduler.mark_task_complete(daily_walk)

    assert daily_walk.is_complete is True
    assert follow_up is not None
    assert follow_up.due_date == today + timedelta(days=1)
    assert follow_up.is_complete is False
    # the new occurrence should actually be stored, not just returned
    assert follow_up in scheduler.owner.get_pet_by_name("Biscuit").tasks


def test_completing_weekly_task_creates_next_week_occurrence(scheduler):
    today = date.today()
    weekly_vet = make_task(
        title="Vet checkup",
        pet_name="Whiskers",
        is_recurring=True,
        frequency="weekly",
        due_date=today,
    )
    scheduler.add_task(weekly_vet)

    follow_up = scheduler.mark_task_complete(weekly_vet)

    assert follow_up.due_date == today + timedelta(days=7)


def test_completing_non_recurring_task_creates_no_follow_up(scheduler):
    """Edge case: a one-off task shouldn't spawn a next occurrence."""
    one_off = make_task(title="One-time grooming", pet_name="Biscuit")
    scheduler.add_task(one_off)

    follow_up = scheduler.mark_task_complete(one_off)

    assert follow_up is None
    assert len(scheduler.owner.get_all_tasks()) == 1


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------

def test_filter_tasks_by_pet_name(scheduler):
    scheduler.add_task(make_task(title="Biscuit's walk", pet_name="Biscuit"))
    scheduler.add_task(make_task(title="Whiskers' checkup", pet_name="Whiskers"))

    biscuit_tasks = scheduler.filter_tasks(pet_name="Biscuit")

    assert len(biscuit_tasks) == 1
    assert biscuit_tasks[0].title == "Biscuit's walk"


def test_filter_tasks_by_completion_status(scheduler):
    done_task = make_task(title="Done", pet_name="Biscuit")
    done_task.mark_complete()
    pending_task = make_task(title="Pending", pet_name="Biscuit")
    scheduler.add_task(done_task)
    scheduler.add_task(pending_task)

    incomplete = scheduler.filter_tasks(is_complete=False)

    assert [t.title for t in incomplete] == ["Pending"]


# ---------------------------------------------------------------------------
# Owner / Scheduler validation
# ---------------------------------------------------------------------------

def test_adding_task_for_unknown_pet_raises_value_error(scheduler):
    """Edge case: a task pointing at a pet the owner doesn't have should be rejected."""
    ghost_task = make_task(title="Mystery task", pet_name="NoSuchPet")

    with pytest.raises(ValueError):
        scheduler.add_task(ghost_task)
