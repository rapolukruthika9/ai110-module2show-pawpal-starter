"""
PawPal+ backend logic layer.

Phase 4 adds the "algorithmic layer": sorting by time, filtering by pet/status,
automatic recurring-task continuation, and lightweight conflict warnings.

Architecture note (unchanged from Phase 2):
Tasks live on the Pet they belong to (pet.tasks). Owner.get_all_tasks()
flattens tasks across all of an owner's pets, and Scheduler reads from there.

Scheduler pipeline (the intended order the methods run in):
    expand_recurring() -> detect_conflicts() -> sort_tasks() -> build_daily_schedule()
Each method assumes the ones before it have already produced their output.
"""

from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from enum import IntEnum


class Priority(IntEnum):
    """Task priority. IntEnum so tasks sort by value with no string mapping."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


def minutes_since_midnight(hhmm: str) -> int:
    """Convert an "HH:MM" clock string into minutes since midnight."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 60 + int(minutes)


@dataclass
class Task:
    """A single pet care activity, optionally scheduled and/or recurring."""

    title: str
    duration_minutes: int
    priority: Priority
    pet_name: str
    # Minutes since midnight (e.g. 8 * 60 == 480 for 08:00). None == unscheduled.
    preferred_time: int | None = None
    is_recurring: bool = False
    frequency: str = ""  # "daily" | "weekly"
    # Anchor for weekly recurrence: 0 == Monday ... 6 == Sunday. Informational;
    # actual next-occurrence math uses due_date below.
    day_of_week: int | None = None
    # The calendar date this specific instance is due. Required for recurring
    # tasks so we can compute the next occurrence with timedelta.
    due_date: date | None = None
    is_complete: bool = False

    def end_time(self) -> int | None:
        """Return this task's end time in minutes since midnight, or None if unscheduled."""
        if self.preferred_time is None:
            return None
        return self.preferred_time + self.duration_minutes

    def conflicts_with(self, other: "Task") -> bool:
        """Return True if this task's time window overlaps another task's."""
        if self.preferred_time is None or other.preferred_time is None:
            return False
        return self.preferred_time < other.end_time() and other.preferred_time < self.end_time()

    def is_high_priority(self) -> bool:
        """Return True if this task's priority is HIGH."""
        return self.priority == Priority.HIGH

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.is_complete = True

    def next_occurrence_date(self) -> date | None:
        """Return the date this task should next occur on, or None if it can't recur.

        "daily" advances by 1 day, "weekly" advances by 7 days. Returns None if
        the task isn't recurring or has no due_date to advance from.
        """
        if not self.is_recurring or self.due_date is None:
            return None
        if self.frequency == "daily":
            return self.due_date + timedelta(days=1)
        if self.frequency == "weekly":
            return self.due_date + timedelta(days=7)
        return None


@dataclass
class Pet:
    """A pet and the list of care tasks assigned to it."""

    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list."""
        self.tasks.append(task)

    def task_count(self) -> int:
        """Return how many tasks this pet currently has."""
        return len(self.tasks)


@dataclass
class Owner:
    """A pet owner who manages one or more pets."""

    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_pet_by_name(self, name: str) -> Pet | None:
        """Look up one of this owner's pets by name; None if not found."""
        for pet in self.pets:
            if pet.name == name:
                return pet
        return None

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets, flattened into one list."""
        all_tasks: list[Task] = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


@dataclass
class Scheduler:
    """The 'brain': retrieves, organizes, and schedules tasks across an owner's pets."""

    owner: Owner

    def add_task(self, task: Task) -> None:
        """Validate task.pet_name against the owner's pets, then store it on that pet."""
        pet = self.owner.get_pet_by_name(task.pet_name)
        if pet is None:
            raise ValueError(f"No pet named '{task.pet_name}' for this owner.")
        pet.add_task(task)

    def sort_tasks(self) -> list[Task]:
        """Return all of the owner's tasks sorted by priority (high first), then time."""
        tasks = self.owner.get_all_tasks()
        return sorted(
            tasks,
            key=lambda t: (
                -t.priority,
                t.preferred_time if t.preferred_time is not None else float("inf"),
            ),
        )

    def sort_by_time(self) -> list[Task]:
        """Return all of the owner's tasks sorted purely by preferred_time.

        Unlike sort_tasks(), this ignores priority entirely -- it's a plain
        chronological ordering. Unscheduled tasks (preferred_time is None)
        sort to the end.
        """
        tasks = self.owner.get_all_tasks()
        return sorted(
            tasks,
            key=lambda t: t.preferred_time if t.preferred_time is not None else float("inf"),
        )

    def filter_tasks(
        self, pet_name: str | None = None, is_complete: bool | None = None
    ) -> list[Task]:
        """Return tasks filtered by pet name and/or completion status.

        Either filter can be omitted (left as None) to skip it. Calling with
        no arguments returns every task, same as owner.get_all_tasks().
        """
        tasks = self.owner.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if is_complete is not None:
            tasks = [t for t in tasks if t.is_complete == is_complete]
        return tasks

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of tasks (across all pets) whose time windows overlap."""
        tasks = self.owner.get_all_tasks()
        conflicts = []
        for i in range(len(tasks)):
            for j in range(i + 1, len(tasks)):
                if tasks[i].conflicts_with(tasks[j]):
                    conflicts.append((tasks[i], tasks[j]))
        return conflicts

    def get_conflict_warnings(self) -> list[str]:
        """Return human-readable warning strings for overlapping tasks.

        This is the "lightweight" version of conflict detection: it never
        raises, it just describes what it found so the caller (CLI or UI)
        can display a warning instead of the program crashing.
        """
        warnings = []
        for a, b in self.detect_conflicts():
            warnings.append(
                f"Warning: '{a.title}' ({a.pet_name}) overlaps with '{b.title}' ({b.pet_name})"
            )
        return warnings

    def build_daily_schedule(self, available_minutes: int) -> list[Task]:
        """Greedily pick non-conflicting tasks, highest priority first, that fit the time budget."""
        ordered = self.sort_tasks()
        schedule: list[Task] = []
        minutes_used = 0
        for task in ordered:
            if minutes_used + task.duration_minutes > available_minutes:
                continue
            if any(task.conflicts_with(scheduled) for scheduled in schedule):
                continue
            schedule.append(task)
            minutes_used += task.duration_minutes
        return schedule

    def expand_recurring(self, day_of_week: int | None = None) -> list[Task]:
        """Return the tasks that should appear for a given day.

        Non-recurring tasks always appear. "daily" recurring tasks always
        appear. "weekly" recurring tasks appear only when day_of_week matches
        their anchor (pass day_of_week=None to include every recurring task
        regardless of day).
        """
        expanded: list[Task] = []
        for task in self.owner.get_all_tasks():
            if not task.is_recurring:
                expanded.append(task)
            elif task.frequency == "daily":
                expanded.append(task)
            elif task.frequency == "weekly":
                if day_of_week is None or task.day_of_week == day_of_week:
                    expanded.append(task)
        return expanded

    def mark_task_complete(self, task: Task) -> Task | None:
        """Mark a task complete, and if it's recurring, queue up the next occurrence.

        This is the piece that makes recurring tasks self-sustaining: a
        "daily" walk marked done today automatically creates tomorrow's walk;
        a "weekly" vet visit marked done creates next week's. Returns the
        newly created follow-up Task, or None if the task doesn't recur.
        """
        task.mark_complete()
        if not task.is_recurring:
            return None

        next_date = task.next_occurrence_date()
        next_task = replace(task, due_date=next_date, is_complete=False)
        self.add_task(next_task)
        return next_task
