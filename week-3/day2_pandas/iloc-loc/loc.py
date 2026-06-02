import pandas as pd
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [25, 30, 35, 40, 45],
    'Gender': ['Female', 'Male', 'Male', 'Male', 'Female']
}
df = pd.DataFrame(data)
print(df.loc[0]) # Access the first row using loc
print(df.loc[1:3]) # Access rows from index 1 to 3 using loc
print(df.loc[df['Age'] > 30]) # Access rows where Age is greater than 30 using loc
print(df.loc[df['Gender'] == 'Female']) # Access rows where Gender is female using loc
print("\n")

print(df.loc[0, 'Name']) # Access the Name of the first row using loc ; df.loc[row_index, column_name]
print(df.loc[[0,2]]) # Access multiple rows using loc with a list of indices

print("\n")
print(df.loc[:,['Name', 'Age']]) # Access multiple columns for all rows using loc