"""Slayd rasmlarini (sxema, oyna maketi, grafik, kod, jadval) chizish. matplotlib (Agg)."""
import math, re, textwrap
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Ellipse, Polygon, Wedge, Arc
import numpy as np

BLUE = '#1F4E79'; LBLUE = '#DCE9F5'; MBLUE = '#9DC3E6'; ORANGE = '#ED7D31'; GREEN = '#70AD47'
GRAY = '#F2F2F2'; DGRAY = '#595959'; WHITE = '#FFFFFF'; RED = '#C00000'
plt.rcParams['font.family'] = 'DejaVu Sans'
W, H = 10.0, 7.0   # dyuym; dpi=100 -> 1000x700

FIG_TYPES = ('flow', 'window', 'plot', 'table', 'code', 'shapes', 'stack')


class SpecError(ValueError):
    pass


def _new(title):
    fig = plt.figure(figsize=(W, H), dpi=100, facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 70); ax.axis('off')
    if title:
        ax.add_patch(Rectangle((0, 63), 100, 7, color=BLUE))
        ax.text(2.5, 66.5, title, color='white', fontsize=17, fontweight='bold', va='center', ha='left')
    return fig, ax


def _wrap(s, width):
    return '\n'.join(textwrap.wrap(str(s), width=width, break_long_words=False)) or str(s)


def _fit_fs(text, w_units, h_units, base=14, minfs=8):
    for fs in range(base, minfs - 1, -1):
        cw = fs * 0.105
        per_line = max(4, int(w_units / cw))
        lines = textwrap.wrap(str(text), width=per_line) or ['']
        lh = fs * 0.19
        if len(lines) * lh <= h_units and max(len(l) for l in lines) <= per_line:
            return fs, '\n'.join(lines)
    fs = minfs; per_line = max(4, int(w_units / (fs * 0.105)))
    return fs, '\n'.join(textwrap.wrap(str(text), width=per_line))


# ---------------------------------------------------------------- flow
def _layers(nodes, edges):
    ids = [n['id'] for n in nodes]
    adj = {i: [] for i in ids}
    for e in edges:
        if e['from'] in adj and e['to'] in adj: adj[e['from']].append(e['to'])
    state = {}; back = set()
    def dfs(u):
        state[u] = 1
        for v in adj[u]:
            if state.get(v) == 1: back.add((u, v))
            elif v not in state: dfs(v)
        state[u] = 2
    indeg = {i: 0 for i in ids}
    for e in edges:
        if e['to'] in indeg: indeg[e['to']] += 1
    for i in ids:
        if indeg[i] == 0 and i not in state: dfs(i)
    for i in ids:
        if i not in state: dfs(i)
    layer = {i: 0 for i in ids}
    for _ in range(len(ids)):
        ch = False
        for u in ids:
            for v in adj[u]:
                if (u, v) in back: continue
                if layer[v] < layer[u] + 1: layer[v] = layer[u] + 1; ch = True
        if not ch: break
    groups = {}
    for i in ids: groups.setdefault(layer[i], []).append(i)
    return [groups[k] for k in sorted(groups)]


def _flow(spec):
    nodes = spec.get('nodes') or []
    edges = spec.get('edges') or []
    if not (2 <= len(nodes) <= 9): raise SpecError('flow: nodes soni 2..9 bo\'lishi kerak')
    idset = {n['id'] for n in nodes}
    if len(idset) != len(nodes): raise SpecError('flow: node id lar takrorlangan')
    for e in edges:
        if e['from'] not in idset or e['to'] not in idset: raise SpecError('flow: noma\'lum node: %s' % e)
    direction = spec.get('direction', 'LR')
    fig, ax = _new(spec.get('title'))
    layers = _layers(nodes, edges)
    byid = {n['id']: n for n in nodes}
    top, bottom, left, right = 60, 5, 3, 97
    pos = {}
    nl = len(layers)
    if direction == 'LR':
        colw = (right - left) / nl
        bw = min(26, colw * 0.72)
        maxk = max(len(l) for l in layers)
        rowh = (top - bottom) / maxk
        bh = min(13, rowh * 0.7)
        for li, l in enumerate(layers):
            cx = left + colw * (li + 0.5)
            for k, i in enumerate(l):
                cy = bottom + (top - bottom) / 2 + ((len(l) - 1) / 2 - k) * rowh
                pos[i] = (cx, cy)
    else:
        rowh = (top - bottom) / nl
        bh = min(11, rowh * 0.68)
        maxk = max(len(l) for l in layers)
        colw = (right - left) / maxk
        bw = min(30, colw * 0.82)
        for li, l in enumerate(layers):
            cy = top - rowh * (li + 0.5)
            for k, i in enumerate(l):
                cx = left + (right - left) / 2 + (k - (len(l) - 1) / 2) * colw
                pos[i] = (cx, cy)
    palette = [LBLUE, '#FCE4D6', '#E2F0D9', '#FFF2CC', '#EADCF4']
    for li, l in enumerate(layers):
        for i in l:
            x, y = pos[i]
            ax.add_patch(FancyBboxPatch((x - bw / 2, y - bh / 2), bw, bh, boxstyle='round,pad=0.4,rounding_size=1.2',
                                        fc=palette[li % len(palette)], ec=BLUE, lw=2))
            fs, txt = _fit_fs(byid[i]['label'], bw - 1.5, bh - 1, base=15)
            ax.text(x, y, txt, ha='center', va='center', fontsize=fs, color='#1b1b1b', linespacing=1.15)
    for e in edges:
        (x1, y1), (x2, y2) = pos[e['from']], pos[e['to']]
        if direction == 'LR':
            if x2 > x1: p1 = (x1 + bw / 2 + 0.4, y1); p2 = (x2 - bw / 2 - 0.4, y2)
            elif x2 < x1: p1 = (x1 - bw / 2 - 0.4, y1); p2 = (x2 + bw / 2 + 0.4, y2)
            else: p1 = (x1, y1 - bh / 2 - 0.4 if y2 < y1 else y1 + bh / 2 + 0.4); p2 = (x2, y2 + bh / 2 + 0.4 if y2 < y1 else y2 - bh / 2 - 0.4)
        else:
            if y2 < y1: p1 = (x1, y1 - bh / 2 - 0.4); p2 = (x2, y2 + bh / 2 + 0.4)
            elif y2 > y1: p1 = (x1, y1 + bh / 2 + 0.4); p2 = (x2, y2 - bh / 2 - 0.4)
            else: p1 = (x1 + bw / 2 + 0.4 if x2 > x1 else x1 - bw / 2 - 0.4, y1); p2 = (x2 - bw / 2 - 0.4 if x2 > x1 else x2 + bw / 2 + 0.4, y2)
        ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle='-|>', mutation_scale=18, lw=2, color=DGRAY, connectionstyle='arc3,rad=0'))
        if e.get('label'):
            if direction == 'TB':
                ax.text((p1[0] + p2[0]) / 2 + 1.5, (p1[1] + p2[1]) / 2, _wrap(e['label'], 16), ha='left', va='center', fontsize=10,
                        color=ORANGE, fontweight='bold', bbox=dict(fc='white', ec='none', pad=0.5, alpha=0.9))
            else:
                ax.text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 1.6, _wrap(e['label'], 14), ha='center', va='bottom', fontsize=10,
                        color=ORANGE, fontweight='bold', bbox=dict(fc='white', ec='none', pad=0.5, alpha=0.9))
    return fig


# ---------------------------------------------------------------- window
CTRL_H = {'button': 6.5, 'textbox': 6.0, 'label': 4.5, 'checkbox': 4.5, 'radio': 4.5, 'combobox': 6.0, 'listbox': 14,
          'datagrid': 16, 'picturebox': 15, 'chart': 17, 'progressbar': 4.5, 'groupbox': 14, 'menu': 5, 'tabcontrol': 14}


def _draw_ctrl(ax, kind, text, x, y, w):
    h = CTRL_H.get(kind, 6)
    t = str(text or '')
    if kind == 'button':
        ax.add_patch(FancyBboxPatch((x, y - h), w, h, boxstyle='round,pad=0.1,rounding_size=0.8', fc='#E1E1E1', ec='#7A7A7A', lw=1.4))
        fs, txt = _fit_fs(t, w - 1, h - .8, base=11, minfs=8)
        ax.text(x + w / 2, y - h / 2, txt, ha='center', va='center', fontsize=fs)
    elif kind == 'textbox':
        ax.add_patch(Rectangle((x, y - h), w, h, fc='white', ec='#7A7A7A', lw=1.4))
        ax.text(x + 1, y - h / 2, t, ha='left', va='center', fontsize=11, color=DGRAY)
    elif kind == 'label':
        ax.text(x, y - h / 2, t, ha='left', va='center', fontsize=11.5, fontweight='bold', color='#222')
    elif kind == 'checkbox':
        ax.add_patch(Rectangle((x, y - h / 2 - 1.2), 2.4, 2.4, fc='white', ec='#333', lw=1.4))
        ax.plot([x + .4, x + 1.1, x + 2.0], [y - h / 2, y - h / 2 - .8, y - h / 2 + .8], color=GREEN, lw=2)
        ax.text(x + 3.6, y - h / 2, t, ha='left', va='center', fontsize=11)
    elif kind == 'radio':
        ax.add_patch(Circle((x + 1.2, y - h / 2), 1.2, fc='white', ec='#333', lw=1.4))
        ax.add_patch(Circle((x + 1.2, y - h / 2), 0.55, fc=BLUE, ec='none'))
        ax.text(x + 3.6, y - h / 2, t, ha='left', va='center', fontsize=11)
    elif kind == 'combobox':
        ax.add_patch(Rectangle((x, y - h), w, h, fc='white', ec='#7A7A7A', lw=1.4))
        ax.add_patch(Rectangle((x + w - 4, y - h), 4, h, fc='#E1E1E1', ec='#7A7A7A', lw=1.4))
        ax.add_patch(Polygon([(x + w - 3.2, y - h / 2 + .7), (x + w - .8, y - h / 2 + .7), (x + w - 2, y - h / 2 - .8)], fc='#333'))
        ax.text(x + 1, y - h / 2, t, ha='left', va='center', fontsize=11, color=DGRAY)
    elif kind == 'listbox':
        ax.add_patch(Rectangle((x, y - h), w, h, fc='white', ec='#7A7A7A', lw=1.4))
        items = [s.strip() for s in re.split(r'[;|]', t) if s.strip()] or [t]
        for k, s in enumerate(items[:4]):
            yy = y - 2.2 - k * 3.2
            if k == 0: ax.add_patch(Rectangle((x + .3, yy - 1.4), w - .6, 3, fc=MBLUE, ec='none'))
            ax.text(x + 1, yy, s, ha='left', va='center', fontsize=10.5)
    elif kind == 'datagrid':
        ax.add_patch(Rectangle((x, y - h), w, h, fc='white', ec='#7A7A7A', lw=1.4))
        cols = [s.strip() for s in re.split(r'[;|]', t) if s.strip()] or ['A', 'B', 'C']
        cols = cols[:4]; cw = w / len(cols)
        ax.add_patch(Rectangle((x, y - 3.8), w, 3.8, fc=LBLUE, ec='#7A7A7A', lw=1))
        for k, c in enumerate(cols):
            ax.text(x + cw * k + 1, y - 1.9, c, ha='left', va='center', fontsize=10, fontweight='bold')
            if k: ax.plot([x + cw * k] * 2, [y - h, y], color='#BBB', lw=1)
        for r in range(1, 4): ax.plot([x, x + w], [y - 3.8 * (r + 1)] * 2, color='#CCC', lw=1)
    elif kind == 'picturebox':
        ax.add_patch(Rectangle((x, y - h), w, h, fc='#EAF3FB', ec='#7A7A7A', lw=1.4))
        ax.add_patch(Polygon([(x + 1, y - h + 1), (x + w * .38, y - h * .55), (x + w * .6, y - h + 1)], fc=GREEN, ec='none'))
        ax.add_patch(Polygon([(x + w * .45, y - h + 1), (x + w * .72, y - h * .45), (x + w - 1, y - h + 1)], fc='#548235', ec='none'))
        ax.add_patch(Circle((x + w * .8, y - h * .22), 1.8, fc='#FFC000', ec='none'))
        if t: ax.text(x + w / 2, y + 0.3, t, ha='center', va='bottom', fontsize=9, color=DGRAY)
    elif kind == 'chart':
        ax.add_patch(Rectangle((x, y - h), w, h, fc='white', ec='#7A7A7A', lw=1.4))
        xs = np.linspace(0, 1, 40)
        ys = 0.5 + 0.35 * np.sin(xs * 2 * math.pi)
        ax.plot(x + 3 + xs * (w - 5), y - h + 2 + ys * (h - 5), color=ORANGE, lw=2.2)
        ax.plot([x + 3, x + 3], [y - h + 1.5, y - 1.5], color='#444', lw=1.2)
        ax.plot([x + 3, x + w - 1.5], [y - h + 1.5] * 2, color='#444', lw=1.2)
        if t: ax.text(x + w / 2, y - 1.4, t, ha='center', va='center', fontsize=9.5, color=DGRAY)
    elif kind == 'progressbar':
        ax.add_patch(Rectangle((x, y - h + 1), w, h - 2, fc='white', ec='#7A7A7A', lw=1.4))
        ax.add_patch(Rectangle((x, y - h + 1), w * 0.62, h - 2, fc=GREEN, ec='none'))
        if t: ax.text(x + w / 2, y - h / 2, t, ha='center', va='center', fontsize=9.5)
    elif kind == 'groupbox':
        ax.add_patch(Rectangle((x, y - h), w, h - 1.5, fc='none', ec='#8C8C8C', lw=1.4))
        ax.text(x + 1.5, y - 0.5, ' %s ' % t, ha='left', va='center', fontsize=10.5, fontweight='bold', bbox=dict(fc='white', ec='none', pad=1))
    elif kind == 'tabcontrol':
        tabs = [s.strip() for s in re.split(r'[;|]', t) if s.strip()] or ['Tab1', 'Tab2']
        tw = min(w / len(tabs[:4]), 14)
        for k, s in enumerate(tabs[:4]):
            ax.add_patch(Rectangle((x + k * tw, y - 4), tw, 4, fc='white' if k == 0 else '#E1E1E1', ec='#7A7A7A', lw=1.2))
            ax.text(x + k * tw + tw / 2, y - 2, s, ha='center', va='center', fontsize=10)
        ax.add_patch(Rectangle((x, y - h), w, h - 4, fc='white', ec='#7A7A7A', lw=1.2))
    else:
        raise SpecError('window: noma\'lum boshqaruv turi: %s' % kind)
    return h


def _group_controls(controls):
    """Ketma-ket tugmalarni (2-3 ta) bitta qatorga birlashtirish."""
    out, run = [], []
    for c in controls:
        if c.get('kind') == 'button':
            run.append(c); continue
        if run: out.append(('row', run)); run = []
        out.append(('one', c))
    if run: out.append(('row', run))
    res = []
    for kind, v in out:
        if kind == 'row':
            for k in range(0, len(v), 3): res.append(('row', v[k:k + 3]))
        else: res.append((kind, v))
    return res


def _window(spec):
    controls = spec.get('controls') or []
    if not (1 <= len(controls) <= 14): raise SpecError('window: controls soni 1..14')
    fig, ax = _new(None)
    ax.add_patch(Rectangle((4, 3), 92, 63, fc='white', ec='#333', lw=2))
    ax.add_patch(Rectangle((4, 60), 92, 6, fc='#2B579A', ec='#333', lw=2))
    ax.text(6, 63, spec.get('title', 'Form1'), color='white', fontsize=13, fontweight='bold', va='center')
    for k, s in enumerate(['–', '□', '✕']):
        ax.text(87 + k * 3.2, 63, s, color='white', fontsize=12, ha='center', va='center')
    y = 60
    menu = spec.get('menu') or []
    if menu:
        ax.add_patch(Rectangle((4, y - 4.5), 92, 4.5, fc='#F0F0F0', ec='#BBB', lw=1))
        x = 6
        for m in menu[:8]:
            ax.text(x, y - 2.3, m, fontsize=11, va='center'); x += 2.2 + len(m) * 1.25
        y -= 4.5
    tb = spec.get('toolbar') or []
    if tb:
        ax.add_patch(Rectangle((4, y - 5.5), 92, 5.5, fc='#E8EEF7', ec='#BBB', lw=1))
        x = 6
        for t_ in tb[:8]:
            ax.add_patch(FancyBboxPatch((x, y - 4.6), 3.6, 3.6, boxstyle='round,pad=0.1,rounding_size=0.5', fc=MBLUE, ec=BLUE, lw=1))
            ax.text(x + 4.4, y - 2.8, t_, fontsize=9.5, va='center'); x += 6.5 + len(t_) * 1.1
        y -= 5.5
    status = spec.get('status')
    bottom = 3 + (4 if status else 0)
    if status:
        ax.add_patch(Rectangle((4, 3), 92, 4, fc='#007ACC', ec='#333', lw=1))
        ax.text(6, 5, status, color='white', fontsize=10.5, va='center')
    items = _group_controls(controls)
    cols = [[], []]; heights = [0, 0]
    for it in items:
        k = 0 if heights[0] <= heights[1] else 1
        h = (CTRL_H['button'] if it[0] == 'row' else CTRL_H.get(it[1].get('kind', 'label'), 6)) + 2.2
        cols[k].append(it); heights[k] += h
    avail = y - bottom - 2
    if max(heights) > avail + 0.001:
        raise SpecError('window: boshqaruvlar sig\'maydi (kam boshqaruv bering)')
    wide = len(items) <= 4
    for ci, lst in enumerate(cols):
        x = 12 if wide else (7 if ci == 0 else 53)
        w = 76 if wide else 40
        yy = y - 2.5
        for kind, v in lst:
            if kind == 'row':
                n = len(v); gap = 2; bw_ = min(34, (w - gap * (n - 1)) / n)
                for j, c in enumerate(v):
                    _draw_ctrl(ax, 'button', c.get('text', ''), x + j * (bw_ + gap), yy, bw_)
                h = CTRL_H['button']
            else:
                kd = v.get('kind', 'label')
                h = _draw_ctrl(ax, kd, v.get('text', ''), x, yy, w if kd not in ('checkbox', 'radio') else min(w, 34))
            yy -= h + 2.2
    return fig


# ---------------------------------------------------------------- plot
_ALLOWED = {k: getattr(np, k) for k in ('sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'abs', 'arctan', 'sinh', 'cosh', 'tanh', 'log10', 'floor', 'ceil')}
_ALLOWED.update({'pi': math.pi, 'e': math.e})


def _eval(expr, x):
    ex = str(expr).replace('^', '**')
    if re.search(r'__|import|open|exec|eval|lambda|;', ex): raise SpecError('plot: noto\'g\'ri ifoda: %s' % expr)
    env = dict(_ALLOWED); env['x'] = x
    with np.errstate(all='ignore'):
        y = eval(ex, {'__builtins__': {}}, env)
    return np.broadcast_to(np.asarray(y, dtype=float), x.shape)


def _plot(spec):
    funcs = spec.get('functions') or []
    if not (1 <= len(funcs) <= 4): raise SpecError('plot: functions 1..4')
    xmin = float(spec.get('xmin', -6.3)); xmax = float(spec.get('xmax', 6.3))
    if not xmin < xmax: raise SpecError('plot: xmin<xmax')
    fig = plt.figure(figsize=(W, H), dpi=100, facecolor='white')
    ax = fig.add_axes([0.09, 0.12, 0.88, 0.74])
    x = np.linspace(xmin, xmax, 800)
    cols = [BLUE, ORANGE, GREEN, RED]
    ymax_all = []
    for k, f in enumerate(funcs):
        y = _eval(f['expr'], x)
        if not np.isfinite(y).any(): raise SpecError('plot: ifoda qiymat bermadi: %s' % f['expr'])
        y = np.where(np.abs(y) > 1e3, np.nan, y)
        ax.plot(x, y, color=cols[k], lw=2.8, label=f.get('label', f['expr']))
        ymax_all.append(np.nanmax(np.abs(y)))
    lim = min(max(ymax_all) * 1.35, 50)
    ax.set_ylim(-lim, lim)
    ax.axhline(0, color='#444', lw=1.2); ax.axvline(0, color='#444', lw=1.2)
    ax.grid(True, color='#DDD', lw=0.8)
    ax.legend(fontsize=13, loc='best', frameon=True, framealpha=0.9)
    ax.tick_params(labelsize=12)
    for s in ('top', 'right'): ax.spines[s].set_visible(False)
    fig.patches.append(Rectangle((0, 0.9), 1, 0.1, transform=fig.transFigure, color=BLUE))
    fig.text(0.025, 0.95, spec.get('title', ''), color='white', fontsize=17, fontweight='bold', va='center')
    return fig


# ---------------------------------------------------------------- table
def _table(spec):
    headers = spec.get('headers') or []; rows = spec.get('rows') or []
    if not (2 <= len(headers) <= 5): raise SpecError('table: headers 2..5')
    if not (1 <= len(rows) <= 8): raise SpecError('table: rows 1..8')
    for r in rows:
        if len(r) != len(headers): raise SpecError('table: qator uzunligi headers ga teng emas')
    fig, ax = _new(spec.get('title'))
    n = len(headers); x0, x1 = 4, 96; cw = (x1 - x0) / n
    rh = min(9.5, 52 / (len(rows) + 1))
    y = 59
    for k, h in enumerate(headers):
        ax.add_patch(Rectangle((x0 + k * cw, y - rh), cw, rh, fc=BLUE, ec='white', lw=1.5))
        fs, txt = _fit_fs(h, cw - 1.5, rh - .8, base=14)
        ax.text(x0 + k * cw + cw / 2, y - rh / 2, txt, color='white', ha='center', va='center', fontsize=fs, fontweight='bold')
    for ri, r in enumerate(rows):
        yy = y - rh * (ri + 1)
        for k, v in enumerate(r):
            ax.add_patch(Rectangle((x0 + k * cw, yy - rh), cw, rh, fc=LBLUE if ri % 2 == 0 else WHITE, ec='#9DB7D1', lw=1.2))
            fs, txt = _fit_fs(v, cw - 1.5, rh - .8, base=13)
            ax.text(x0 + k * cw + cw / 2, yy - rh / 2, txt, ha='center', va='center', fontsize=fs)
    return fig


# ---------------------------------------------------------------- code
_KW = r'\b(?:int|double|float|char|bool|void|string|class|struct|public|private|protected|return|if|else|for|while|do|switch|case|break|new|delete|template|typename|using|namespace|include|const|auto|static|virtual|override|foreach|var|this|true|false|null|nullptr|try|catch|throw|in|get|set)\b'


def _code(spec):
    lines = spec.get('lines') or []
    if not (2 <= len(lines) <= 15): raise SpecError('code: lines 2..15')
    if max(len(l) for l in lines) > 62: raise SpecError('code: qator 62 belgidan uzun')
    fig, ax = _new(spec.get('title'))
    ax.add_patch(FancyBboxPatch((3, 3), 94, 56, boxstyle='round,pad=0.3,rounding_size=1.5', fc='#1E1E1E', ec='#333', lw=2))
    ax.add_patch(Rectangle((3, 55), 94, 4, fc='#2D2D30', ec='none'))
    for k, c in enumerate(['#FF5F56', '#FFBD2E', '#27C93F']): ax.add_patch(Circle((6 + k * 2.6, 57), 0.9, fc=c, ec='none'))
    ax.text(50, 57, spec.get('language', 'C++'), color='#AAA', fontsize=10, ha='center', va='center')
    n = len(lines); lh = min(3.9, 49 / n); fs = max(9, min(13.5, lh * 3.3))
    for k, l in enumerate(lines):
        yy = 52.3 - k * lh
        ax.text(5, yy, '%2d' % (k + 1), color='#6E7681', fontsize=fs, family='DejaVu Sans Mono', va='center')
        x = 9.0; cw = fs * 0.0836
        for tok in re.split(r'(//.*$|"[^"]*"|%s)' % _KW, l):
            if not tok: continue
            if tok.startswith('//'): col = '#6A9955'
            elif tok.startswith('"'): col = '#CE9178'
            elif re.fullmatch(_KW, tok): col = '#569CD6'
            elif re.fullmatch(r'\d+(\.\d+)?', tok.strip()): col = '#B5CEA8'
            else: col = '#D4D4D4'
            ax.text(x, yy, tok, color=col, fontsize=fs, family='DejaVu Sans Mono', va='center')
            x += len(tok) * cw
    return fig


# ---------------------------------------------------------------- shapes
def _shapes(spec):
    items = spec.get('items') or []
    if not (2 <= len(items) <= 8): raise SpecError('shapes: items 2..8')
    fig, ax = _new(spec.get('title'))
    n = len(items); cols = 4 if n > 6 else (3 if n > 4 else (2 if n == 4 else n)); rows = math.ceil(n / cols)
    cw, ch = 92 / cols, 56 / rows
    for k, it in enumerate(items):
        r, c = divmod(k, cols)
        cx = 4 + cw * (c + 0.5); cy = 60 - ch * (r + 0.5)
        ax.add_patch(Rectangle((cx - cw / 2 + 1, cy - ch / 2 + 1), cw - 2, ch - 2, fc='#FAFAFA', ec='#CCC', lw=1.2))
        s = it.get('shape', 'rect'); a = min(cw, ch) * 0.28
        kw = dict(fc=MBLUE, ec=BLUE, lw=2.5)
        ox, oy = cx, cy + ch * 0.08
        if s == 'line': ax.plot([ox - a * 1.3, ox + a * 1.3], [oy - a * .6, oy + a * .6], color=BLUE, lw=4)
        elif s == 'rect': ax.add_patch(Rectangle((ox - a * 1.2, oy - a * .8), a * 2.4, a * 1.6, **kw))
        elif s == 'ellipse': ax.add_patch(Ellipse((ox, oy), a * 2.6, a * 1.6, **kw))
        elif s == 'triangle': ax.add_patch(Polygon([(ox - a * 1.2, oy - a * .8), (ox + a * 1.2, oy - a * .8), (ox, oy + a)], **kw))
        elif s == 'polygon': ax.add_patch(Polygon([(ox + a * math.cos(2 * math.pi * j / 5 + math.pi / 2), oy + a * math.sin(2 * math.pi * j / 5 + math.pi / 2)) for j in range(5)], **kw))
        elif s == 'arc': ax.add_patch(Arc((ox, oy - a * .3), a * 2.4, a * 2.0, theta1=0, theta2=180, color=BLUE, lw=4))
        elif s == 'pie': ax.add_patch(Wedge((ox, oy), a, 30, 330, **kw))
        elif s == 'text': ax.text(ox, oy, 'Abc', fontsize=26, ha='center', va='center', color=BLUE, fontweight='bold')
        else: raise SpecError('shapes: noma\'lum shakl: %s' % s)
        ax.text(cx, cy - ch * 0.36, _wrap(it.get('label', s), 22), ha='center', va='center', fontsize=11.5, fontweight='bold', color='#222')
    return fig


# ---------------------------------------------------------------- stack
def _stack(spec):
    layers = spec.get('layers') or []
    if not (2 <= len(layers) <= 7): raise SpecError('stack: layers 2..7')
    fig, ax = _new(spec.get('title'))
    n = len(layers); lh = min(10.5, 54 / n)
    pal = [BLUE, '#2E75B6', '#5B9BD5', '#9DC3E6', '#BDD7EE', '#DEEBF7', '#EEF5FB']
    for k, l in enumerate(layers):
        yy = 60 - lh * (k + 1)
        col = pal[min(k, len(pal) - 1)]
        ax.add_patch(FancyBboxPatch((8, yy + .6), 84, lh - 1.2, boxstyle='round,pad=0.2,rounding_size=1.2', fc=col, ec='white', lw=2))
        tc = 'white' if k < 3 else '#1b1b1b'
        ax.text(12, yy + lh / 2 + (1.2 if l.get('sub') else 0), l['label'], color=tc, fontsize=15, fontweight='bold', va='center')
        if l.get('sub'): ax.text(12, yy + lh / 2 - 1.8, _wrap(l['sub'], 70), color=tc, fontsize=11, va='center')
    return fig


_DISPATCH = {'flow': _flow, 'window': _window, 'plot': _plot, 'table': _table, 'code': _code, 'shapes': _shapes, 'stack': _stack}


def render(spec, path):
    t = spec.get('type')
    if t not in _DISPATCH: raise SpecError('noma\'lum rasm turi: %s (mumkin: %s)' % (t, ', '.join(FIG_TYPES)))
    try:
        fig = _DISPATCH[t](spec)
    except SpecError:
        raise
    except (KeyError, TypeError, IndexError, AttributeError) as ex:
        raise SpecError('%s: maydon xatosi: %r' % (t, ex))
    fig.savefig(path, dpi=100, facecolor='white')
    plt.close(fig)
    return path
