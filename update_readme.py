import json, os, re, urllib.request
from datetime import date

USER = "pedrohcml"
BORN = date.fromisoformat(os.environ["BIRTHDATE"])

def api(path):
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"},
    )
    return json.load(urllib.request.urlopen(req))

user = api(f"/users/{USER}")
repos = api(f"/users/{USER}/repos?per_page=100")
stars = sum(r["stargazers_count"] for r in repos)

today = date.today()
months = (today.year - BORN.year) * 12 + today.month - BORN.month - (today.day < BORN.day)

values = {
    "Uptime": f"{months // 12} years, {months % 12} months",
    "Repos": user["public_repos"],
    "Stars": stars,
    "Followers": user["followers"],
}

test = open("README.md", encoding="utf-8").read()
for key, val in values.items():
    def fix(m, key=key, val=val):
        prefix = f". {key}: "
        fill = len(m.group(0)) - len(prefix) - len(str(val)) - 1
        return prefix + "." * fill + " " + str(val)
    text = re.sub(rf"^\. {key}:.*$", fix, text, flags=re.M)

open("README.md", "w", encoding="utf-8").write(text)