# Pandas iloc

## Introduction

`iloc` is a position-based indexing method used to access data in a Pandas DataFrame or Series.

## Features

* Access data using row and column positions.
* Position counting starts from 0.
* Supports single values, rows, columns, and slices.
* Supports negative indexing.
* Supports row and column selection together.

## Accessing Data

### Rows

Select rows using their position numbers.

### Columns

Select columns using their position numbers.

### Cells

Access a specific value using row and column positions.

### Multiple Rows and Columns

Select multiple rows or columns using:

* Lists of positions
* Position ranges (slicing)

## Slicing

A range of positions can be selected using slicing.

Unlike `loc`, the ending position is **not included**.

Example:

* `0:2` returns positions 0 and 1.

## Negative Indexing

Negative positions count from the end:

* `-1` → Last row or column
* `-2` → Second last row or column

## Advanced Selection

`iloc` supports:

* Selecting alternate rows
* Reversing rows
* Selecting subsets of rows and columns
* Returning a column as a DataFrame

## loc vs iloc

| Feature            | loc          | iloc           |
| ------------------ | ------------ | -------------- |
| Uses               | Labels       | Positions      |
| Rows               | Index labels | Row numbers    |
| Columns            | Column names | Column numbers |
| Range End Included | Yes          | No             |

## Advantages

* Fast and simple.
* Useful when positions are known.
* Ideal for slicing and indexing operations.
* Works even when labels are unavailable.

## Summary

`iloc` is a position-based indexing method used to access rows, columns, and individual values using integer positions in a Pandas DataFrame.
