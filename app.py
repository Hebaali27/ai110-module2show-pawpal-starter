"""Streamlit interface for the PawPal+ scheduler."""
from datetime import date, datetime, time
import streamlit as st
from pawpal_system import FREQUENCIES, PRIORITIES, Owner, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾")
st.title("🐾 PawPal+")
if "owner" not in st.session_state:
    st.session_state.owner = Owner("Jordan")
owner = st.session_state.owner
scheduler = Scheduler(owner)

with st.sidebar:
    st.header("Owner settings")
    owner.name = st.text_input("Owner name", owner.name).strip()
    owner.minutes_available = st.number_input("Daily care budget (minutes)", 0, 1440, 60)
    with st.form("new_pet", clear_on_submit=True):
        name = st.text_input("New pet name")
        species = st.selectbox("Species", ["dog", "cat", "other"])
        if st.form_submit_button("Add pet"):
            try:
                owner.add_pet(name, species)
                st.success(f"Added {name.strip()}.")
            except ValueError as error:
                st.warning(str(error))

if not owner.pets:
    st.info("Add your first pet in the sidebar to start scheduling.")
    st.stop()

pets = {pet.name: pet for pet in owner.pets}
pet = pets[st.selectbox("Pet to manage", list(pets))]
open_tasks = [task for task in pet.tasks if not task.completed]
choice = st.selectbox("Task to manage", range(-1, len(open_tasks)),
                      format_func=lambda i: "New task" if i == -1 else
                      f"{open_tasks[i].due:%b %d, %H:%M} · {open_tasks[i].description}",
                      key=f"choice_{pet.name}")
old = open_tasks[choice] if choice >= 0 else None
# A new form key reloads the saved values when switching between tasks.
form_key = f"editor_{pet.name}_{id(old)}"
with st.form(form_key):
    title = st.text_input("Task name", old.description if old else "")
    day = st.date_input("Due date", old.due.date() if old else date.today())
    start = st.time_input("Start time", old.due.time() if old else time(8))
    duration = st.number_input("Duration (minutes)", 1, 1440, old.duration if old else 15)
    priority = st.selectbox("Priority", PRIORITIES, PRIORITIES.index(old.priority) if old else 1)
    frequency = st.selectbox("Frequency", FREQUENCIES, FREQUENCIES.index(old.frequency) if old else 0)
    if st.form_submit_button("Save task"):
        try:
            task = Task(title, datetime.combine(day, start), duration, priority, frequency)
            if old:
                pet.tasks[pet.tasks.index(old)] = task
            else:
                pet.add_task(task)
            st.session_state.notice = f"Saved {task.description} for {pet.name}."
            st.rerun()
        except ValueError as error:
            st.warning(str(error))
if old and st.button("Mark complete"):
    scheduler.mark_task_complete(pet, old)
    st.session_state.notice = f"Completed {old.description} for {pet.name}."
    st.rerun()
if "notice" in st.session_state:
    st.success(st.session_state.pop("notice"))


def show_tasks(rows):
    """Show a readable schedule or a short empty-state message."""
    if rows:
        st.table([{"Time": t.due.strftime("%H:%M"), "Pet": p.name,
                   "Task": t.description, "Minutes": t.duration,
                   "Priority": t.priority, "Status": "Done" if t.completed else "Open"}
                  for p, t in rows])
    else:
        st.caption("No matching tasks.")


st.header("Daily schedule")
view_day = st.date_input("Schedule date", date.today())
pet_filter = st.selectbox("Show pets", [None, *pets], format_func=lambda p: p or "All pets")
status = st.selectbox("Show status", ["All", "Open", "Done"])
show_tasks(scheduler.filter_tasks(view_day, pet_filter, {"All": None, "Open": False, "Done": True}[status]))
for warning in scheduler.conflicts(view_day):
    st.warning(warning)

st.subheader(f"{owner.name or 'Owner'}’s plan for all pets")
selected, skipped = scheduler.daily_plan(view_day)
st.caption(f"Budget: {owner.minutes_available} minutes. Higher priorities get first choice. "
           "Within each priority, earlier tasks get first choice. Selected tasks keep their start times.")
show_tasks(selected)
if skipped:
    st.write("These tasks exceeded the minutes left in the plan:")
    show_tasks(skipped)
