# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I picked three things a user should be able to do: add a pet, add a task for a pet, and see a schedule for the day. To make that work, I made four classes:

1. **Owner** - stores the person's name and email, and their list of pets.
2. **Pet** - stores basic info like name, species, breed, and age.
3. **Task** - one thing to do, like a walk or a vet visit. Knows its time, priority, and which pet it's for.
4. **Scheduler** - the part that does the actual work: sorting tasks, checking for time conflicts, and building the day's schedule.

**b. Design changes**

Yes, a few things changed. I switched task priority from plain text (like "high") to a proper `Priority` type, and switched task times from text like "08:00" to numbers (minutes since midnight). This made comparing times and sorting much easier and less error-prone. I also moved the task list so it lives on each `Pet` instead of on the `Scheduler`, so there's only one place tasks are stored instead of two lists that could get out of sync.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler looks at three things: how much time is available, how important each task is, and whether two tasks overlap in time. Time and priority mattered most because they answer the two questions a pet owner actually has: "can I fit this in today" and "what has to happen no matter what."

**b. Tradeoffs**

The scheduler only checks for exact time overlaps, it doesn't worry about things like leaving a gap between tasks. That's fine for now because "do two times overlap" is a clear yes/no question, while "should there be a break in between" is more of a personal preference I didn't build in yet.

---

## 3. AI Collaboration

**a. How I used AI**

I used AI to help plan the classes, write the code, write tests, and fix errors (like a broken Python setup on my computer). The most helpful thing was asking specific questions about one file or method at a time, instead of vague ones like "make this better."

**b. Judgment and verification**

At one point, my task list was stored in the `Scheduler` class, but the assignment expected it to live on the `Pet` class instead. Rather than just changing it quietly, the mismatch was pointed out to me first, explained why the `Pet` version made more sense, and then updated. I double-checked it myself by re-running my tests and demo script afterward to make sure nothing broke.

---

## 4. Testing and Verification

**a. What I tested**

I tested that tasks sort correctly by time, that overlapping tasks get flagged as conflicts (but back-to-back tasks don't), that recurring tasks create a new copy for the next day or week, and that filtering by pet or status works. These are the spots where a scheduler is most likely to have a hidden bug.

**b. Confidence**

I'd say I'm fairly confident. Most of the important cases are tested and I ran everything myself to check. If I had more time, I'd test what happens if a single task is longer than the whole time budget, or if three or more tasks overlap at once instead of just two.

---

## 5. Reflection

**a. What went well**

The class design from the very beginning held up the whole way through. I didn't have to rebuild it from scratch, just add more to it.

**b. What I would improve**

I'd add real calendar dates to tasks from the start, instead of adding them later just for the recurring-task feature. It works now, but it would've been cleaner built in from day one.

**c. Key takeaway**

AI can write working code fast, but it can't always tell which version of a design is actually the right one for the bigger picture, that part is still on me to decide and check.