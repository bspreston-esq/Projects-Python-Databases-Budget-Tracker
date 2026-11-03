#!/usr/bin/env python3
"""Household budget: income, expenses and recurring costs with date ranges."""
import argparse
import calendar
import datetime as dt
import os
import sqlite3
import tempfile

SCHEMA = """
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('income','expense')),
    category TEXT NOT NULL,
    description TEXT DEFAULT '',
    amount REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS recurring (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kind TEXT NOT NULL CHECK (kind IN ('income','expense')),
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    day_of_month INTEGER NOT NULL
);"""

def connect(path):
    connection = sqlite3.connect(path)
    connection.executescript(SCHEMA)
    connection.commit()
    return connection

def add(connection, date, kind, category, amount, description=""):
    if kind not in ("income", "expense") or amount <= 0:
        raise ValueError("kind must be income/expense and amount must be positive")
    dt.date.fromisoformat(date)
    connection.execute("INSERT INTO transactions (date,kind,category,description,amount) VALUES (?,?,?,?,?)",
                       (date, kind, category, description, amount))
    connection.commit()

def add_recurring(connection, kind, category, description, amount, day):
    if not 1 <= day <= 28:
        raise ValueError("day_of_month must be 1-28 to exist in every month")
    connection.execute("INSERT INTO recurring (kind,category,description,amount,day_of_month) VALUES (?,?,?,?,?)",
                       (kind, category, description, amount, day))
    connection.commit()

def recurring_in_range(connection, start: dt.date, end: dt.date):
    """Expand recurring entries into concrete monthly items inside the range."""
    items = []
    for kind, category, description, amount, day in connection.execute(
            "SELECT kind,category,description,amount,day_of_month FROM recurring"):
        year, month = start.year, start.month
        while (year, month) <= (end.year, end.month):
            date = dt.date(year, month, day)
            if start <= date <= end:
                items.append((date, kind, category, description, amount))
            month += 1
            if month == 13:
                month, year = 1, year + 1
    return items

def summary(connection, start: dt.date, end: dt.date):
    rows = [(dt.date.fromisoformat(date), kind, category, description, amount)
            for date, kind, category, description, amount in connection.execute(
                "SELECT date,kind,category,description,amount FROM transactions WHERE date BETWEEN ? AND ?",
                (start.isoformat(), end.isoformat()))]
    rows += recurring_in_range(connection, start, end)
    income = sum(amount for _, kind, _, _, amount in rows if kind == "income")
    expenses = sum(amount for _, kind, _, _, amount in rows if kind == "expense")
    by_category = {}
    for _, kind, category, _, amount in rows:
        if kind == "expense":
            by_category[category] = by_category.get(category, 0) + amount
    return {"income": income, "expenses": expenses, "net": income - expenses,
            "by_category": dict(sorted(by_category.items(), key=lambda kv: -kv[1])), "count": len(rows)}

def demo() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        connection = connect(os.path.join(tmp, "budget.db"))
        add(connection, "2026-11-01", "income", "salary", 5200, "November salary")
        add(connection, "2026-11-02", "expense", "groceries", 142.30, "weekly shop")
        add(connection, "2026-11-04", "expense", "utilities", 96.20, "electricity")
        add(connection, "2026-11-10", "expense", "dining", 68.00, "dinner out")
        add_recurring(connection, "expense", "housing", "rent", 1800, 1)
        add_recurring(connection, "expense", "subscriptions", "streaming", 15.99, 15)
        result = summary(connection, dt.date(2026, 11, 1), dt.date(2026, 12, 31))
        print(f"income ${result['income']:,.2f} | expenses ${result['expenses']:,.2f} | net ${result['net']:,.2f}")
        print("top categories:", ", ".join(f"{name} ${amount:,.2f}" for name, amount in list(result["by_category"].items())[:4]))
        print("entries considered:", result["count"])
        connection.close()

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="budget.db")
    parser.add_argument("--add", nargs=4, metavar=("DATE", "KIND", "CATEGORY", "AMOUNT"))
    parser.add_argument("--description", default="")
    parser.add_argument("--recurring", nargs=5, metavar=("KIND", "CATEGORY", "DESCRIPTION", "AMOUNT", "DAY"))
    parser.add_argument("--from", dest="start")
    parser.add_argument("--to", dest="end")
    parser.add_argument("--demo", action="store_true")
    args = parser.parse_args()
    if args.demo:
        demo(); return
    connection = connect(args.db)
    try:
        if args.add:
            add(connection, args.add[0], args.add[1], args.add[2], float(args.add[3]), args.description)
            print("transaction added")
        if args.recurring:
            kind, category, description, amount, day = args.recurring
            add_recurring(connection, kind, category, description, float(amount), int(day))
            print("recurring item added")
        if args.start and args.end:
            result = summary(connection, dt.date.fromisoformat(args.start), dt.date.fromisoformat(args.end))
            print(f"income ${result['income']:,.2f} | expenses ${result['expenses']:,.2f} | net ${result['net']:,.2f}")
            for category, amount in result["by_category"].items():
                print(f"  {category:<14} ${amount:,.2f}")
    finally:
        connection.close()

if __name__ == "__main__":
    main()
