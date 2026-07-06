from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Priority, Scheduler, Task, minutes_since_midnight

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
**PawPal+** is a pet care planning assistant. Add your pets, add care tasks for
them, and generate a prioritized daily schedule. The scheduler sorts by time
or priority, filters by pet or completion status, flags overlapping tasks,
and automatically re-creates recurring tasks when you complete them.
"""
)

# ---------------------------------------------------------------------------
# Application "memory" via st.session_state
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", email="jordan@example.com")

if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

st.divider()

# ---------------------------------------------------------------------------
# Owner info
# ---------------------------------------------------------------------------
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner.name = st.text_input("Owner name", value=owner.name)
with col2:
    owner.email = st.text_input("Owner email", value=owner.email)

st.divider()

# ---------------------------------------------------------------------------
# Add a pet -> Owner.add_pet()
# ---------------------------------------------------------------------------
st.subheader("Add a Pet")

with st.form("add_pet_form", clear_on_submit=True):
    pcol1, pcol2, pcol3, pcol4 = st.columns(4)
    with pcol1:
        new_pet_name = st.text_input("Pet name", value="")
    with pcol2:
        new_species = st.selectbox("Species", ["dog", "cat", "other"])
    with pcol3:
        new_breed = st.text_input("Breed", value="")
    with pcol4:
        new_age = st.number_input("Age", min_value=0, max_value=40, value=1)

    submitted_pet = st.form_submit_button("Add pet")
    if submitted_pet:
        if not new_pet_name.strip():
            st.error("Pet name can't be empty.")
        elif owner.get_pet_by_name(new_pet_name) is not None:
            st.error(f"A pet named '{new_pet_name}' already exists.")
        else:
            owner.add_pet(
                Pet(name=new_pet_name, species=new_species, breed=new_breed, age=int(new_age))
            )
            st.success(f"Added {new_pet_name}!")

if owner.pets:
    st.table(
        [
            {"name": p.name, "species": p.species, "breed": p.breed, "age": p.age, "tasks": p.task_count()}
            for p in owner.pets
        ]
    )
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ---------------------------------------------------------------------------
# Add a task -> Scheduler.add_task()
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first before scheduling tasks for them.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        tcol1, tcol2, tcol3 = st.columns(3)
        with tcol1:
            task_title = st.text_input("Task title", value="Morning walk")
        with tcol2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with tcol3:
            priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)

        tcol4, tcol5 = st.columns(2)
        with tcol4:
            task_pet_name = st.selectbox("Pet", [p.name for p in owner.pets])
        with tcol5:
            task_time = st.time_input("Preferred time", value=None)

        rcol1, rcol2 = st.columns(2)
        with rcol1:
            recurring = st.checkbox("Recurring task")
        with rcol2:
            frequency = st.selectbox("Frequency", ["daily", "weekly"], disabled=not recurring)

        submitted_task = st.form_submit_button("Add task")
        if submitted_task:
            preferred_minutes = None
            if task_time is not None:
                preferred_minutes = minutes_since_midnight(
                    f"{task_time.hour:02d}:{task_time.minute:02d}"
                )
            new_task = Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=Priority[priority_label.upper()],
                pet_name=task_pet_name,
                preferred_time=preferred_minutes,
                is_recurring=recurring,
                frequency=frequency if recurring else "",
                due_date=date.today() if recurring else None,
            )
            try:
                scheduler.add_task(new_task)
                st.success(f"Added '{task_title}' for {task_pet_name}!")
            except ValueError as e:
                st.error(str(e))

st.divider()

# ---------------------------------------------------------------------------
# Task list: sorting + filtering + conflict warnings + mark complete
# ---------------------------------------------------------------------------
st.subheader("Tasks")

if not owner.get_all_tasks():
    st.info("No tasks yet. Add one above.")
else:
    fcol1, fcol2, fcol3 = st.columns(3)
    with fcol1:
        pet_filter = st.selectbox("Filter by pet", ["All"] + [p.name for p in owner.pets])
    with fcol2:
        status_filter = st.selectbox("Filter by status", ["All", "Pending", "Complete"])
    with fcol3:
        sort_mode = st.selectbox("Sort by", ["Time", "Priority"])

    # Scheduler.filter_tasks() does the actual filtering; None means "don't filter on this"
    is_complete_filter = {"All": None, "Pending": False, "Complete": True}[status_filter]
    filtered = scheduler.filter_tasks(
        pet_name=None if pet_filter == "All" else pet_filter,
        is_complete=is_complete_filter,
    )
    # Sort the filtered set using the same ordering the Scheduler would use
    ordering = {t.title: i for i, t in enumerate(
        scheduler.sort_by_time() if sort_mode == "Time" else scheduler.sort_tasks()
    )}
    filtered.sort(key=lambda t: ordering.get(t.title, len(ordering)))

    # Conflict warnings, shown prominently so a pet owner notices before their day starts
    warnings = scheduler.get_conflict_warnings()
    for w in warnings:
        st.warning(w)

    for i, task in enumerate(filtered):
        time_str = (
            f"{task.preferred_time // 60:02d}:{task.preferred_time % 60:02d}"
            if task.preferred_time is not None
            else "unscheduled"
        )
        rec_str = f" ({task.frequency})" if task.is_recurring else ""
        row1, row2, row3 = st.columns([3, 1, 1])
        with row1:
            label = f"**{time_str}** — {task.title} ({task.duration_minutes} min, {task.priority.name}, {task.pet_name}){rec_str}"
            if task.is_complete:
                st.markdown(f"~~{label}~~")
            else:
                st.markdown(label)
        with row2:
            if not task.is_complete:
                if st.button("Mark complete", key=f"complete_{i}_{task.title}"):
                    follow_up = scheduler.mark_task_complete(task)
                    if follow_up:
                        st.success(f"Done! Next occurrence created for {follow_up.due_date}.")
                    else:
                        st.success("Marked complete!")
                    st.rerun()
        with row3:
            st.write("✅ done" if task.is_complete else "⏳ pending")

st.divider()

# ---------------------------------------------------------------------------
# Generate schedule -> Scheduler.build_daily_schedule()
# ---------------------------------------------------------------------------
st.subheader("Build Schedule")

available_minutes = st.number_input(
    "Minutes available today", min_value=15, max_value=600, value=120, step=15
)

if st.button("Generate schedule"):
    all_tasks = owner.get_all_tasks()
    if not all_tasks:
        st.warning("Add at least one task first.")
    else:
        for w in scheduler.get_conflict_warnings():
            st.warning(w + " — only one will be placed in today's schedule.")

        schedule = scheduler.build_daily_schedule(int(available_minutes))
        if schedule:
            st.success("Today's Schedule:")
            for t in schedule:
                time_str = (
                    f"{t.preferred_time // 60:02d}:{t.preferred_time % 60:02d}"
                    if t.preferred_time is not None
                    else "unscheduled"
                )
                st.write(f"**{time_str}** — {t.title} ({t.duration_minutes} min, {t.priority.name}, {t.pet_name})")
        else:
            st.info("No tasks fit in the available time.")
