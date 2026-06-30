import os
import re
import sys
import subprocess

def check_for_stubs():
    patterns = ["pass", "TODO", "FIXME", "placeholder", "stub", "Mock", "Dummy"]
    errors = []
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith((".py", ".mqh", ".mq5")):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        for p in patterns:
                            if p in line and all(x not in line for x in ["Magic:", "password", "password_hash", "CredentialManager"]):
                                # Exclude docstrings if they are explanations
                                if '"""' not in line and "'''" not in line:
                                    errors.append(f"{path}:{i} - Found forbidden pattern: {p}")
    return errors

def check_magic_numbers():
    found = {}
    errors = []
    # Simplified regex for Magic: XXXXX
    pattern = re.compile(r"Magic: (\d+)")
    for root, dirs, files in os.walk("src/python"):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    content = f.read()
                    matches = pattern.findall(content)
                    for m in matches:
                        if m in found:
                            errors.append(f"DUPLICATE MAGIC: {m} in {path} and {found[m]}")
                        found[m] = path
    return errors

if __name__ == "__main__":
    print("--- INSTITUTIONAL REVIEWER START ---")
    stubs = check_for_stubs()
    if stubs:
        print("\n[!] STUB CHECK FAILED:")
        for s in stubs: print(s)
    else:
        print("\n[OK] Zero stubs/placeholders detected.")

    magics = check_magic_numbers()
    if magics:
        print("\n[!] MAGIC NUMBER CHECK FAILED:")
        for m in magics: print(m)
    else:
        print("\n[OK] All magic numbers are unique.")

    if stubs or magics:
        sys.exit(1)
    print("\n--- SYSTEM BATTLE-READY ---")
