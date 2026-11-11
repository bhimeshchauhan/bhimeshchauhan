"""Rebuilds the activity sky from GitHub's own data:  python3 scripts/update-activity.py   (needs the GitHub CLI logged in)
Writes assets/activity-sky.svg (animated, for the README) and assets/activity.json ([date, contributions] for every active
day, used by the interactive page on the portfolio). Private-repository work appears as counts only, never names.
"""
import datetime, json, random, subprocess
from pathlib import Path

USER = "bhimeshchauhan"
Q = 'query($f:DateTime!,$t:DateTime!){user(login:"%s"){contributionsCollection(from:$f,to:$t){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}' % USER

def year_days(y):
    now = datetime.datetime.utcnow()
    to = now if y == now.year else datetime.datetime(y, 12, 31, 23, 59, 59)
    r = subprocess.run(["gh", "api", "graphql", "-f", f"query={Q}", "-f", f"f={y}-01-01T00:00:00Z", "-f", f"t={to:%Y-%m-%dT%H:%M:%SZ}"], capture_output=True, text=True, check=True)
    weeks = json.loads(r.stdout)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(d["date"], d["contributionCount"]) for w in weeks for d in w["contributionDays"] if d["date"].startswith(str(y)) and d["contributionCount"] > 0]

first, last = 2017, datetime.date.today().year
by_year = {y: year_days(y) for y in range(first, last + 1)}
days = sorted(d for ds in by_year.values() for d in ds)
root = Path(__file__).resolve().parents[1]
(root / "assets" / "activity.json").write_text(json.dumps(days, separators=(",", ":")) + "\n")

F = 'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"'
W, H, L, R, T, ROW = 1000, 372, 76, 36, 112, 25
span = W - L - R
rnd = random.Random(7)
total_c = sum(c for _, c in days)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Activity sky: every day with a GitHub contribution from {first} to {last} drawn as a star, one row per year. {len(days):,} active days and {total_c:,} contributions in total; private repositories are counted but not named.">',
     '<title>Activity sky</title>',
     '<defs><radialGradient id="g" cx="85%" cy="100%" r="80%"><stop offset="0" stop-color="#ffb454" stop-opacity=".16"/><stop offset=".6" stop-color="#3b4bd8" stop-opacity=".07"/><stop offset="1" stop-color="#0b0c10" stop-opacity="0"/></radialGradient></defs>',
     f'<rect width="{W}" height="{H}" rx="16" fill="#0b0c10"/><rect width="{W}" height="{H}" rx="16" fill="url(#g)"/><rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="#262b3d"/>',
     f'<text x="32" y="38" {F} font-size="12" fill="#6f7488" letter-spacing="1.6">THE ACTIVITY SKY · ONE STAR PER DAY I SHIPPED</text>',
     f'<text x="32" y="72" {F} font-size="26" font-weight="700" fill="#f2f0ea">{len(days):,} days, {first} to {last}</text>',
     f'<text x="{W-32}" y="72" {F} font-size="13" fill="#ffb454" text-anchor="end">Explore it: hover any star on my site →</text>']
for m, name in enumerate("JFMAMJJASOND"):
    o.append(f'<text x="{L + span * (m / 12) + 2}" y="{T-10}" {F} font-size="10" fill="#6f7488" letter-spacing="1">{name}</text>')
for i, y in enumerate(range(first, last + 1)):
    cy = T + i * ROW; cur = y == last
    o.append(f'<line x1="{L}" y1="{cy+ROW/2-2}" x2="{W-R}" y2="{cy+ROW/2-2}" stroke="#1a1d2a"/>')
    o.append(f'<text x="32" y="{cy+9}" {F} font-size="12" fill="{"#ffb454" if cur else "#a3a8b8"}" font-weight="{600 if cur else 400}">{y}</text>')
    for n, (date, c) in enumerate(by_year[y]):
        dt = datetime.date.fromisoformat(date)
        x = L + span * ((dt.timetuple().tm_yday - 1) / 366) + rnd.uniform(-1, 1)
        yy = cy + 5 + rnd.uniform(-5, 5)
        r = min(3.4, 1.1 + 0.55 * c ** 0.5)
        op = min(1, 0.42 + 0.07 * c) if not cur else min(1, 0.7 + 0.06 * c)
        fill = "#ffd08a" if cur else "#ffb454"
        if n % 6 == 0:
            o.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="{r:.1f}" fill="{fill}" opacity="{op:.2f}"><animate attributeName="opacity" values="{op:.2f};{max(.15, op-.45):.2f};{op:.2f}" dur="{rnd.uniform(2.6, 6.2):.1f}s" begin="-{rnd.uniform(0, 6):.1f}s" repeatCount="indefinite"/></circle>')
        else:
            o.append(f'<circle cx="{x:.1f}" cy="{yy:.1f}" r="{r:.1f}" fill="{fill}" opacity="{op:.2f}"/>')
o.append('</svg>')
(root / "assets" / "activity-sky.svg").write_text("\n".join(o) + "\n")
print(f"{len(days)} active days, {total_c} contributions; wrote assets/activity-sky.svg and assets/activity.json")
