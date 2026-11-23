from datetime import datetime, timedelta
import pytest
from pawpal_system import Owner, Scheduler, Task


@pytest.fixture
def household():
    owner = Owner("Jordan", 20)
    cat = owner.add_pet("Luna", "cat")
    dog = owner.add_pet("Milo", "dog")
    return Scheduler(owner), cat, dog


MORNING = datetime(2026, 12, 31, 8)


def test_mark_complete():
    task = Task("Food", MORNING)
    task.mark_complete()
    assert task.completed


def test_add_task(household):
    _, cat, dog = household
    task = Task("Food", MORNING)
    cat.add_task(task)
    assert cat.tasks == [task]
    assert dog.tasks == []


def test_sort_across_pets(household):
    scheduler, cat, dog = household
    late = Task("Brush", MORNING + timedelta(hours=3))
    early = Task("Walk", MORNING)
    cat.add_task(late)
    dog.add_task(early)
    assert scheduler.sort_by_time() == [(dog, early), (cat, late)]


@pytest.mark.parametrize("frequency,days", [("daily", 1), ("weekly", 7), ("once", 0)])
def test_completion_and_recurrence(household, frequency, days):
    scheduler, cat, _ = household
    task = Task("Food", MORNING, 5, "high", frequency)
    cat.add_task(task)
    scheduler.mark_task_complete(cat, task)
    scheduler.mark_task_complete(cat, task)
    assert task.completed
    assert len(cat.tasks) == (2 if days else 1)
    if days:
        new = cat.tasks[1]
        assert new.due == MORNING + timedelta(days=days)
        assert (new.description, new.frequency, new.priority, new.duration, new.completed) == (
            "Food", frequency, "high", 5, False)


def test_conflicts_use_both_pets_and_date(household):
    scheduler, cat, dog = household
    cat.add_task(Task("Food", MORNING))
    dog.add_task(Task("Walk", MORNING))
    dog.add_task(Task("Brush", MORNING + timedelta(days=1)))
    assert scheduler.conflicts(MORNING.date()) == ["08:00 conflict: Luna (Food), Milo (Walk)"]
    scheduler.mark_task_complete(cat, cat.tasks[0])
    assert scheduler.conflicts(MORNING.date()) == []


def test_filters(household):
    scheduler, cat, dog = household
    done = Task("Food", MORNING, completed=True)
    cat.add_task(done)
    cat.add_task(Task("Brush", MORNING))
    dog.add_task(Task("Walk", MORNING, completed=True))
    assert scheduler.filter_tasks(MORNING.date(), "Luna", True) == [(cat, done)]


def test_budget_and_priorities(household):
    scheduler, cat, dog = household
    play = Task("Play", MORNING, 20, "low")
    food = Task("Food", MORNING + timedelta(hours=1), 15, "high")
    brush = Task("Brush", MORNING, 5, "medium")
    cat.add_task(play)
    dog.add_task(food)
    cat.add_task(brush)
    assert scheduler.daily_plan(MORNING.date()) == ([(cat, brush), (dog, food)], [(cat, play)])


def test_empty_household_plan(household):
    scheduler, _, _ = household
    assert scheduler.daily_plan(MORNING.date()) == ([], [])


def test_blank_title():
    with pytest.raises(ValueError):
        Task("  ", MORNING)
