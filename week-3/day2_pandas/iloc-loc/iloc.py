import pandas as pd

# Create DataFrame
data = {
    "Name": ["Koushik", "Rahul", "Anu", "Priya"],
    "Age": [21, 22, 20, 23],
    "City": ["Vijayawada", "Hyderabad", "Chennai", "Bangalore"]
}

df = pd.DataFrame(data)

print("Original DataFrame:")
print(df)

# 1. First row
print("\n1. First Row")
print(df.iloc[0])

# 2. Second row
print("\n2. Second Row")
print(df.iloc[1])

# 3. Specific value
print("\n3. Value at row 2, column 0")
print(df.iloc[2, 0])

# 4. Age of Priya
print("\n4. Age of Priya")
print(df.iloc[3, 1])

# 5. Multiple rows
print("\n5. Rows 0 and 2")
print(df.iloc[[0, 2]])

# 6. First two rows
print("\n6. First Two Rows")
print(df.iloc[0:2])

# 7. First two columns
print("\n7. First Two Columns")
print(df.iloc[:, 0:2])

# 8. Only Names column
print("\n8. Names Column")
print(df.iloc[:, 0])

# 9. Last row
print("\n9. Last Row")
print(df.iloc[-1])

# 10. Last column
print("\n10. Last Column")
print(df.iloc[:, -1])

# 11. Rows 1 to 3 and columns 0 to 1
print("\n11. Rows 1 to 3 and Columns 0 to 1")
print(df.iloc[1:4, 0:2])

# 12. Reverse rows
print("\n12. Reverse Rows")
print(df.iloc[::-1])

# 13. Skip rows
print("\n13. Alternate Rows")
print(df.iloc[::2])

# 14. Single column as DataFrame
print("\n14. Name Column as DataFrame")
print(df.iloc[:, [0]])