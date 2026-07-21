import os
import sys

TREATMENT_DIR = r'C:\Users\Unicorn\vibe-qa\20260719T210443Z\T3\treatment'
sys.path.insert(0, TREATMENT_DIR)

import user_service as us
from user_service import create_user, get_user, delete_user

results = []

us._users.clear()

# happy path
u = create_user("verify-u1", "VerifyUser")
assert u == {"user_id": "verify-u1", "name": "VerifyUser", "role": "user"}, "happy path mismatch"
assert get_user("verify-u1") == u, "get mismatch"
results.append("happy_path: PASS")

# duplicate create
try:
    create_user("verify-u1", "Again")
except ValueError:
    us._users.clear()
    results.append("duplicate_create: PASS")
else:
    results.append("duplicate_create: FAIL")
    us._users.clear()

# delete then post-check
create_user("verify-u2", "ToDelete")
delete_user("verify-u2")
try:
    get_user("verify-u2")
except KeyError:
    results.append("delete_postcheck: PASS")
else:
    results.append("delete_postcheck: FAIL")

# unknown get
try:
    get_user("verify-unknown")
except KeyError:
    results.append("unknown_get: PASS")
else:
    results.append("unknown_get: FAIL")

# unknown delete
try:
    delete_user("verify-unknown")
except KeyError:
    results.append("unknown_delete: PASS")
else:
    results.append("unknown_delete: FAIL")

print("ADHOC_RESULTS:")
for r in results:
    print(r)

if all("PASS" in r for r in results):
    print("ADHOC_OVERALL: PASS")
    sys.exit(0)
else:
    print("ADHOC_OVERALL: FAIL")
    sys.exit(1)
