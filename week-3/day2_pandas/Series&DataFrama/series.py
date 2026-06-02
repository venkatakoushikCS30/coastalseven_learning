import pandas as pd

#series - one dimensional array with labels like a single column of a spreadsheet

data = [100, 102,104]
series = pd.Series(data,index=['a','b','c'])
print(series)
print(series.loc['c']) #loc - access by label (index)
series.loc['a'] = 101 #update value of existing element
series.loc['d'] = 106 #add new element to series
print(series)

series.iloc[0] = 1 #iloc - access by position (integer location)
print(series)
print(series.iloc[0])

print(series[series>=102]) #boolean indexing - filter series based on condition

calories = {"Day1":1750 , "Day2":2100 , "Day3":1700}

series = pd.Series(calories)
print(series)
print(series.loc['Day2']) #accessing value by label
series.loc['Day3'] += 200
print(series[series < 2000])