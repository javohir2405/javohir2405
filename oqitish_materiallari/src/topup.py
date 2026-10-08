import sys, re
def apply(num, parts):
    """parts: dict plan_number(1..4 or 'Q') -> text; inserted at end of that plan section."""
    p = f"topics/{num}.md"
    s = open(p, encoding="utf-8").read()
    for key, text in parts.items():
        if key == "Q":
            marker = "## Nazorat"
        else:
            marker = f"## {key+1}. " if key < 4 else "## Nazorat"
        i = s.index(marker)
        s = s[:i] + text.strip() + "\n\n" + s[i:]
    open(p, "w", encoding="utf-8").write(s)
