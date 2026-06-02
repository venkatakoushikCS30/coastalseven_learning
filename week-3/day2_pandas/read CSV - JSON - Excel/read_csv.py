import pandas as pd

df = pd.read_csv("data.csv") #read csv file and create data frame
print(df.to_string()) #print entire data frame without truncation
print(df.head()) #print first 5 rows of data frame
print(df.tail()) #print last 5 rows of data frame

df = pd.read_json('data.json') #read json file and create data frame
print(df)

df = pd.read_excel('data.xls') #read excel file and create data frame - needs openpyxl library to read xlsx files and xlrd library to read xls files
print(df)