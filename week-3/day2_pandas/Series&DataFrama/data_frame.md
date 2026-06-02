# Pandas DataFrame

## Introduction

A Pandas DataFrame is a two-dimensional labeled data structure. It is similar to a spreadsheet or database table containing rows and columns.

## Structure of a DataFrame

### Rows

Rows represent individual records.

### Columns

Columns represent attributes or features of the data.

### Index

Each row has an index label that uniquely identifies it.

## Creating a DataFrame

A DataFrame can be created from:

* Dictionaries
* Lists of dictionaries
* CSV files
* Excel files
* NumPy arrays

When a dictionary is used:

* Dictionary keys become column names.
* Dictionary values become column data.

## Accessing Data

### Accessing Rows by Label (`loc`)

* Uses row index labels.
* Useful when rows have meaningful names.

### Accessing Rows by Position (`iloc`)

* Uses numerical positions.
* Position counting starts from 0.

## Filtering Data

Rows can be filtered using conditions.
Only rows satisfying the condition are returned.

Examples:

* Employees with a specific age.
* Records above a threshold value.
* Matching categories.

## Adding Columns

New columns can be added to store additional information.

Benefits:

* Enhances dataset structure.
* Allows storage of derived information.
* Supports feature engineering.

## Adding Rows

New records can be appended to an existing DataFrame.

A new row should contain values corresponding to the existing columns.

## Adding Multiple Rows

Multiple records can be added together to expand the dataset.

This is useful when:

* Importing new data.
* Combining datasets.
* Updating records in batches.

## Common DataFrame Operations

* Selecting rows and columns.
* Filtering records.
* Updating values.
* Adding or removing columns.
* Adding or removing rows.
* Sorting data.
* Aggregating data.

## Advantages of DataFrames

* Handles structured data efficiently.
* Supports powerful filtering and analysis.
* Easy integration with CSV and Excel files.
* Widely used in data science and machine learning.

## Real-World Uses

* Employee management systems.
* Sales reports.
* Customer databases.
* Machine learning datasets.
* Financial analysis.

## Series vs DataFrame

| Feature    | Series                   | DataFrame        |
| ---------- | ------------------------ | ---------------- |
| Dimensions | 1D                       | 2D               |
| Structure  | Single column            | Rows and columns |
| Labels     | Index only               | Rows and columns |
| Usage      | Individual data sequence | Complete dataset |

## Summary

A Pandas DataFrame is a tabular data structure consisting of rows and columns. It provides powerful tools for storing, accessing, filtering, updating, and analyzing structured data.
