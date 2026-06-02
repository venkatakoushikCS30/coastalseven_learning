# Pandas loc

## Introduction

`loc` is a label-based indexing method used to access and filter data in a Pandas DataFrame or Series.

## Features

* Access rows by index label.
* Access columns by column name.
* Access specific cells.
* Select multiple rows and columns.
* Filter data using conditions.

## Accessing Data

### Rows

Select one or more rows using row labels.

### Columns

Select one or more columns using column names.

### Cells

Access a specific value using both row and column labels.

### Conditional Filtering

Retrieve rows that satisfy a condition, such as:

* Age greater than 30
* Gender equals Female

## Row and Column Selection

`loc` can select:

* Single row
* Multiple rows
* Single column
* Multiple columns
* Rows and columns together

## loc vs iloc

| Feature            | loc          | iloc           |
| ------------------ | ------------ | -------------- |
| Uses               | Labels       | Positions      |
| Rows               | Index labels | Row numbers    |
| Columns            | Column names | Column numbers |
| Range End Included | Yes          | No             |

## Advantages

* Easy to read.
* Works with meaningful labels.
* Supports powerful filtering.
* Useful for data analysis.

## Summary

`loc` is a label-based selection method used to access, filter, and retrieve specific rows, columns, or values from a Pandas DataFrame.
