"""
CLI demo for PawPal+.

Creates an owner with two pets, adds several tasks with different times and
priorities, then prints today's prioritized schedule. This is the
verification step before wiring anything into the Streamlit UI.
"""

from pawpal_system import Owner, Pet, Priority, Scheduler, Task, minutes_since_midnight


def print_schedule(title: str, tasks: list[Task]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if not tasks:
        print("  (no tasks)")
        return
    for task in tasks:
        time_str = "unscheduled"
        if task.preferred_time is not None:
            hours, mins = divmod(task.preferred_time, 60)
            time_str = f"{hours:02d}:{mins:02d}"
        status = "done" if task.is_complete else "pending"
        print(
            f"  {time_str}  {task.title:<20} "
            f"({task.duration_minutes} min, {task.priority.name} priority, "
            f"{task.pet_name}) [{status}]"
        )


def main() -> None:
    owner = Owner(name="Jordan", email="jordan@example.com")
    scheduler = Scheduler(owner=owner)

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3)
    whiskers = Pet(name="Whiskers", species="cat", breed="Tabby", age=5)
    owner.add_pet(biscuit)
    owner.add_pet(whiskers)

    tasks = [
        Task(
            title="Morning walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            pet_name="Biscuit",
            preferred_time=minutes_since_midnight("08:00"),
        ),
        Task(
            title="Feeding",
            duration_minutes=10,
            priority=Priority.HIGH,
            pet_name="Biscuit",
            preferred_time=minutes_since_midnight("08:15"),  # overlaps the walk on purpose
        ),
        Task(
            title="Litter box cleaning",
            duration_minutes=10,
            priority=Priority.MEDIUM,
            pet_name="Whiskers",
            preferred_time=minutes_since_midnight("09:00"),
        ),
        Task(
            title="Vet checkup",
            duration_minutes=45,
            priority=Priority.HIGH,
            pet_name="Whiskers",
            preferred_time=minutes_since_midnight("14:00"),
        ),
        Task(
            title="Playtime",
            duration_minutes=15,
            priority=Priority.LOW,
            pet_name="Biscuit",
            preferred_time=minutes_since_midnight("18:00"),
        ),
    ]
    for task in tasks:
        scheduler.add_task(task)

    print(f"Owner: {owner.name} ({len(owner.pets)} pets, {len(owner.get_all_tasks())} tasks)")

    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nConflicts detected:")
        for a, b in conflicts:
            print(f"  '{a.title}' overlaps '{b.title}'")

    print_schedule("All tasks (priority order)", scheduler.sort_tasks())
    print_schedule("Today's Schedule (fits in 90 minutes)", scheduler.build_daily_schedule(90))

    # demonstrate mark_complete
    tasks[0].mark_complete()
    print(f"\nMarked '{tasks[0].title}' complete: {tasks[0].is_complete}")


if __name__ == "__main__":
    main()
