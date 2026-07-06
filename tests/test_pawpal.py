from pawpal_system import Pet, Priority, Task


def make_task(title="Walk", pet_name="Biscuit") -> Task:
    return Task(
        title=title,
        duration_minutes=20,
        priority=Priority.MEDIUM,
        pet_name=pet_name,
    )


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
