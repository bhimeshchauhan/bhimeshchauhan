"""Regenerates assets/activity.svg: days with at least one contribution, by year, from GitHub's own data.
Private-repo activity is included as counts only (no repo names). Needs the GitHub CLI logged in:  python3 scripts/update-activity.py
"""
import datetime, json, subprocess
from pathlib import Path

USER = "bhimeshchauhan"
QUERY = 'query($f:DateTime!,$t:DateTime!){user(login:"%s"){createdAt contributionsCollection(from:$f,to:$t){contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}' % USER

def year(y):
    now = datetime.datetime.utcnow()
    to = now if y == now.year else datetime.datetime(y, 12, 31, 23, 59, 59)
    r = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"f={y}-01-01T00:00:00Z", "-f", f"t={to:%Y-%m-%dT%H:%M:%SZ}"], capture_output=True, text=True, check=True)
    cal = json.loads(r.stdout)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"] if d["date"].startswith(str(y))]
    return cal["totalContributions"], sum(1 for d in days if d["contributionCount"] > 0)

first = 2017
rows = [(y, *year(y)) for y in range(first, datetime.date.today().year + 1)]
total_c = sum(r[1] for r in rows); total_d = sum(r[2] for r in rows)
F = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'
W, H, left, base, top = 1000, 300, 48, 236, 96
bw, gap = 62, 28
mx = max(r[2] for r in rows)
out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Days with at least one GitHub contribution, by year, from {first} to {rows[-1][0]}: {", ".join(f"{y} {d}" for y, c, d in rows)}. {total_d} active days and {total_c} contributions in total, private repositories included as counts only.">',
       f'<title>Active days on GitHub, by year</title>',
       f'<rect width="{W}" height="{H}" rx="16" fill="#0b0c10" stroke="#262b3d"/>',
       f'<text x="32" y="40" {F} font-size="12" fill="#6f7488" letter-spacing="1.6">ACTIVE DAYS ON GITHUB, BY YEAR</text>',
       f'<text x="32" y="74" {F} font-size="26" font-weight="700" fill="#f2f0ea">{total_d:,} active days · {total_c:,} contributions since {first}</text>',
       f'<text x="{W-32}" y="74" {F} font-size="13" fill="#a3a8b8" text-anchor="end">private repositories included as counts only</text>']
for i, (y, c, d) in enumerate(rows):
    h = max(4, int((base - top - 22) * d / mx)); x = left + i * (bw + gap); cur = (y == rows[-1][0])
    out += [f'<rect x="{x}" y="{base-h}" width="{bw}" height="{h}" rx="6" fill="#ffb454" opacity="{1 if cur else .55}"/>',
            f'<text x="{x+bw/2}" y="{base-h-8}" {F} font-size="15" font-weight="700" fill="#f2f0ea" text-anchor="middle">{d}</text>',
            f'<text x="{x+bw/2}" y="{base+20}" {F} font-size="14" fill="{"#ffb454" if cur else "#a3a8b8"}" text-anchor="middle" font-weight="{600 if cur else 400}">{y}</text>',
            f'<text x="{x+bw/2}" y="{base+38}" {F} font-size="11" fill="#6f7488" text-anchor="middle">{c:,} contrib.</text>']
out.append('</svg>')
Path(__file__).resolve().parents[1].joinpath("assets", "activity.svg").write_text("\n".join(out) + "\n")
print("years:", ", ".join(f"{y}: {d} days" for y, c, d in rows)); print("total", total_d, "days,", total_c, "contributions")
