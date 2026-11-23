# PawPal+

Plan walks, meals, medication reminders and other care tasks for several pets in one daily schedule. The full schedule shows everything due. A second table shows what fits in the owner's available minutes.

## Run it

From the project folder on macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
python -m streamlit run app.py
```

On Windows PowerShell, activate the environment with `.\.venv\Scripts\Activate.ps1`.

## How it works

An Owner keeps a list of pets. Each Pet keeps its own tasks. A Task stores a description, date and time, duration, priority, frequency and completion status. Scheduler reads all pet-task pairs through Owner.get_all_tasks(). Both the terminal demo and the Streamlit app use the same backend. The web app stores the owner in Streamlit session state. A new session starts with an empty household.

[Draft UML](diagrams/uml_draft.mmd) · [Final UML](diagrams/uml_final.mmd)

## Smarter Scheduling

| Feature | Method | Rule |
|---|---|---|
| Time order | Scheduler.sort_by_time() | Sort by full date and time. Equal times retain their original order. |
| Filters | Scheduler.filter_tasks() | Combine date, pet and completion status. |
| Conflicts | Scheduler.conflicts() | Group all open tasks for the selected day by start time. A shared start produces a warning with the pets and task names. |
| Recurrence | Scheduler.mark_task_complete() | Completing a daily or weekly occurrence adds a fresh open task one or seven days after its scheduled date. Completing it twice creates only one successor. |
| Daily plan | Scheduler.daily_plan() | Consider high priorities first and break ties by earlier start. Skip a task if its duration exceeds the remaining minutes. Display chosen tasks in time order. |

## Demo Walkthrough

1. Enter an owner name and a 40-minute budget in the sidebar. Add Luna (cat) and Milo (dog).
2. Choose Luna and add Medication at 08:00 for 5 minutes, high priority, daily. Add Playtime at noon for 15 minutes, medium priority.
3. Choose Milo and add Breakfast at 08:00 for 10 minutes, high priority. Add Evening walk at 18:00 for 25 minutes, low priority.
4. Open today's schedule. Both 08:00 tasks appear in one conflict warning. The plan has 10 minutes left after medication, breakfast and playtime, so the walk appears under tasks that exceeded the budget. Choose the walk in “Task to manage” to edit it.
5. Choose Luna's medication and click “Mark complete.” Filter by Done to see the completed occurrence. Change the schedule date to tomorrow to see the next dose.

### Sample Output

Running `python main.py` gives:

```text
Today's Schedule
08:00  Luna - Medication
08:00  Milo - Breakfast
12:00  Luna - Playtime
18:00  Milo - Evening walk
08:00 conflict: Luna (Medication), Milo (Breakfast)
40-minute plan: Medication, Breakfast, Playtime
Over budget: Evening walk
Tomorrow: Luna - Medication at 08:00
```

## Testing PawPal+

Run `python -m pytest`. The tests cover task addition and completion, sorting across pets, combined filters, recurring tasks across a year boundary, duplicate completion, conflict warnings, the daily budget, an empty schedule and blank input.

```text
============================= test session starts ==============================
platform linux -- Python 3.12.14, pytest-9.2.0, pluggy-1.7.0
rootdir: /workspace/scratch/aec39d5d516a/PawPal
plugins: anyio-4.16.0
collected 11 items

tests/test_pawpal.py ...........                                         [100%]

============================== 11 passed in 0.02s ==============================
```

Confidence: 4/5. The tests cover the main rules, and the web workflow was checked by adding a pet, saving and editing a daily task, and completing it. Two tasks with different start times can still overlap. The owner reviews the warnings and makes any timing changes.

[CodePath starter project](https://github.com/codepath/ai110-module2show-pawpal-starter)
