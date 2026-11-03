"""Static checks for the Constraints section of .claude/spec.md.

These read the source files instead of running the app, so they catch rule breaks
(SQL outside models.py, |safe in templates, a leaked key...) that a passing
acceptance test would not.
"""

import ast
import re
import subprocess

import pytest

from conftest import ROOT

REQUIRED_FILES = ["app.py", "models.py", "validators.py", "ai.py", "seed.py", "static/chat.js"]
ALLOWED_PACKAGES = {"flask", "python-dotenv", "pypdf", "google-genai", "pytest"}
FORBIDDEN_IMPORTS = {
    "sqlalchemy", "flask_sqlalchemy", "flask_login", "langchain", "llama_index",
    "chromadb", "pinecone", "faiss", "openai", "google.generativeai", "requests", "httpx",
}
SQL_PATTERN = re.compile(
    r"\b(SELECT\s+.+\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|CREATE\s+TABLE)\b",
    re.IGNORECASE | re.DOTALL,
)
SKIP_DIRS = {"tests", ".git", ".venv", "venv", "env", "__pycache__", ".claude", "node_modules"}


def project_files(*suffixes):
    return [
        p
        for p in ROOT.rglob("*")
        if p.is_file() and p.suffix in suffixes and not SKIP_DIRS & set(p.relative_to(ROOT).parts)
    ]


def string_literals(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node
        elif isinstance(node, ast.JoinedStr):
            yield node


def parse(path):
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


@pytest.mark.parametrize("name", REQUIRED_FILES)
def test_required_file_exists(name):
    assert (ROOT / name).is_file(), f"{name} is required by the spec"


def test_sql_only_in_models():
    offenders = []
    for path in project_files(".py"):
        if path.name == "models.py":
            continue
        for node in string_literals(parse(path)):
            text = node.value if isinstance(node, ast.Constant) else ast.unparse(node)
            if SQL_PATTERN.search(text):
                offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    for path in project_files(".html", ".jinja", ".j2"):
        if SQL_PATTERN.search(path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"SQL outside models.py: {offenders}"


def test_sql_is_parameterized():
    """No f-strings, + concatenation, % formatting, or .format() in execute() calls."""
    path = ROOT / "models.py"
    if not path.exists():
        pytest.skip("models.py not written yet")
    offenders = []
    for node in ast.walk(parse(path)):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)):
            continue
        if node.func.attr not in {"execute", "executemany", "executescript"} or not node.args:
            continue
        sql = node.args[0]
        built = isinstance(sql, (ast.JoinedStr, ast.BinOp)) or (
            isinstance(sql, ast.Call)
            and isinstance(sql.func, ast.Attribute)
            and sql.func.attr == "format"
        )
        if built:
            offenders.append(f"models.py:{node.lineno}")
    assert not offenders, f"SQL built from strings instead of ? placeholders: {offenders}"


def test_no_orm_or_forbidden_libraries():
    offenders = []
    for path in project_files(".py"):
        for node in ast.walk(parse(path)):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
            for name in names:
                if any(name == bad or name.startswith(bad + ".") for bad in FORBIDDEN_IMPORTS):
                    offenders.append(f"{path.relative_to(ROOT)}:{node.lineno} imports {name}")
    assert not offenders, offenders


def test_ai_provider_only_called_from_ai_py():
    offenders = []
    for path in project_files(".py"):
        if path.name == "ai.py":
            continue
        source = path.read_text(encoding="utf-8")
        if re.search(r"^\s*(from\s+google\s+import\s+genai|import\s+google\.genai)", source, re.M):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"google-genai used outside ai.py: {offenders}"


def test_requirements_only_allowed_packages():
    path = ROOT / "requirements.txt"
    assert path.exists(), "requirements.txt is missing"
    packages = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#")[0].strip()
        if line:
            packages.add(re.split(r"[<>=!~\[; ]", line, maxsplit=1)[0].lower().replace("_", "-"))
    extra = packages - ALLOWED_PACKAGES
    assert not extra, f"packages not on the spec's allowed list: {sorted(extra)}"


def test_templates_do_not_disable_escaping():
    offenders = []
    for path in project_files(".html", ".jinja", ".j2"):
        text = path.read_text(encoding="utf-8")
        if re.search(r"\|\s*safe\b", text) or re.search(r"{%\s*autoescape\s+false", text):
            offenders.append(str(path.relative_to(ROOT)))
    for path in project_files(".py"):
        if re.search(r"\bMarkup\s*\(", path.read_text(encoding="utf-8")):
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"|safe, autoescape false, or Markup() used: {offenders}"


def test_question_box_has_no_maxlength():
    offenders = [
        str(p.relative_to(ROOT))
        for p in project_files(".html", ".jinja", ".j2")
        if re.search(r"<textarea[^>]*maxlength|<input[^>]*name=[\"']question[\"'][^>]*maxlength",
                     p.read_text(encoding="utf-8"), re.I | re.S)
    ]
    assert not offenders, f"the 500-character rule must be server-side only: {offenders}"


def test_only_chat_js_and_no_external_scripts():
    js_files = sorted(str(p.relative_to(ROOT).as_posix()) for p in project_files(".js"))
    assert js_files in ([], ["static/chat.js"]), f"only static/chat.js is allowed: {js_files}"
    offenders = []
    for path in project_files(".html", ".jinja", ".j2"):
        for tag in re.findall(r"<script\b[^>]*>", path.read_text(encoding="utf-8"), re.I):
            if "chat.js" not in tag:
                offenders.append(f"{path.relative_to(ROOT)}: {tag}")
    assert not offenders, f"script tags other than chat.js: {offenders}"


def test_env_is_ignored_and_not_committed():
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8-sig").splitlines()
    assert ".env" in [line.strip() for line in gitignore]
    tracked = subprocess.run(
        ["git", "ls-files", ".env"], cwd=ROOT, capture_output=True, text=True
    ).stdout.strip()
    assert not tracked, ".env is committed; remove it with `git rm --cached .env`"


def test_no_api_keys_in_source():
    key = re.compile(r"AIza[0-9A-Za-z_\-]{35}")
    offenders = [
        str(p.relative_to(ROOT))
        for p in project_files(".py", ".html", ".js", ".md", ".txt", ".json", ".yml", ".yaml")
        if key.search(p.read_text(encoding="utf-8", errors="ignore"))
    ]
    assert not offenders, f"something that looks like a Google API key: {offenders}"


def test_debug_mode_not_hard_coded():
    offenders = [
        str(p.relative_to(ROOT))
        for p in project_files(".py")
        if re.search(r"debug\s*=\s*True|DEBUG\s*=\s*True", p.read_text(encoding="utf-8"))
    ]
    assert not offenders, f"debug must come from FLASK_DEBUG in .env: {offenders}"
