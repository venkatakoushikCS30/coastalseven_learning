import pandas as pd

# ==================================================
# SAMPLE DATA
# ==================================================

data = {
    "Department": ["IT", "IT", "HR", "HR", "Sales", "Sales"],
    "Employee": ["A", "B", "C", "D", "E", "F"],
    "Salary": [50000, 60000, 45000, 55000, 40000, 70000],
    "Experience": [2, 4, 1, 3, 2, 5],
    "Gender": ["M", "F", "M", "F", "M", "F"]
}

df = pd.DataFrame(data)

print("\n===== ORIGINAL DATAFRAME =====")
print(df)

# ==================================================
# 1. BASIC GROUPBY
# ==================================================

print("\n===== GROUPBY OBJECT =====")
print(df.groupby("Department"))

# ==================================================
# 2. SUM
# ==================================================

print("\n===== SUM OF SALARY =====")
print(df.groupby("Department")["Salary"].sum())

# ==================================================
# 3. MEAN
# ==================================================

print("\n===== AVERAGE SALARY =====")
print(df.groupby("Department")["Salary"].mean())

# ==================================================
# 4. COUNT
# ==================================================

print("\n===== EMPLOYEE COUNT =====")
print(df.groupby("Department")["Employee"].count())

# ==================================================
# 5. MIN
# ==================================================

print("\n===== MIN SALARY =====")
print(df.groupby("Department")["Salary"].min())

# ==================================================
# 6. MAX
# ==================================================

print("\n===== MAX SALARY =====")
print(df.groupby("Department")["Salary"].max())

# ==================================================
# 7. MULTIPLE AGGREGATIONS
# ==================================================

print("\n===== MULTIPLE AGGREGATIONS =====")
print(
    df.groupby("Department")["Salary"].agg(
        ["sum", "mean", "min", "max"]
    )
)

# ==================================================
# 8. GROUPBY MULTIPLE COLUMNS
# ==================================================

print("\n===== GROUPBY DEPARTMENT + GENDER =====")
print(
    df.groupby(["Department", "Gender"])["Salary"].mean()
)

# ==================================================
# 9. AS_INDEX = FALSE
# ==================================================

print("\n===== AS_INDEX = FALSE =====")
print(
    df.groupby("Department", as_index=False)["Salary"].sum()
)

# ==================================================
# 10. MULTIPLE NUMERIC COLUMNS
# ==================================================

print("\n===== SALARY & EXPERIENCE MEAN =====")
print(
    df.groupby("Department")[["Salary", "Experience"]].mean()
)

# ==================================================
# 11. NAMED AGGREGATIONS
# ==================================================

print("\n===== NAMED AGGREGATIONS =====")
print(
    df.groupby("Department").agg(
        Average_Salary=("Salary", "mean"),
        Highest_Salary=("Salary", "max"),
        Avg_Experience=("Experience", "mean")
    )
)

# ==================================================
# 12. ITERATE THROUGH GROUPS
# ==================================================

print("\n===== ITERATING GROUPS =====")

for dept, group in df.groupby("Department"):
    print(f"\nDepartment: {dept}")
    print(group)

# ==================================================
# 13. GET SPECIFIC GROUP
# ==================================================

print("\n===== GET IT GROUP =====")

grouped = df.groupby("Department")
print(grouped.get_group("IT"))

# ==================================================
# 14. SIZE VS COUNT
# ==================================================

print("\n===== SIZE =====")
print(df.groupby("Department").size())

print("\n===== COUNT =====")
print(df.groupby("Department")["Salary"].count())

# ==================================================
# 15. TRANSFORM
# ==================================================

print("\n===== TRANSFORM =====")

df["Dept_Avg_Salary"] = (
    df.groupby("Department")["Salary"]
      .transform("mean")
)

print(df)

# ==================================================
# 16. FILTER
# ==================================================

print("\n===== FILTER GROUPS (AVG SALARY > 50000) =====")

filtered = df.groupby("Department").filter(
    lambda x: x["Salary"].mean() > 50000
)

print(filtered)

# ==================================================
# 17. APPLY
# ==================================================

print("\n===== APPLY CUSTOM FUNCTION =====")

def salary_range(group):
    return group["Salary"].max() - group["Salary"].min()

print(
    df.groupby("Department").apply(
        salary_range,
        include_groups=False
    )
)

