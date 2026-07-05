# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions I identified were: adding a pet, adding/scheduling a care task for a pet, and viewing a prioritized daily schedule. Based on those, I designed four classes:

1. Owner - holds the pet owner's basic info (name, email) and their list of Pet objects. Responsible for adding pets and looking one up by name.
2. Pet - a simple data container for a single pet's info (name, species, breed, age). No behavior of its own; it's referenced by Task and owned by Owner.
3. Task - represents one care task (title, duration, priority, which pet it's for, preferred time, and recurrence info). Responsible for knowing whether it conflicts with another task and whether it's high priority.
4. Scheduler - owns the list of Tasks for an Owner and is responsible for all the "smart" behavior: adding tasks, sorting by priority, detecting time conflicts, expanding recurring tasks, and building an actual daily schedule that fits within available time.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
