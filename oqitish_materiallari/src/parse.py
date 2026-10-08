import re, glob, os

def fix_quotes(s):
    s = re.sub(r"(?<=[oOgG])'", "‘", s)
    return s.replace("'", "’")

def parse(path):
    """Returns dict: title, tur, plans[(heading, [blocks])], questions[]
    block = ('p', text) | ('li', text) | ('code', text)"""
    lines = open(path, encoding="utf-8").read().split("\n")
    d = {"title": "", "tur": "N", "plans": [], "questions": []}
    cur = None; para = []; code = None; mode = None
    def flush():
        nonlocal para
        if para and cur is not None:
            cur.append(("p", fix_quotes(" ".join(para))))
        para = []
    for ln in lines:
        if code is not None:
            if ln.startswith("```"):
                cur.append(("code", "\n".join(code))); code = None
            else:
                code.append(ln)
            continue
        if ln.startswith("```"):
            flush(); code = []; continue
        if ln.startswith("# "):
            d["title"] = fix_quotes(ln[2:].strip()); continue
        if ln.startswith("@tur:"):
            d["tur"] = ln.split(":")[1].strip(); continue
        if ln.startswith("## "):
            flush()
            h = fix_quotes(ln[3:].strip())
            if h.startswith("Nazorat"):
                cur = d["questions"]; mode = "q"
            else:
                cur = []; d["plans"].append([re.sub(r"^\d+\.\s*", "", h), cur]); mode = "p"
            continue
        if ln.startswith("- "):
            flush(); cur.append(("li", fix_quotes(ln[2:].strip()))); continue
        if not ln.strip():
            flush(); continue
        para.append(ln.strip())
    flush()
    return d

def words(d):
    n = 0
    for _, blocks in d["plans"]:
        for t, x in blocks:
            if t != "code":
                n += len(x.split())
    return n

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for f in sorted(glob.glob(os.path.join(here, "topics", "*.md"))):
        d = parse(f)
        print(os.path.basename(f), d["tur"], len(d["plans"]), "reja,", words(d), "so'z |", d["title"][:60])
