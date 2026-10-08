import glob, os, re
from parse import parse, words

HERE = os.path.dirname(os.path.abspath(__file__))
FAN = "Ma’lumotlar tuzilmasi va algoritmlar"
YONALISH = "50320203 – Kutubxonashunoslik va bibliografiya"

def clean_title(t):
    return re.sub(r"\s*\(amaliy mashg.ulot\)\s*$", "", t).strip()

def load():
    topics = []
    for i, f in enumerate(sorted(glob.glob(os.path.join(HERE, "topics", "*.md"))), 1):
        d = parse(f)
        d["no"] = i
        d["title"] = clean_title(d["title"])
        d["words"] = words(d)
        topics.append(d)
    return topics

def sentences(text):
    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZO‘G‘«\"])", text)
    return [p.strip() for p in parts if p.strip()]

def bullet_from(par, maxlen=150):
    ss = sentences(par)
    cand = ss[:2]
    for c in cand:
        if 45 <= len(c) <= maxlen:
            return c
    ok = [c for c in cand if len(c) <= maxlen]
    if ok:
        return max(ok, key=len)
    s = ss[0]
    cut = max(s.rfind(", ", 0, maxlen), s.rfind(" va ", 0, maxlen))
    return (s[:cut] if cut > 50 else s[:maxlen].rsplit(" ", 1)[0]) + "…"

def plan_slides(topic):
    """Returns list of slide dicts. 10 slides total."""
    slides = []
    slides.append({"kind": "title"})
    slides.append({"kind": "plan"})
    for pi, (h, blocks) in enumerate(topic["plans"]):
        pars = [x for t, x in blocks if t == "p"]
        codes = [x for t, x in blocks if t == "code"]
        # birinchi paragraf odatda umumiy kirish; ikkinchi slaydga keyingilari
        bl = [bullet_from(p) for p in pars]
        good = [b for b in bl if len(b) >= 45 and not b.endswith("tushuntiramiz.") and not b.endswith("qilamiz.")]
        bl = good if len(good) >= 6 else bl
        n = len(bl)
        if pi < 3:
            half = max(3, min(5, n // 2))
            a = bl[:half][:5]
            if codes:
                slides.append({"kind": "bullets", "title": f"{pi+1}. {h}", "bullets": a})
                slides.append({"kind": "code", "title": f"{pi+1}. {h} — namuna", "code": codes[0]})
            else:
                b = bl[half:][:5]
                slides.append({"kind": "bullets", "title": f"{pi+1}. {h}", "bullets": a})
                slides.append({"kind": "bullets", "title": f"{pi+1}. {h} (davomi)", "bullets": b})
        else:
            b = (bl[:2] + bl[-3:])[:5]
            slides.append({"kind": "bullets", "title": f"{pi+1}. {h}", "bullets": b})
    slides.append({"kind": "questions"})
    assert len(slides) == 10, len(slides)
    return slides

def slide_titles(topic):
    out = []
    for s in plan_slides(topic):
        k = s["kind"]
        if k == "title": out.append(topic["title"])
        elif k == "plan": out.append("Mavzu rejasi")
        elif k == "questions": out.append("Xulosa va nazorat savollari")
        else: out.append(s["title"])
    return out
