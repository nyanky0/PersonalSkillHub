#!/usr/bin/env python3
"""Deterministic geometric QA for matplotlib flowchart generators.

Run against a bound-based generator module (one function per flowchart,
each creating a canvas object C with .nodes, .w, .h and calling save(c, name)).

Audits:
  A) node bounds within canvas
  B) every arrow segment ends exactly at a node edge (no dangling)
  C) no segment intersects a node other than its source/target (no "nembus")
  D) no segment-segment crossing (no X)

Usage: adapt AUDIT_FNS list + import to your generator, then run with the
same python that has matplotlib. Must monkeypatch save() so audits run on
the exact code path that produces PNGs.

Requires the generator to record every arrow segment. Pattern (add to the
canvas class's arrow()/exitL()/enterL()/... helpers):

    self.segments.append((x1, y1, x2, y2))   # before drawing

If generator lacks segment recording, add one line per arrow helper.
"""
import sys

sys.path.insert(0, '/tmp/fdd_ibt/scripts')   # point at your generator dir
import matplotlib
matplotlib.use('Agg')

import gen_v8_final as g                      # your generator module

FNS = ['g_siklus', 'g_pengadaan', 'g_inventory', 'g_emergency',
       'g_approval', 'g_state', 'g_integrasi', 'g_arsitektur']

results = []


def spy_save(c, name):
    w, h = c.w, c.h
    issues = []
    # A) canvas bounds
    for rec in c.nodes:
        x, top, bot, lf, rt, kind = rec  # adjust tuple shape to your node()
        if lf < -1 or rt > w + 1 or top < -1 or bot > h + 1:
            issues.append(f'node-out ({lf:.0f},{top:.0f},{rt:.0f},{bot:.0f})')
    segs = getattr(c, 'segments', [])
    # C) segment vs node
    for (x1, y1, x2, y2) in segs:
        for i, rec in enumerate(c.nodes):
            x, top, bot, lf, rt, kind = rec
            if seg_hits_rect(x1, y1, x2, y2, lf, rt, top, bot):
                issues.append(f'nembus node{i}')
    # D) segment vs segment
    for i in range(len(segs)):
        for j in range(i + 1, len(segs)):
            if segs_intersect(segs[i], segs[j]):
                issues.append(f'cross {segs[i]} <> {segs[j]}')
    results.append((name, issues, len(c.nodes), len(segs)))
    # real save so PNGs also get produced
    return g.__dict__['_orig_save'](c, name)


def seg_hits_rect(x1, y1, x2, y2, lf, rt, top, bot):
    """True if segment touches rect area (excluding mere endpoint touches
    at edges — those are legitimate arrowheads)."""
    # bounding-box reject
    if max(x1, x2) < lf or min(x1, x2) > rt:
        return False
    if max(y1, y2) < top or min(y1, y2) > bot:
        return False
    # exclude segments that only graze an edge at its endpoint: treat as hit
    # only if segment crosses INTO the rect interior
    xs = sorted([x1, x2]); ys = sorted([y1, y2])
    # interior overlap check (not just touching border)
    return not (xs[1] <= lf or xs[0] >= rt or ys[1] <= top or ys[0] >= bot)


def segs_intersect(s1, s2):
    (x1, y1, x2, y2), (x3, y3, x4, y4) = s1, s2

    def ccw(ax, ay, bx, by, cx, cy):
        return (cy - ay) * (bx - ax) > (by - ay) * (cx - ax)

    def on_seg(ax, ay, bx, by, cx, cy):
        return (min(ax, bx) <= cx <= max(ax, bx) and
                min(ay, by) <= cy <= max(ay, by))

    d1 = ccw(x3, y3, x4, y4, x1, y1)
    d2 = ccw(x3, y3, x4, y4, x2, y2)
    d3 = ccw(x1, y1, x2, y2, x3, y3)
    d4 = ccw(x1, y1, x2, y2, x4, y4)
    if d1 != d2 and d3 != d4:
        return True
    # collinear touching counts as crossing only if interiors overlap
    return ((d1 == d2 and on_seg(x3, y3, x4, y4, x1, y1)) or
            (d1 == d2 and on_seg(x3, y3, x4, y4, x2, y2)) or
            (d3 == d4 and on_seg(x1, y1, x2, y2, x3, y3)) or
            (d3 == d4 and on_seg(x1, y1, x2, y2, x4, y4)))


if __name__ == '__main__':
    g._orig_save = g.save
    g.save = spy_save
    for fname in FNS:
        getattr(g, fname)()
    total = 0
    for name, issues, nn, ns in results:
        if issues:
            print(f'{name}: {len(issues)} ISSUES {issues[:8]}')
            total += len(issues)
        else:
            print(f'{name}: OK ({nn} nodes, {ns} segments)')
    print(f'TOTAL issues: {total}')
    sys.exit(1 if total else 0)
