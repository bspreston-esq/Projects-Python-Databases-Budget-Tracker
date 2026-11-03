# Budget Tracker

**Category:** Databases

## Problem

Write an application that keeps track of a household's budget. The user can add expenses, income, and recurring costs to find out how much they are saving or losing over a period of time. Optional: Allow the user to specify a date range and see the net flow of money in and out of the house budget for that time period.

## Solution

SQLite stores one-off transactions and recurring monthly items (day 1-28 so every month has it). A range summary merges both, totals income and expenses, computes net flow, and ranks expense categories. Invalid kinds, negative amounts and malformed dates are rejected.

## How to run

Requires Python 3.8+ and no third-party packages.

```bash
python3 main.py --db budget.db --add 2026-11-02 expense groceries 142.30 --description "weekly shop"
python3 main.py --db budget.db --recurring expense housing rent 1800 1
python3 main.py --db budget.db --from 2026-11-01 --to 2026-12-31
python3 main.py --demo
```

## Example

```text
income $5,200.00 | expenses $3,938.48 | net $1,261.52
top categories: housing $3,600.00, groceries $142.30, utilities $96.20, dining $68.00
entries considered: 8
```

## Attribution

The problem statement is from [karan/Projects](https://github.com/karan/Projects), a list of practical projects that anyone can solve in any programming language (MIT License, Copyright (c) 2013 Karan Goel). The Python solution in this repository was implemented by [bspreston-esq](https://github.com/bspreston-esq).

This repository is part of the [Projects-Python-All](https://github.com/bspreston-esq/Projects-Python-All) collection.
