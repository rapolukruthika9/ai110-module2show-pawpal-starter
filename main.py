"""
CLI demo for PawPal+.

Phase 4: tasks are added out of order on purpose to prove sort_by_time()
actually sorts, two tasks are scheduled at the same time to prove conflict
warnings fire without crashing, and a recurring task is marked complete to
prove the next occurrence gets created automatically.
"""

from datetime import date

from pawpal_system import Owner, Pet, Priority, Scheduler, Task, minutes_since_midnight


def format_time(minutes: int | None) -> str:
    if minutes is None:
        return "unscheduled"
    hours, mins = divmod(minutes, 60)
    return f"{hours:02d}:{mins:02d}"


def print_tasks(title: str, tasks: list[Task]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if not tasks:
        print("  (no tasks)")
        return
    for task in tasks:
        status = "done" if task.is_complete else "pending"
        due = f" due {task.due_date}" if task.due_date else ""
        print(
            f"  {format_time(task.preferred_time)}  {task.title:<20} "
            f"({task.duration_minutes} min, {task.priority.name}, {task.pet_name}) "
            f"[{status}]{due}"
        )


def main() -> None:
    owner = Owner(name="Jordan", email="jordan@example.com")
    scheduler = Scheduler(owner=owner)

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    whiskers = Pet(name="Whiskers", species="cat", breed="Tabby", age=5)
    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    today = date.today()

    # Added deliberately out of chronological order to prove sort_by_time() works.
    tasks = [
        Task(
            title="Playtime",
            duration_minutes=15,
            priority=Priority.LOW,
            pet_name="Biscuit",
            preferred_time=minutes_since_midnight("18:00"),
        ),
        Task(
            title="Morning walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            pet_name="Biscuit",
            preferred_time=minutes_since_midnight("08:00"),
            is_recurring=True,
            frequency="daily",
            due_date=today,
        ),
        Task(
            title="Vet checkup",
            duration_minutes=45,
            priority=Priority.HIGH,
            pet_name="Whiskers",
            preferred_time=minutes_since_midnight("14:00"),
        ),
        Task(
            title="Feeding",
            duration_minutes=10,
            priority=Priority.HIGH,
            pet_name="Biscuit",
            preferred_time=minutes_since_midnight("08:00"),  # same time as the walk, on purpose
        ),
        Task(
            title="Litter box cleaning",
            duration_minutes=10,
            priority=Priority.MEDIUM,
            pet_name="Whiskers",
            preferred_time=minutes_since_midnight("09:00"),
        ),
    ]
    for task in tasks:
        scheduler.add_task(task)

    print(f"Owner: {owner.name} ({len(owner.pets)} pets, {len(owner.get_all_tasks())} tasks)")

    # --- Sorting ---
    print_tasks("All tasks sorted by time (sort_by_time)", scheduler.sort_by_time())
    print_tasks("All tasks sorted by priority (sort_tasks)", scheduler.sort_tasks())

    # --- Filtering ---
    print_tasks("Tasks for Biscuit only (filter_tasks)", scheduler.filter_tasks(pet_name="Biscuit"))
    print_tasks(
        "Incomplete tasks only (filter_tasks)",
        scheduler.filter_tasks(is_complete=False),
    )

    # --- Conflict detection (lightweight warnings, no crash) ---
    warnings = scheduler.get_conflict_warnings()
    print("\nConflict warnings")
    print("------------------")
    if warnings:
        for w in warnings:
            print(f"  {w}")
    else:
        print("  (none)")

    # --- Recurring task auto-continuation ---
    morning_walk = tasks[1]
    follow_up = scheduler.mark_task_complete(morning_walk)
    print(f"\nMarked '{morning_walk.title}' complete (was due {morning_walk.due_date}).")
    if follow_up:
        print(f"Next occurrence auto-created: due {follow_up.due_date}, is_complete={follow_up.is_complete}")
    print(f"Owner now has {len(owner.get_all_tasks())} tasks (was 5, now includes the new occurrence).")

    # --- Final schedule ---
    print_tasks("Today's Schedule (fits in 90 minutes)", scheduler.build_daily_schedule(90))


if __name__ == "__main__":
    main()
