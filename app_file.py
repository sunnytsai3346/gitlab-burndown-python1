# obsidian_burndown_kit
# This script reads a CSV file, generates a burndown chart, saves it into Obsidian vault, and generates a sprint report markdown file.

import shutil
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os

# === CONFIGURATION ===
DATA_FOLDER = "data"
BACKUP_FOLDER = "backup"
OBSIDIAN_VAULT_PATH = "C:\\Users\\plsun\\OneDrive\\Documents\\Obsidian-books\\MyKnowledgeBase\\Sprint_Reports"

os.makedirs(DATA_FOLDER, exist_ok=True)  
os.makedirs(BACKUP_FOLDER, exist_ok=True)
csv_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith(".csv")]
if not csv_files:
    print("No CSV files found in the data folder.")
    exit()

for csv_file in csv_files:
    # Extract sprint_start and sprint_end from filename (e.g., sprint_2025-03-10_to_2025-03-16.csv)
    try:
        filename_parts = csv_file.replace(".csv", "").split("_")        
        SPRINT_START = datetime.strptime(filename_parts[1], "%Y-%m-%d")
        SPRINT_END = datetime.strptime(filename_parts[3], "%Y-%m-%d")
        print(f"Processing: {csv_file} (Sprint {SPRINT_START} to {SPRINT_END})")
    except Exception as e:
        print(f"Skipping invalid file: {csv_file}, Error: {e}")
        continue

    CSV_FILE_PATH = os.path.join(DATA_FOLDER, csv_file)    
    REPORT_FILE_PATH = os.path.join(OBSIDIAN_VAULT_PATH, f"Sprint_{SPRINT_START.strftime('%Y-%m-%d')}.md")
    CHART_FILE_PATH = os.path.join(OBSIDIAN_VAULT_PATH, f"Sprint_{SPRINT_START.strftime('%Y-%m-%d')}_burndown.png")    

    # === READ CSV DATA ===
    df = pd.read_csv(CSV_FILE_PATH, encoding='utf-8')
    df["closed_at"] = pd.to_datetime(df["closed_at"], errors='coerce')

    total_work = df["story_points"].sum()
    completed_work = df[df["closed_at"].notna()]["story_points"].sum()
    completion_percentage = round((completed_work / total_work) * 100, 2) if total_work > 0 else 0

    # Generate remaining work over time
    sprint_days = (SPRINT_END - SPRINT_START).days + 1
    dates = [SPRINT_START + timedelta(days=i) for i in range(sprint_days)]
    remaining_work = []

    for date in dates:
        work_left = total_work
        for _, row in df.iterrows():
            if pd.notna(row["closed_at"]) and row["closed_at"] <= date:
                work_left -= row["story_points"]
        remaining_work.append(work_left)

    # === GENERATE BURNDOWN CHART ===
    
    plt.figure(figsize=(10,6))
    plt.plot(dates, remaining_work, marker='o', label="Actual Progress")
    plt.plot(dates, [total_work - (i * total_work / sprint_days) for i in range(sprint_days)], '--', label="Ideal Progress")
    plt.xlabel("Sprint Days")
    plt.ylabel("Remaining Work (Story Points)")
    plt.title(f"Sprint Burndown Chart - {SPRINT_START.strftime('%Y-%m-%d')} to {SPRINT_END.strftime('%Y-%m-%d')}")
    plt.legend()
    plt.grid()
    plt.savefig(CHART_FILE_PATH)
    print(f"Burndown chart saved to {CHART_FILE_PATH}")

    # === GENERATE OBSIDIAN SPRINT REPORT ===


    completed_issues = df[df["closed_at"].notna()]
    carryover_issues = df[df["closed_at"].isna()]

    with open(REPORT_FILE_PATH, "w", encoding='utf-8', errors='ignore') as report_file:
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
        report_file.write(f"![[{os.path.basename(CHART_FILE_PATH)}]]\n\n")

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
                            
                

    print(f"Sprint report saved to {REPORT_FILE_PATH}")
    # === MOVE PROCESSED FILE TO BACKUP ===
    shutil.move(CSV_FILE_PATH, os.path.join(BACKUP_FOLDER, csv_file))
    print(f"CSV file moved to {BACKUP_FOLDER}/{csv_file}")

print("All sprints processed successfully.")    
