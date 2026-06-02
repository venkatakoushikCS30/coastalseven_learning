import pandas as pd

#Data Frame - two dimensional array with labels like a spreadsheet

data = {"name":['koushik','karthikeya','jabir'],
        "age":[23,24,22]}

df = pd.DataFrame(data , index=['Employee1','Employee2','Employee3'])
print(df)
print(df.loc['Employee1']) #accessing row by label
print(df.iloc[1]) #accessing row by position
print(df[df['age'] == 23])

df["Job"] = ['Data Scientist','Software Engineer','Data Analyst'] #adding new column to data frame
print(df)

new_row = pd.DataFrame([{"name":"Sai" , "age":25 , "Job":"Data Engineer"}], index=['Employee4']) #creating new row as a data frame
df = pd.concat([df , new_row]) #adding new row to data frame
print(df)

new_rows = pd.DataFrame([{"name":"tharun" , "age":26 , "Job":"Data Architect"},
                         {"name":"surya" , "age":27 , "Job":"Data Manager"}], index=['Employee5','Employee6']) #creating multiple new rows as a data frame
df = pd.concat([df , new_rows]) #adding multiple new rows to data frame
print(df)