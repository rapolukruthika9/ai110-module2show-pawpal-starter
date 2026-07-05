"""
PawPal+ backend logic layer.

Phase 1: class skeletons only (attributes + empty method stubs).
Scheduling logic gets implemented in later phases.

Scheduler pipeline (the intended order the methods run in):
    expand_recurring() -> detect_conflicts() -> sort_tasks() -> build_daily_schedule()
Each method assumes the ones before it have already produced their output.
"""

from dataclasses import dataclass, field
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
class Pet:
    name: str
    species: str
    breed: str
    age: int


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    pet_name: str
    # Minutes since midnight (e.g. 8 * 60 == 480 for 08:00). None == unscheduled.
    preferred_time: int | None = None
    is_recurring: bool = False
    frequency: str = ""  # "daily" | "weekly"
    # Anchor for weekly recurrence: 0 == Monday ... 6 == Sunday. Required when
    # frequency == "weekly"; ignored otherwise.
    day_of_week: int | None = None

    def end_time(self) -> int | None:
        """Return the task's end as minutes since midnight, or None if unscheduled."""
        pass

    def conflicts_with(self, other: "Task") -> bool:
        """Return True if this task's time window overlaps another task's.

        A task whose preferred_time is None is unscheduled and never conflicts.
        """
        pass

    def is_high_priority(self) -> bool:
        """Return True if this task is marked high priority."""
        pass


@dataclass
class Owner:
    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        pass

    def get_pet_by_name(self, name: str) -> Pet | None:
        """Look up one of this owner's pets by name."""
        pass


@dataclass
class Scheduler:
    owner: Owner
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the scheduler.

        Validates that task.pet_name resolves to one of the owner's pets
        (via owner.get_pet_by_name); a task pointing at an unknown pet is
        rejected rather than silently stored.
        """
        pass

    def sort_tasks(self) -> list[Task]:
        """Return tasks sorted by priority (high first), then by preferred_time."""
        pass

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of tasks whose time windows overlap."""
        pass

    def build_daily_schedule(self, available_minutes: int) -> list[Task]:
        """Choose and order tasks that fit within available_minutes.

        Assumes recurring tasks are already expanded. Uses detect_conflicts to
        avoid placing overlapping tasks in the same schedule, and sort_tasks to
        order what fits.
        """
        pass

    def expand_recurring(self) -> list[Task]:
        """Expand recurring tasks into concrete daily instances.

        "daily" tasks yield one instance per day; "weekly" tasks yield an
        instance only on their day_of_week.
        """
        pass
