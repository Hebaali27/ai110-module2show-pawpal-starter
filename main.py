"""Run a small two-pet schedule in the terminal."""
from datetime import date, datetime, time, timedelta
from pawpal_system import Owner, Scheduler, Task


def main():
    today = date.today()
    owner = Owner("Jordan", 40)
    luna = owner.add_pet("Luna", "cat")
    milo = owner.add_pet("Milo", "dog")
    morning = datetime.combine(today, time(8))
    milo.add_task(Task("Evening walk", morning.replace(hour=18), 25, "low"))
    meds = Task("Medication", morning, 5, "high", "daily")
    luna.add_task(meds)
    milo.add_task(Task("Breakfast", morning, 10, "high"))
    luna.add_task(Task("Playtime", morning.replace(hour=12), 15))
    scheduler = Scheduler(owner)

    print("Today's Schedule")
    for pet, task in scheduler.filter_tasks(day=today):
        print(f"{task.due:%H:%M}  {pet.name} - {task.description}")
    for warning in scheduler.conflicts(today):
        print(warning)
    selected, skipped = scheduler.daily_plan(today)
    print("40-minute plan:", ", ".join(task.description for _, task in selected))
    print("Over budget:", ", ".join(task.description for _, task in skipped))
    scheduler.mark_task_complete(luna, meds)
    tomorrow = today + timedelta(days=1)
    for pet, task in scheduler.filter_tasks(tomorrow, "Luna", False):
        print(f"Tomorrow: {pet.name} - {task.description} at {task.due:%H:%M}")


if __name__ == "__main__":
    main()
