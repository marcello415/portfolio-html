"""Pull job-search numbers from the Asana "Job Search" board and write them into the admin site.

applications = cards in Applied, Interview, Offer, Rejected
interviews   = cards in Interview, Offer
sources      = distinct source codes at the end of card titles ("... — Company · ZIP")
"""
import json, os, re, sys, urllib.request, urllib.parse
from pathlib import Path

PROJECT = os.environ.get("ASANA_PROJECT_GID", "1220250026925579")
TOKEN = os.environ.get("ASANA_TOKEN", "").strip().strip('"').removeprefix("Bearer ").strip()
if not TOKEN:
    sys.exit("ASANA_TOKEN secret is empty.")
print(f"Token length {len(TOKEN)}, starts {TOKEN[:2]}…")
APPLIED = {"Applied", "Interview", "Offer", "Rejected"}
INTERVIEW = {"Interview", "Offer"}
ROOT = Path(__file__).resolve().parents[2] / "admin"


def get(path, **params):
    out, params = [], {**params, "limit": 100}
    while True:
        url = f"https://app.asana.com/api/1.0{path}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {TOKEN}"})
        with urllib.request.urlopen(req, timeout=30) as r:
            body = json.load(r)
        out += body["data"]
        nxt = body.get("next_page")
        if not nxt:
            return out
        params["offset"] = nxt["offset"]


sections = {s["name"].strip(): s["gid"] for s in get(f"/projects/{PROJECT}/sections")}
missing = APPLIED - sections.keys()
if missing:
    sys.exit(f"Board is missing sections: {missing}")

apps = interviews = 0
sources = set()
for name in APPLIED:
    tasks = get(f"/sections/{sections[name]}/tasks", opt_fields="name")
    apps += len(tasks)
    if name in INTERVIEW:
        interviews += len(tasks)
    for t in tasks:
        code = t["name"].rsplit("·", 1)[-1].strip()
        if re.fullmatch(r"[A-Z]{2,4}", code):
            sources.add(code)

stats = {"applications": apps, "interviews": interviews, "sources": len(sources)}
print(stats, sorted(sources))
if apps == 0:
    sys.exit("Got 0 applications; refusing to overwrite the site.")

tag = re.compile(r'(<(\w+)\b[^>]*\bdata-stat="(\w+)"[^>]*>)[^<]*(</\2>)')
for page in [ROOT / "index.html", ROOT / "work" / "job-search-automation.html"]:
    html = page.read_text()
    page.write_text(tag.sub(lambda m: f"{m[1]}{stats.get(m[3], '')}{m[4]}" if m[3] in stats else m[0], html))

llms = ROOT / "llms.txt"
llms.write_text(re.sub(r"\d+ applications so far", f"{apps} applications so far", llms.read_text()))
