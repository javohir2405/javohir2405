"""Mavzu fayllarini tekshirish.  python3 -I validate_topic.py <ildiz papka> <NN> [matn|slides|both]"""
import json, re, sys, os, tempfile
SP, NN = sys.argv[1], int(sys.argv[2])
mode = sys.argv[3] if len(sys.argv) > 3 else 'both'
sys.path.insert(0, SP + '/scripts')
errs, info = [], []

CYR = re.compile('[Ѐ-ӿ]')
MD = re.compile(r'(\*\*|^#{1,6} |`{3}|__)', re.M)


def words(s): return len(re.findall(r"[\w‘’'`ʻ-]+", s, re.U))


def check_text(where, s):
    if CYR.search(s): errs.append('%s: kirill harf bor: %r' % (where, CYR.findall(s)[:5]))
    if MD.search(s): errs.append('%s: markdown belgisi bor' % where)


def matn():
    p = '%s/content/t%02d_matn.json' % (SP, NN)
    try: d = json.load(open(p, encoding='utf-8'))
    except Exception as ex: errs.append('matn json o\'qilmadi: %r' % ex); return
    for k in ('num', 'title', 'shakl', 'reja', 'sections'):
        if k not in d: errs.append('matn: "%s" maydoni yo\'q' % k)
    if errs: return
    if d['num'] != NN: errs.append('matn: num=%s != %s' % (d['num'], NN))
    if d['shakl'] not in ('Nazariy', 'Amaliy'): errs.append('matn: shakl noto\'g\'ri')
    if not (isinstance(d['reja'], list) and len(d['reja']) == 4): errs.append('matn: reja aynan 4 ta bo\'lishi kerak'); return
    if len(d['sections']) != 4: errs.append('matn: sections aynan 4 ta bo\'lishi kerak'); return
    total = 0
    for i, sec in enumerate(d['sections']):
        if sec.get('heading', '').strip() != d['reja'][i].strip(): errs.append('matn: section %d heading reja[%d] ga teng emas' % (i + 1, i))
        sw = 0
        if not sec.get('blocks'): errs.append('matn: section %d bo\'sh' % (i + 1))
        for b in sec.get('blocks', []):
            k = b.get('kind')
            if k == 'p': check_text('section %d p' % (i + 1), b['text']); sw += words(b['text'])
            elif k == 'list':
                for it in b['items']: check_text('section %d list' % (i + 1), it); sw += words(it)
            elif k == 'code':
                if not b.get('lines'): errs.append('matn: code bloki bo\'sh')
                if len(b['lines']) > 40: errs.append('matn: code bloki 40 qatordan uzun')
            else: errs.append('matn: noma\'lum blok turi %r' % k)
        info.append('section %d: %d so\'z' % (i + 1, sw))
        if sw < 200: errs.append('matn: section %d juda qisqa (%d so\'z, kamida 200)' % (i + 1, sw))
        total += sw
    check_text('title', d['title'])
    for r in d['reja']: check_text('reja', r)
    info.append('JAMI matn: %d so\'z' % total)
    if total < 1100: errs.append('matn: jami %d so\'z, kamida 1100 kerak' % total)


def slides():
    p = '%s/content/t%02d_slides.json' % (SP, NN)
    try: d = json.load(open(p, encoding='utf-8'))
    except Exception as ex: errs.append('slides json o\'qilmadi: %r' % ex); return
    from figrender import render, SpecError
    sl = d.get('slides')
    if not (isinstance(sl, list) and len(sl) == 5): errs.append('slides: aynan 5 ta slayd kerak'); return
    tmp = tempfile.mkdtemp()
    for i, s in enumerate(sl, 1):
        if not (3 <= len(s.get('bullets', [])) <= 5): errs.append('slayd %d: bullets 3..5 ta bo\'lishi kerak' % i)
        for b in s.get('bullets', []):
            check_text('slayd %d' % i, b)
            if not (3 <= words(b) <= 24): errs.append('slayd %d: bullet 3..24 so\'z bo\'lishi kerak: %r' % (i, b[:40]))
        if not s.get('title') or len(s['title']) > 80: errs.append('slayd %d: title yo\'q yoki 80 belgidan uzun' % i)
        check_text('slayd %d title' % i, s.get('title', ''))
        if not s.get('caption'): errs.append('slayd %d: caption yo\'q' % i)
        try: render(s['figure'], '%s/s%d.png' % (tmp, i))
        except SpecError as ex: errs.append('slayd %d rasm: %s' % (i, ex))
        except Exception as ex: errs.append('slayd %d rasm xato: %r' % (i, ex))
    ish = d.get('ishchi') or {}
    for k in ('natija', 'baholash', 'bilim', 'konikma'):
        if not ish.get(k): errs.append('ishchi: "%s" yo\'q' % k)
        else: check_text('ishchi ' + k, ish[k])
    info.append('slaydlar: 5 ta, rasmlar chizildi' if not errs else 'slaydlar tekshirildi')


if mode in ('matn', 'both'): matn()
if mode in ('slides', 'both'): slides()
for i in info: print('  ', i)
if errs:
    print('XATOLAR (%d):' % len(errs))
    for e in errs: print(' -', e)
    sys.exit(1)
print('OK')
