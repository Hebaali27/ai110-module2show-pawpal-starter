# PawPal+ Project Reflection

## 1. System design

### a. Initial design

An owner needs to add a pet, schedule or edit a care task, and check what is due across all their pets. The draft has four classes. Owner knows which pets belong to the household. Pet stores its own tasks. Task records one scheduled activity. Scheduler reads tasks from the owner so a dog's walk and a cat's feeding show up on the same schedule.

### b. Design changes

The draft gave Task a mark_complete method. That works for updating one checkbox, but the task has no reference to its pet's list. The final design adds Scheduler.mark_task_complete(pet, task). It can mark today's occurrence done and put tomorrow's occurrence on the right pet without giving every task a link back to its parent.

## 2. Scheduling logic and tradeoffs

### a. Constraints and priorities

Start time matters when reading the plan. Priority matters when choosing what fits. With only 20 minutes available, a 15-minute high-priority feeding and a 5-minute brushing can both fit. A 20-minute low-priority play session scheduled earlier would use up all the time if the selection loop simply started with the earliest task.

### b. Tradeoffs

Conflict detection groups tasks with the same start time. It catches two pets that need attention at 08:00. It misses an 08:00 walk lasting half an hour and an 08:15 feeding. Comparing start and end times would handle that case. The budget is a total for the day and assumes the owner decides how to handle any overlap.

## 3. AI collaboration

### a. How AI was used

ChatGPT implemented the backend and Streamlit forms
### b. Judgment and verification

The initial design relied on Task.mark_complete(). During implementation, the design was revised so the scheduler handles the full completion workflow. A repeat-completion test checks that a second call cannot add another copy of tomorrow's task. A Streamlit interaction check also exercised completion through the same button an owner would use.


## 4. Testing and verification

### a. What was tested

The CLI demo puts two pets on the same schedule. The tests check that a conflict disappears when one of the tasks is done, and that a daily or weekly recurrence crosses December 31 correctly. Other tests cover sorting, filters, the time budget, empty schedules and basic input validation.

### b. Confidence

The verification supports a 4/5 reliability rating for the implemented rules. A useful next test would give three equal-priority tasks the same start time with enough minutes for only two, and check the order in the resulting plan.

## 5. Reflection

### a. What went well

The CLI and web app use the same scheduler. The example in the README can be entered in the browser and checked against the terminal output.

### b. What could improve

Saving the household between sessions would make the app easier to use for real daily routines. Another improvement would be checking overlapping durations as well as identical start times.

### c. Key takeaway

Picking class responsibilities changes how easy the behavior is to verify. Keeping task selection outside the UI made it possible to test the budget with three tasks and no browser.
