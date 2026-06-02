# Pandas Series

## Introduction

A Pandas Series is a one-dimensional labeled data structure. It can store data of a single type or mixed types and is similar to a single column in a spreadsheet.

## Key Components

* **Values**: The actual data stored in the Series.
* **Index**: Labels used to identify each value.
* **Data Type**: Defines the type of values stored.

## Creating a Series

A Series can be created from:

* Lists
* Tuples
* Dictionaries
* NumPy arrays

When labels are provided, they become the index of the Series.

## Accessing Data

### Label-Based Access (`loc`)

* Uses index labels.
* Useful when meaningful labels are assigned.

### Position-Based Access (`iloc`)

* Uses integer positions.
* Indexing starts from 0.

## Updating Data

Existing values can be modified by specifying their label or position.

## Adding New Elements

A new element can be added by assigning a value to a new index label.

## Boolean Indexing

Boolean indexing filters data based on conditions.
It returns only the elements that satisfy the specified condition.

Examples:

* Values greater than a threshold.
* Values less than a threshold.
* Values equal to a specific value.

## Creating a Series from a Dictionary

When a dictionary is used:

* Keys become index labels.
* Values become Series values.

## Advantages of Series

* Easy data storage and manipulation.
* Fast filtering and selection.
* Supports arithmetic operations.
* Integrates well with DataFrames.

## Real-World Uses

* Daily sales records.
* Student marks.
* Temperature readings.
* Calorie tracking data.

## Summary

A Pandas Series is a labeled one-dimensional structure that supports efficient data access, updates, filtering, and analysis.
