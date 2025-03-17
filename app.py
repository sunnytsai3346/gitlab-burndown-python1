import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Sample sprint details
sprint_start = datetime(2025, 2, 1)
sprint_end = datetime(2025, 2, 14)
sprint_days = (sprint_end - sprint_start).days + 1

# Sample issues with (Created Date, Closed Date, Story Points)
issues = [
    {"id": 1, "created": "2025-02-01", "closed": "2025-02-04", "points": 5},
    {"id": 2, "created": "2025-02-02", "closed": "2025-02-07", "points": 8},
    {"id": 3, "created": "2025-02-03", "closed": None, "points": 13},  # Unfinished task
]

# Create daily progress tracker
dates = [sprint_start + timedelta(days=i) for i in range(sprint_days)]
remaining_work = []
total_work = sum(issue["points"] for issue in issues)

for date in dates:
    work_left = total_work
    for issue in issues:
        if issue["closed"] and datetime.strptime(issue["closed"], "%Y-%m-%d") <= date:
            work_left -= issue["points"]
    remaining_work.append(work_left)

# Plot Burndown Chart
plt.figure(figsize=(8,5))
plt.plot(dates, remaining_work, marker='o', label="Actual Progress")
plt.plot(dates, [total_work - (i * total_work / sprint_days) for i in range(sprint_days)], '--', label="Ideal Progress")
plt.xlabel("Sprint Days")
plt.ylabel("Remaining Work (Story Points)")
plt.title("Sprint Burndown Chart")
plt.legend()
plt.grid()
plt.show()
