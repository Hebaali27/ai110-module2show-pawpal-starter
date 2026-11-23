"""Pet care records and scheduling rules for PawPal+."""
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta

PRIORITIES = ("high", "medium", "low")
FREQUENCIES = ("once", "daily", "weekly")


@dataclass(eq=False)
class Task:
    description: str
    due: datetime
    duration: int = 15
    priority: str = "medium"
    frequency: str = "once"
    completed: bool = False

    def __post_init__(self):
        """Validate a new or edited task before saving it."""
        self.description = self.description.strip()
        if not self.description or self.duration < 1:
            raise ValueError("Enter a task name and a positive duration.")
        if self.priority not in PRIORITIES or self.frequency not in FREQUENCIES:
            raise ValueError("Choose a listed priority and frequency.")

    def mark_complete(self):
        """Record that this occurrence has been completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task):
        """Attach one care task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    minutes_available: int = 60
    pets: list = field(default_factory=list)

    def add_pet(self, name, species):
        """Create a pet with a unique display name for this owner."""
        name = name.strip()
        if not name or any(p.name.casefold() == name.casefold() for p in self.pets):
            raise ValueError("Give each pet a distinct, nonempty name.")
        pet = Pet(name, species)
        self.pets.append(pet)
        return pet

    def get_all_tasks(self):
        """Return (pet, task) pairs so the schedule retains each pet's name."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner):
        """Use this owner's current records for every query."""
        self.owner = owner

    def sort_by_time(self, rows=None):
        """Order pet-task pairs by due date and time."""
        if rows is None:
            rows = self.owner.get_all_tasks()
        return sorted(rows, key=lambda row: row[1].due)

    def filter_tasks(self, day=None, pet_name=None, completed=None):
        """Apply any supplied filters and return matching rows in time order."""
        matches = []
        for pet, task in self.owner.get_all_tasks():
            if day is not None and task.due.date() != day:
                continue
            if pet_name is not None and pet.name != pet_name:
                continue
            if completed is None or task.completed == completed:
                matches.append((pet, task))
        return self.sort_by_time(matches)

    def mark_task_complete(self, pet, task):
        """Complete an occurrence once and attach its successor to the same pet."""
        if not any(p is pet for p in self.owner.pets) or task not in pet.tasks:
            raise ValueError("This task does not belong to this pet and owner.")
        if task.completed:
            return
        days = {"daily": 1, "weekly": 7}.get(task.frequency)
        if days:
            pet.add_task(replace(task, due=task.due + timedelta(days=days)))
        task.mark_complete()

    def conflicts(self, day):
        """Warn about open tasks that have the same start time across all pets."""
        slots = {}
        for pet, task in self.filter_tasks(day=day, completed=False):
            slots.setdefault(task.due, []).append(f"{pet.name} ({task.description})")
        return [f"{due:%H:%M} conflict: " + ", ".join(names)
                for due, names in slots.items() if len(names) > 1]

    def daily_plan(self, day):
        """Choose open tasks by priority within the budget, then show time order."""
        rows = self.filter_tasks(day=day, completed=False)
        ranked = sorted(rows, key=lambda row: PRIORITIES.index(row[1].priority))
        remaining = self.owner.minutes_available
        selected, skipped = [], []
        for pet, task in ranked:
            if task.duration <= remaining:
                selected.append((pet, task))
                remaining -= task.duration
            else:
                skipped.append((pet, task))
        return self.sort_by_time(selected), self.sort_by_time(skipped)
