import random

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri"]
random.seed(42)


def build_schedule(sections, subjects, faculty, subject_to_fac, weekly_quota, periods_per_day, classrooms):
    """Build schedules for all sections and return a dictionary"""
    schedules = {sec: {d: [None] * periods_per_day for d in DAYS} for sec in sections}

    # 🔹 Track global constraints
    classroom_usage = {d: {p: set() for p in range(periods_per_day)} for d in DAYS}
    faculty_usage = {d: {p: set() for p in range(periods_per_day)} for d in DAYS}

    # 🔹 Round-robin classroom assignment template
    classroom_map = {}
    idx = 0
    for d in DAYS:
        classroom_map[d] = {}
        for p in range(periods_per_day):
            # Rotate classroom priority order for fairness
            rotated = classrooms[idx % len(classrooms):] + classrooms[:idx % len(classrooms)]
            classroom_map[d][p] = rotated
            idx += 1

    # Build expanded list of events per section
    events_per_section = {}
    for sec in sections:
        events = []
        for s in subjects:
            for _ in range(weekly_quota[s]["T"]):
                events.append((s, "T", subject_to_fac[s]))
            for _ in range(weekly_quota[s]["P"]):
                events.append((s, "P", subject_to_fac[s]))
        random.shuffle(events)
        events_per_section[sec] = events

    # Try to assign each section's events
    for sec in sections:
        events = events_per_section[sec]
        positions = [(d, p) for d in DAYS for p in range(periods_per_day)]
        random.shuffle(positions)

        for ev in events:
            s, typ, teacher = ev
            placed = False
            for (d, p) in positions:
                # Already filled?
                if schedules[sec][d][p] is not None:
                    continue

                # Check faculty availability
                if teacher in faculty_usage[d][p]:
                    continue

                # Try classrooms in round-robin order
                for cr in classroom_map[d][p]:
                    if cr not in classroom_usage[d][p]:
                        schedules[sec][d][p] = (s, typ, teacher, cr)
                        classroom_usage[d][p].add(cr)
                        faculty_usage[d][p].add(teacher)
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                raise RuntimeError(f"Could not place {ev} for section {sec}")

    return schedules


def format_schedule(schedule, periods_per_day):
    """Format for HTML template"""
    rows = []
    for d in DAYS:
        row = []
        for p in range(periods_per_day):
            cell = schedule[d][p]
            if cell is None:
                row.append("FREE")
            else:
                sub, typ, teacher, cr = cell
                row.append(f"{cr}: {sub} ({teacher}, {typ})")
        rows.append((d, row))
    return rows