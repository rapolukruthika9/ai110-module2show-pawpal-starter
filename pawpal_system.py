"""
PawPal+ backend logic layer.

Phase 1: class skeletons only (attributes + empty method stubs).
Scheduling logic gets implemented in later phases.
"""

from dataclasses import dataclass, field


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
    priority: str  # "low" | "medium" | "high"
    pet_name: str
    preferred_time: str = ""  # e.g. "08:00"
    is_recurring: bool = False
    frequency: str = ""  # e.g. "daily" | "weekly"

    def conflicts_with(self, other: "Task") -> bool:
        """Return True if this task's time window overlaps another task's."""
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
        """Add a task to the scheduler."""
        pass

    def sort_tasks(self) -> list[Task]:
        """Return tasks sorted by priority (and any other tiebreakers)."""
        pass

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of tasks whose time windows overlap."""
        pass

    def build_daily_schedule(self, available_minutes: int) -> list[Task]:
        """Choose and order tasks that fit within available_minutes."""
        pass

    def expand_recurring(self) -> list[Task]:
        """Expand recurring tasks into concrete daily instances."""
        pass
