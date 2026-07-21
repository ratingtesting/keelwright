# Ad-hoc Verification Script for SQL Injection Fixes

```python
import sqlite3
import os
import tempfile

def search_users_by_name(db_path: str, name: str):
    """Parameterized query implementation to verify."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM users WHERE name = ?", (name,))
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

def init_test_db(db_path: str):
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    """)
    test_users = [
        ("Alice", "alice@example.com"),
        ("Bob", "bob@example.com"),
        ("Charlie", "charlie@example.com"),
        ("O'Reilly", "oreilly@example.com"),
        ("Test; DROP TABLE users", "hack@example.com"),
        ("\u0418\u0432\u0430\u043d", "ivan@example.com"),  # Иван
        ("Jos\u00e9", "jose@example.com"),  # José
        ("Smith", "smith@example.com"),
    ]
    cursor.executemany("INSERT INTO users (name, email) VALUES (?, ?)", test_users)
    conn.commit()
    conn.close()

# Run verification
with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
    db_path = f.name

try:
    init_test_db(db_path)

    test_cases = [
        ("Alice", 1),
        ("O'Reilly", 1),
        ("Test; DROP TABLE users", 1),
        ("\u0418\u0432\u0430\u043d", 1),
        ("Jos\u00e9", 1),
        ("NonExistent", 0),
    ]

    all_passed = True
    for name, expected_count in test_cases:
        results = search_users_by_name(db_path, name)
        passed = len(results) == expected_count
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: search(\"{name}\") -> {len(results)} results (expected {expected_count})")
        if not passed:
            all_passed = False

    # Verify DB integrity
    conn = sqlite3.connect(db_path)
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    integrity_pass = count == 8
    print(f"  {'PASS' if integrity_pass else 'FAIL'}: DB integrity - {count} users (expected 8)")
    all_passed = all_passed and integrity_pass

    print(f"\n  OVERALL: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

finally:
    if os.path.exists(db_path):
        os.remove(db_path)
```

**Usage:** Run with `python hermes-verify-sqlfix.py` after fixing a SQL injection vulnerability. Modify `search_users_by_name` function to test your fixed implementation.