# Pandas GroupBy - Complete Guide

## What is GroupBy?

`groupby()` is one of the most powerful features in Pandas. It allows you to:

1. **Split** data into groups
2. **Apply** a function to each group
3. **Combine** the results

This process is often called the **Split-Apply-Combine** strategy.

---

## Import Pandas

```python
import pandas as pd
```

---

## Sample Dataset

```python
data = {
    "Department": ["IT", "HR", "IT", "Finance", "HR", "Finance"],
    "Employee": ["John", "Alice", "Bob", "David", "Emma", "Mike"],
    "Salary": [60000, 50000, 70000, 80000, 55000, 85000]
}

df = pd.DataFrame(data)
print(df)
```

Output:

| Department | Employee | Salary |
| ---------- | -------- | ------ |
| IT         | John     | 60000  |
| HR         | Alice    | 50000  |
| IT         | Bob      | 70000  |
| Finance    | David    | 80000  |
| HR         | Emma     | 55000  |
| Finance    | Mike     | 85000  |

---

# Basic GroupBy

Group rows by a column:

```python
grouped = df.groupby("Department")
print(grouped)
```

Output:

```python
<pandas.core.groupby.generic.DataFrameGroupBy object>
```

A GroupBy object is created but no calculation is performed yet.

---

# Sum Aggregation

Calculate total salary per department:

```python
df.groupby("Department")["Salary"].sum()
```

Output:

```text
Department
Finance    165000
HR         105000
IT         130000
```

---

# Mean Aggregation

Average salary per department:

```python
df.groupby("Department")["Salary"].mean()
```

Output:

```text
Department
Finance    82500
HR         52500
IT         65000
```

---

# Count Records

Count employees in each department:

```python
df.groupby("Department")["Employee"].count()
```

Output:

```text
Department
Finance    2
HR         2
IT         2
```

---

# Multiple Aggregations

Perform multiple calculations at once:

```python
df.groupby("Department")["Salary"].agg(
    ["sum", "mean", "max", "min"]
)
```

Output:

| Department | sum    | mean  | max   | min   |
| ---------- | ------ | ----- | ----- | ----- |
| Finance    | 165000 | 82500 | 85000 | 80000 |
| HR         | 105000 | 52500 | 55000 | 50000 |
| IT         | 130000 | 65000 | 70000 | 60000 |

---

# Group By Multiple Columns

Dataset:

```python
data = {
    "Department": ["IT", "IT", "HR", "HR"],
    "Gender": ["M", "F", "M", "F"],
    "Salary": [60000, 65000, 50000, 55000]
}

df = pd.DataFrame(data)
```

Group by two columns:

```python
df.groupby(["Department", "Gender"])["Salary"].mean()
```

Output:

```text
Department  Gender
HR          F         55000
            M         50000
IT          F         65000
            M         60000
```

---

# Using as_index=False

By default, grouped columns become the index.

```python
df.groupby("Department")["Salary"].sum()
```

To keep them as normal columns:

```python
df.groupby("Department", as_index=False)["Salary"].sum()
```

Output:

| Department | Salary |
| ---------- | ------ |
| Finance    | 165000 |
| HR         | 105000 |
| IT         | 130000 |

---

# Iterating Through Groups

```python
for dept, group in df.groupby("Department"):
    print("Department:", dept)
    print(group)
```

Output:

```text
Department: Finance
...

Department: HR
...

Department: IT
...
```

---

# Using transform()

`transform()` returns data with the same size as the original DataFrame.

Example:

```python
df["Dept_Avg"] = df.groupby("Department")["Salary"].transform("mean")
print(df)
```

Output:

| Department | Employee | Salary | Dept_Avg |
| ---------- | -------- | ------ | -------- |
| IT         | John     | 60000  | 65000    |
| IT         | Bob      | 70000  | 65000    |
| HR         | Alice    | 50000  | 52500    |
| HR         | Emma     | 55000  | 52500    |

---

# Using filter()

Keep only groups that satisfy a condition.

```python
df.groupby("Department").filter(
    lambda x: x["Salary"].mean() > 60000
)
```

Only departments with average salary greater than 60000 are returned.

---

# Using apply()

Apply a custom function to each group.

```python
def salary_range(group):
    return group["Salary"].max() - group["Salary"].min()

df.groupby("Department").apply(salary_range)
```

Output:

```text
Department
Finance    5000
HR         5000
IT        10000
```

---

# Real-World Example

Sales Data:

```python
sales = pd.DataFrame({
    "Product": ["Laptop", "Laptop", "Phone", "Phone", "Tablet"],
    "Region": ["East", "West", "East", "West", "East"],
    "Revenue": [1000, 1500, 800, 1200, 600]
})
```

Total revenue per product:

```python
sales.groupby("Product")["Revenue"].sum()
```

Output:

```text
Laptop    2500
Phone     2000
Tablet     600
```

Revenue by product and region:

```python
sales.groupby(["Product", "Region"])["Revenue"].sum()
```



# Summary

`groupby()` is used to:

* Aggregate data
* Calculate statistics by category
* Build reports
* Perform feature engineering
* Analyze grouped datasets

The most common pattern is:

```python
df.groupby("column")["target_column"].agg(
    ["sum", "mean", "max", "min"]
)
```

Mastering `groupby()` is essential for data analysis, data science, machine learning, and analytics workflows.
