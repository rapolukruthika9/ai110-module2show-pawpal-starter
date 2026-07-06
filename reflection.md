# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions I identified were: adding a pet, adding/scheduling a care task for a pet, and viewing a prioritized daily schedule. Based on those, I designed four classes:

1. Owner - holds the pet owner's basic info (name, email) and their list of Pet objects. Responsible for adding pets and looking one up by name.
2. Pet - a simple data container for a single pet's info (name, species, breed, age). No behavior of its own; it's referenced by Task and owned by Owner.
3. Task - represents one care task (title, duration, priority, which pet it's for, preferred time, and recurrence info). Responsible for knowing whether it conflicts with another task and whether it's high priority.
4. Scheduler - owns the list of Tasks for an Owner and is responsible for all the "smart" behavior: adding tasks, sorting by priority, detecting time conflicts, expanding recurring tasks, and building an actual daily schedule that fits within available time.

**b. Design changes**

Yes. I switched `Task.priority` from a free-form string to a `Priority` IntEnum and `preferred_time` from an `"HH:MM"` string to an integer count of minutes since midnight, because both were being parsed and compared repeatedly — the enum makes tasks sort directly and the integer makes conflict/overlap checks simple arithmetic instead of string parsing. I also added a `day_of_week` field to anchor weekly recurrence (the original design had no way to say *which* day a weekly task lands on) and moved pet-name validation into `Scheduler.add_task` so a task can't silently reference a pet the owner doesn't have.

**Phase 2 update:** the task list moved off `Scheduler` and onto `Pet` (`pet.tasks`), with `Owner.get_all_tasks()` flattening tasks across all pets and `Scheduler` reading from there instead of keeping its own copy. This avoids two sources of truth for the same tasks and matches how the assignment expects `Pet` to store tasks directly. I also added `Task.is_complete` and `mark_complete()` since Phase 2 required tracking completion status.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three things: available time (`build_daily_schedule`'s `available_minutes` budget), priority (`sort_tasks` puts HIGH-priority tasks first), and time-window conflicts (`detect_conflicts`/`conflicts_with` prevent two overlapping tasks from both landing in the same schedule). I decided time and priority mattered most because those map directly to what a real pet owner cares about first: "can I actually fit this in today" and "what absolutely has to happen." Preferences (like a pet's favorite time of day) weren't built in yet — that's a reasonable next step but wasn't essential for a working v1.

**b. Tradeoffs**

One clear tradeoff: `conflicts_with()` only checks for overlapping time *windows* (start/end minute ranges), not softer scheduling preferences like "don't do two high-energy activities back to back" or minimum gaps between tasks. That's reasonable for this scenario because exact time overlap is an unambiguous, checkable fact (two things literally can't happen at once), while "should there be a buffer between tasks" is a judgment call that varies by owner and pet — building that in now would mean guessing at a rule instead of letting the actual user express a preference later.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI throughout, but for different jobs at each phase: brainstorming the initial class breakdown in Phase 1, scaffolding empty method stubs before I wrote real logic, generating the full method bodies in Phase 2, drafting test cases in Phase 5, and debugging environment issues (a broken venv built from an MSYS2 Python install that couldn't verify SSL certificates when installing packages, which took recreating the venv with the official python.org interpreter to fix). The most helpful prompts were narrow and code-specific — pointing at a specific file and method name and asking "does this match what Phase X requires" rather than open-ended "make this better" requests. Asking it to run and actually execute the demo script before handing anything back also mattered more than any single prompt wording — seeing real terminal output caught issues that just reading the code wouldn't have. Keeping planning/testing conversations separate from implementation ones also helped: when a chat's whole context is "what should I test," the suggestions stay focused on test design instead of drifting back into rewriting the feature itself.

**b. Judgment and verification**

The clearest moment: partway through, the assignment's Phase 2 spec described `Pet` storing its own task list and `Owner` exposing tasks across pets, but my Phase 1 design had put the task list on `Scheduler` instead. Rather than quietly picking one, the AI flagged the mismatch, explained why the Pet-owns-tasks version matched the assignment better (single source of truth, no duplicate task lists to keep in sync), and only made the change after calling it out. I verified it by checking that `Owner.get_all_tasks()` still gave `Scheduler` everything it needed and that no code accidentally still assumed a `Scheduler.tasks` list existed. I also independently re-ran the test suite and CLI demo after that change rather than trusting the explanation alone.

---

## 4. Testing and Verification

**a. What you tested**

The suite covers task completion status, pet task counts, sorting by time (including an all-unscheduled edge case and an empty list), conflict detection (overlapping tasks, back-to-back tasks that should *not* count as conflicts, and zero-task cases), recurrence (daily advances by 1 day, weekly by 7, non-recurring tasks create no follow-up), filtering by pet and by status, and rejecting a task for a pet the owner doesn't have. These mattered because they're exactly the places a scheduler quietly breaks: off-by-one errors in time math, forgetting that "ends exactly when the next starts" isn't an overlap, and recurring tasks either not advancing or advancing by the wrong amount.

**b. Confidence**

I'd put this at 4/5. The core logic is well-tested including boundary cases, and I ran everything myself rather than just trusting green checkmarks reported back to me. What I haven't tested yet: `build_daily_schedule` when a single task's duration exceeds the whole time budget, and conflict behavior across three or more overlapping tasks instead of just pairs. Those would be next if I had more time.

---

## 5. Reflection

**a. What went well**

The architecture holding up across phases without a rewrite — Owner/Pet/Task/Scheduler from Phase 1 is still the same core shape in Phase 6, just with more methods added. That came from treating the UML diagram as a living document I kept updating instead of a one-time drawing.

**b. What you would improve**

I'd build the recurring-task date logic (`due_date`, `next_occurrence_date`) in from Phase 1 instead of bolting it on in Phase 4. The original design used `day_of_week` as an anchor with no actual calendar date, which worked fine until recurrence needed real `timedelta` math — I ended up adding a parallel `due_date` field rather than redesigning the whole recurrence model, which is a bit more patched-together than a version built with dates from the start.

**c. Key takeaway**

Being the "lead architect" meant I had to keep deciding what the AI's output actually meant for *my* system, not just whether the code ran. The AI could generate correct-looking code for either the Phase 1 or Phase 2 task-storage design, but only I could catch that having tasks live in two places (`Scheduler.tasks` and eventually `Pet.tasks`) would create a bug where they drift out of sync. AI is fast at producing plausible code; the human's job is deciding which plausible version is actually the right one for the system as a whole.
