# obsidian_burndown_kit
# This script reads a CSV file, generates a burndown chart, saves it into Obsidian vault, and generates a sprint report markdown file.

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# === CONFIGURATION ===
SPRINT_START = datetime(2025, 3, 17)
SPRINT_END = datetime(2025, 3, 25)
OBSIDIAN_VAULT_PATH = "C:\\Users\\plsun\\OneDrive\\Documents\\Obsidian-books\\MyKnowledgeBase\\Sprint_Reports"
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)  
CSV_FILE_PATH = os.path.join(DATA_DIR, f"sprint_{SPRINT_START.strftime('%Y-%m-%d')}_to_{SPRINT_END.strftime('%Y-%m-%d')}.csv")
REPORT_PATH = os.path.join(OBSIDIAN_VAULT_PATH, f"Sprint_{SPRINT_START.strftime('%Y-%m-%d')}.md")
SPRINT_DAYS = (SPRINT_END - SPRINT_START).days + 1

# === READ CSV DATA ===
df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
df["closed_at"] = pd.to_datetime(df["closed_at"], errors='coerce')

total_work = df["story_points"].sum()
completed_work = df[df["closed_at"].notna()]["story_points"].sum()
completion_percentage = round((completed_work / total_work) * 100, 2) if total_work > 0 else 0

# Generate remaining work over time
dates = [SPRINT_START + timedelta(days=i) for i in range(SPRINT_DAYS)]
remaining_work = []

for date in dates:
    work_left = total_work
    for _, row in df.iterrows():
        if pd.notna(row["closed_at"]) and row["closed_at"] <= date:
            work_left -= row["story_points"]
    remaining_work.append(work_left)

# === GENERATE BURNDOWN CHART ===
chart_path = os.path.join(OBSIDIAN_VAULT_PATH, f"Sprint_{SPRINT_START.strftime('%Y-%m-%d')}_burndown.png")
plt.figure(figsize=(10,6))
plt.plot(dates, remaining_work, marker='o', label="Actual Progress")
plt.plot(dates, [total_work - (i * total_work / SPRINT_DAYS) for i in range(SPRINT_DAYS)], '--', label="Ideal Progress")
plt.xlabel("Sprint Days")
plt.ylabel("Remaining Work (Story Points)")
plt.title(f"Sprint Burndown Chart - {SPRINT_START.strftime('%Y-%m-%d')} to {SPRINT_END.strftime('%Y-%m-%d')}")
plt.legend()
plt.grid()
plt.savefig(chart_path)
print(f"Burndown chart saved to {chart_path}")

# === GENERATE OBSIDIAN SPRINT REPORT ===


completed_issues = df[df["closed_at"].notna()]
carryover_issues = df[df["closed_at"].isna()]

with open(REPORT_PATH, "w", encoding='utf-8', errors='ignore') as report_file:
    report_file.write(f"---\n")
    report_file.write(f"date: {SPRINT_START.strftime('%Y-%m-%d')}\n")
    report_file.write(f"completion_percentage: {completion_percentage}%\n")
    report_file.write(f"total_story_points: {total_work}\n")
    report_file.write(f"---\n\n")

    report_file.write(f"# Sprint {SPRINT_START.strftime('%Y-%m-%d')} Review\n\n")    
    report_file.write(f"**Sprint Start:** {SPRINT_START.strftime('%Y-%m-%d')}\n")
    report_file.write(f"**Sprint End:** {SPRINT_END.strftime('%Y-%m-%d')}\n")
    report_file.write(f"**Total Story Points:**  {total_work}\n")
    report_file.write(f"**Remaining Story Points:**   {work_left}\n")
    
    report_file.write(f"# Burndown Chart\n")  
    report_file.write(f"![[{os.path.basename(chart_path)}]]\n\n")

    report_file.write(f"## Completed Issues ({completed_work} Story Points, {completion_percentage}%)\n\n")
    for _, row in completed_issues.iterrows():
        report_file.write(f"- [/] {row['title']}  ({row['story_points']} pts)\n\n")

    report_file.write(f"---\n## Carryover Issues\n\n")
    for _, row in carryover_issues.iterrows():
        report_file.write(f"- [ ] {row['title']}  ({row['story_points']} pts)\n\n")

    report_file.write(f"---\n## Sprint Notes & Observations\n\n")
    report_file.write(f"- Key accomplishments\n\n")
    report_file.write(f"- Blockers faced\n\n")
    report_file.write(f"- Actionable improvements\n\n")

    report_file.write(f"---\n## Sprint Velocity History\n\n")
    # report_file.write(f"```dataview\n") 
    # report_file.write(f"LIST\n") 
    # report_file.write(f"FROM \"Sprint_Reports\"\n") 
    # report_file.write(f"WHERE  !completed \n") 
    # report_file.write(f"SORT closed_at ASC \n") 
    # report_file.write(f"```\n\n")
    report_file.write(f"```dataview\n") 
    report_file.write(f"table date, total_story_points, completion_percentage\n") 
    report_file.write(f"FROM \"Sprint_Reports\"\n")     
    report_file.write(f"sort date desc \n") 
                        
    

print(f"Sprint report saved to {REPORT_PATH}")
