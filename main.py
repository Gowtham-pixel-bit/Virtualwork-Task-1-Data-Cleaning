
import pandas as pd
import matplotlib.pyplot as plt
import os

# Create output folder
os.makedirs("output", exist_ok=True)

# 1. Load Dataset
df = pd.read_csv("data/raw_data.csv")
original_rows = len(df)

print("\n===== DATA CLEANING PIPELINE =====")
print("Original Records:", original_rows)

# 2. Remove Duplicates
duplicates = df.duplicated().sum()
df = df.drop_duplicates()

# 3. Handle Missing Values
df["Name"] = df["Name"].fillna("Unknown")
df["Email"] = df["Email"].fillna("Not Provided")
df["Age"] = df["Age"].fillna(df["Age"].median())
df["Salary"] = df["Salary"].fillna(df["Salary"].median())

# 4. Standardize Text
df["Name"] = df["Name"].str.strip().str.title()
df["Email"] = df["Email"].str.strip().str.lower()
df["Department"] = df["Department"].str.strip().str.upper()

# 5. Standardize Dates
df["Join_Date"] = pd.to_datetime(
    df["Join_Date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

# 6. Structural Validation
df["ID"] = pd.to_numeric(df["ID"], errors="coerce")
df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
df["Salary"] = pd.to_numeric(df["Salary"], errors="coerce")

email_valid = df["Email"].str.fullmatch(
    r"[^@\s]+@[^@\s]+\.[^@\s]+", na=False
)

email_unavailable = df["Email"].eq("not provided")

validation = {
    "Unique Employee IDs": df["ID"].notna().all() and df["ID"].is_unique,
    "Valid Email Addresses": (email_valid | email_unavailable).all(),
    "Valid Age": df["Age"].between(18, 100).all(),
    "Valid Salary": df["Salary"].ge(0).all(),
    "Valid Departments": df["Department"].isin(
        ["IT", "HR", "FINANCE"]
    ).all(),
    "Valid Join Dates": df["Join_Date"].notna().all()
}

# 7. Save Cleaned Dataset
df["Join_Date"] = df["Join_Date"].dt.strftime("%Y-%m-%d")
df.to_csv("output/cleaned_data.csv", index=False)

# 8. Generate Cleaning Report
report = [
    "DATA CLEANING AND STRUCTURAL VALIDATION REPORT",
    "=" * 50,
    f"Original Records: {original_rows}",
    f"Duplicates Removed: {duplicates}",
    f"Final Records: {len(df)}",
    "\nVALIDATION RESULTS"
]

for check, result in validation.items():
    report.append(
        f"{check}: {'PASSED' if result else 'FAILED'}"
    )

report.append("\nMISSING VALUES:")
report.append(str(df.isnull().sum()))

with open("output/cleaning_report.txt", "w") as file:
    file.write("\n".join(report))

# 9. Data Visualization

department_count = df["Department"].value_counts()

plt.figure(figsize=(8, 5))
department_count.plot(kind="bar")
plt.title("Employee Count by Department")
plt.xlabel("Department")
plt.ylabel("Number of Employees")
plt.tight_layout()
plt.savefig("output/department_count.png")
plt.close()

salary_data = df.groupby("Department")["Salary"].mean()

plt.figure(figsize=(8, 5))
salary_data.plot(kind="bar")
plt.title("Average Salary by Department")
plt.xlabel("Department")
plt.ylabel("Average Salary")
plt.tight_layout()
plt.savefig("output/average_salary.png")
plt.close()

# 10. Display Results
print("\n===== VALIDATION RESULTS =====")

for check, result in validation.items():
    print(check, ":", "PASSED" if result else "FAILED")

print("\nDuplicates Removed:", duplicates)
print("Final Records:", len(df))

print("\nAll files generated successfully!")
print("Check the output folder.")
