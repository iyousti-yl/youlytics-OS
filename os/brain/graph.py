#!/usr/bin/env python3
"""The OS brain: every file in the workspace and how they connect (for the Brain micro app).

  python3 os/brain/graph.py           summary: files, links, the most connected files
  python3 os/brain/graph.py --json    the full graph as JSON (the dashboard serves this at /api/brain)

Nodes are the files git tracks or would track (gitignored data like reports and logs is left out)
plus their folders. Edges are:
  folder   a folder holds a file or folder
  link     a file points to another: Markdown links, [[wiki links]], @imports, `path/in/backticks`,
           HTML href/src, and /skill mentions (to that skill's SKILL.md)
Nothing is stored; the graph is rebuilt from the files every time, so it never goes stale.
"""
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TEXT = {".md", ".html", ".json", ".py", ".js", ".css", ".txt", ".svg", ".example", ""}
SKIP = {".gitkeep", ".DS_Store"}
GENERIC = {"CHANGELOG.md", "NOTES.md", "index.html", "README.md", "README.txt", "app.json", "config.json", "SKILL.md"}
GROUPS = {"knowledge": "knowledge", "business": "business", "life": "life", "memory": "memory",
          ".claude": "skills", "os": "os", "brand": "brand", "artifacts": "brand", "docs": "docs"}
MD_LINK = re.compile(r"\]\(([^)\s#]+)")
WIKI = re.compile(r"\[\[([^\]|#]+)")
IMPORT = re.compile(r"(?:^|\s)@([\w./-]+\.md)")
TICK = re.compile(r"`([\w.-]+(?:/[\w.<>-]*)+|[\w-]+\.(?:md|json|html|py))`")
HREF = re.compile(r"""(?:href|src)=["']([^"'#?:]+)["']""")
SKILL = re.compile(r"(?<![\w/.-])/([a-z][a-z0-9-]+)\b")
QUOTED = re.compile(r"""["']([\w./-]+\.(?:html|json|md|py|js|css|txt|png|svg))["']""")  # in code and JSON
PY_IMPORT = re.compile(r"^\s*import (\w+)", re.M)


def files():
    try:
        out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"],
                             cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True).stdout.splitlines()
    except (OSError, subprocess.CalledProcessError):
        out = [str(p.relative_to(ROOT)) for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
    return sorted(f for f in out if Path(f).name not in SKIP and (ROOT / f).is_file()
                  and "__pycache__" not in f and not f.endswith(".pyc"))


def group(path):
    top = path.split("/")[0]
    if "/" not in path:
        return "core"
    return GROUPS.get(top, "os")


def label(path):
    p = Path(path)
    if p.name == "SKILL.md":
        return "/" + p.parent.name
    if p.name in GENERIC and len(p.parts) > 1:  # e.g. tone/CHANGELOG.md instead of a dozen CHANGELOG.md
        return f"{p.parent.name}/{p.name}"
    return p.name


def build():
    paths = files()
    known = set(paths)
    folders = {str(Path(p).parent) for p in paths if "/" in p}
    for f in list(folders):  # every ancestor folder too
        parts = Path(f).parts
        folders.update(str(Path(*parts[:i])) for i in range(1, len(parts)))
    stems = {}
    for p in paths:
        stems.setdefault(Path(p).stem.lower(), p)
    skills = {Path(p).parent.name: p for p in paths if p.startswith(".claude/skills/") and p.endswith("/SKILL.md")}

    nodes = [{"id": p, "label": label(p), "group": group(p), "kind": "file"} for p in paths]
    nodes += [{"id": f + "/", "label": Path(f).name + "/", "group": group(f + "/x"), "kind": "folder"} for f in sorted(folders)]
    edges = set()
    for p in paths:
        parent = str(Path(p).parent)
        if parent != ".":
            edges.add((parent + "/", p, "folder"))
    for f in folders:
        parent = str(Path(f).parent)
        if parent != ".":
            edges.add((parent + "/", f + "/", "folder"))

    def resolve(src, ref):
        ref = ref.strip().rstrip(".,;:").replace("<name>", "").replace("<", "").replace(">", "")
        if not ref or ref.startswith(("http", "mailto:", "chrome:", "#")):
            return None
        for base in (Path(src).parent, Path(".")):
            cand = (ROOT / base / ref).resolve()
            try:
                rel = str(cand.relative_to(ROOT))
            except ValueError:
                continue
            if rel in known:
                return rel
            if rel in folders:
                return rel + "/"
        return None

    for p in paths:
        if Path(p).suffix not in TEXT:
            continue
        try:
            text = (ROOT / p).read_text(errors="replace", encoding="utf-8")[:200_000]
        except OSError:
            continue
        targets = set()
        for rx in (MD_LINK, IMPORT, TICK, HREF):
            for ref in rx.findall(text):
                t = resolve(p, ref)
                if t:
                    targets.add(t)
        if Path(p).suffix in (".py", ".js", ".json"):
            for ref in QUOTED.findall(text):
                t = resolve(p, ref)
                if t:
                    targets.add(t)
        if Path(p).suffix == ".py":
            for mod in PY_IMPORT.findall(text):
                sib = str(Path(p).parent / f"{mod}.py")
                if sib in known:
                    targets.add(sib)
        # Files inside a skill folder (changelog, notes, references) belong to its SKILL.md.
        parts = Path(p).parts
        if len(parts) > 3 and parts[:2] == (".claude", "skills") and parts[-1] != "SKILL.md":
            owner = skills.get(parts[2])
            if owner:
                targets.add(owner)
        for name in WIKI.findall(text):
            t = stems.get(name.strip().lower())
            if t:
                targets.add(t)
        if Path(p).suffix in (".md", ".json", ".html") and Path(p).name not in ("CHANGELOG.md", "NOTES.md"):
            for name in SKILL.findall(text):
                if name in skills:
                    targets.add(skills[name])
        for t in targets:
            if t != p and t != str(Path(p).parent) + "/":
                edges.add((p, t, "link"))
        # An image and its description belong together.
        if Path(p).suffix == ".txt":
            for ext in (".png", ".jpg", ".svg"):
                img = str(Path(p).with_suffix(ext))
                if img in known:
                    edges.add((p, img, "link"))

    degree = Counter()
    for a, b, kind in edges:
        if kind == "link":
            degree[a] += 1
            degree[b] += 1
    for n in nodes:
        n["links"] = degree.get(n["id"], 0)
    return {"nodes": nodes, "edges": [{"source": a, "target": b, "kind": k} for a, b, k in sorted(edges)]}


def preview(path, limit=4000):
    """The start of one file in the graph, for the side panel. None if it isn't a text file in the graph."""
    if path not in set(files()) or Path(path).suffix not in TEXT or path.endswith(".env"):
        return None
    return (ROOT / path).read_text(errors="replace", encoding="utf-8")[:limit]


def main(argv):
    g = build()
    if "--json" in argv:
        print(json.dumps(g))
        return 0
    links = [e for e in g["edges"] if e["kind"] == "link"]
    files_ = [n for n in g["nodes"] if n["kind"] == "file"]
    print(f"{len(files_)} files, {len(g['nodes']) - len(files_)} folders, {len(links)} links between files.\n")
    print("Most connected:")
    for n in sorted(files_, key=lambda n: -n["links"])[:12]:
        print(f"  {n['links']:>3}  {n['id']}")
    lonely = [n["id"] for n in files_ if n["links"] == 0]
    print(f"\n{len(lonely)} files nothing links to or from (candidates for a line in a router file).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
