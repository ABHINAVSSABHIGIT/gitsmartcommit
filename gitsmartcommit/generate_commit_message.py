# Modified generate_commit_message.py
"""
gitcommit — smart commit message generator from git diff
Supports: Python, JS, TS, React, Vue, Svelte, Java, Go, Rust,
          PHP, C, C++, C#, Ruby, Swift, Kotlin, SQL, HTML, XML,
          CSS, SCSS, Shell, Dart, Lua, Elixir, GraphQL, Protobuf,
          JSON, YAML, TOML, Markdown, Docker, CI/CD configs and more.
"""

import re
import subprocess
import sys
from collections import defaultdict


# ─────────────────────────────────────────────────────────────────────────────
# ANSI COLORS & ICONS
# ─────────────────────────────────────────────────────────────────────────────

class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Foreground
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[98m"

    # Tag colors
    TAG_COLORS = {
        "[ADD]": "\033[92m",  # green
        "[FIX]": "\033[91m",  # red
        "[REMOVE]": "\033[91m",  # red
        "[UPDATE]": "\033[94m",  # blue
        "[REFACTOR]": "\033[95m",  # magenta
        "[STYLE]": "\033[96m",  # cyan
        "[DOCS]": "\033[93m",  # yellow
        "[CONFIG]": "\033[93m",  # yellow
        "[TEST]": "\033[95m",  # magenta
        "[RENAME]": "\033[96m",  # cyan
        "[CHORE]": "\033[90m",  # gray
    }

    @staticmethod
    def tag(t: str) -> str:
        color = C.TAG_COLORS.get(t, C.WHITE)
        return f"{C.BOLD}{color}{t}{C.RESET}"

    @staticmethod
    def bold(s: str) -> str:
        return f"{C.BOLD}{s}{C.RESET}"

    @staticmethod
    def dim(s: str) -> str:
        return f"{C.DIM}{C.GRAY}{s}{C.RESET}"

    @staticmethod
    def green(s: str) -> str:
        return f"{C.GREEN}{s}{C.RESET}"

    @staticmethod
    def red(s: str) -> str:
        return f"{C.RED}{s}{C.RESET}"

    @staticmethod
    def cyan(s: str) -> str:
        return f"{C.CYAN}{s}{C.RESET}"

    @staticmethod
    def yellow(s: str) -> str:
        return f"{C.YELLOW}{s}{C.RESET}"

    @staticmethod
    def blue(s: str) -> str:
        return f"{C.BLUE}{s}{C.RESET}"

    @staticmethod
    def white(s: str) -> str:
        return f"{C.WHITE}{s}{C.RESET}"


# Icons per tag
TAG_ICON = {
    "[ADD]": "✚",
    "[FIX]": "✖",
    "[REMOVE]": "✖",
    "[UPDATE]": "●",
    "[REFACTOR]": "⟳",
    "[STYLE]": "◈",
    "[DOCS]": "✎",
    "[CONFIG]": "⚙",
    "[TEST]": "⚑",
    "[RENAME]": "↪",
    "[CHORE]": "⊡",
}

# Language icons
LANG_ICON = {
    "Python": "🐍",
    "JavaScript": "🟨",
    "TypeScript": "🔷",
    "React": "⚛",
    "Vue": "💚",
    "Svelte": "🧡",
    "Java": "☕",
    "Go": "🐹",
    "Rust": "🦀",
    "PHP": "🐘",
    "C": "©",
    "C++": "⊕",
    "C#": "♯",
    "Ruby": "💎",
    "Swift": "🦅",
    "Kotlin": "🎯",
    "Scala": "λ",
    "SQL": "🗄",
    "HTML": "🌐",
    "XML": "📄",
    "CSS": "🎨",
    "SCSS": "🎨",
    "Shell": "🐚",
    "Docker": "🐳",
    "Node": "📦",
    "GraphQL": "◈",
    "Markdown": "📝",
    "YAML": "⚙",
    "JSON": "{}",
    "TOML": "⚙",
    "Dart": "🎯",
    "Elixir": "💧",
    "Haskell": "λ",
    "Lua": "🌙",
    "CI/CD": "🔄",
    "Environment": "🔐",
    "Git": "📄",  # Added for Git
    "LICENSE": "📄",  # Added for LICENSE
}

# ─────────────────────────────────────────────────────────────────────────────
# LANGUAGE / FILE TYPE MAPS
# ─────────────────────────────────────────────────────────────────────────────

EXT_LANG = {
    ".py": "Python", ".pyw": "Python", ".pyi": "Python",
    ".js": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".ts": "TypeScript", ".mts": "TypeScript",
    ".jsx": "React", ".tsx": "React",
    ".vue": "Vue", ".svelte": "Svelte",
    ".java": "Java", ".kt": "Kotlin", ".kts": "Kotlin",
    ".scala": "Scala", ".sc": "Scala",
    ".go": "Go",
    ".rs": "Rust",
    ".c": "C", ".h": "C",
    ".cpp": "C++", ".cc": "C++", ".cxx": "C++", ".hpp": "C++", ".hxx": "C++",
    ".cs": "C#",
    ".rb": "Ruby", ".rake": "Ruby", ".gemspec": "Ruby",
    ".php": "PHP", ".php5": "PHP", ".php7": "PHP", ".phtml": "PHP",
    ".swift": "Swift",
    ".dart": "Dart",
    ".ex": "Elixir", ".exs": "Elixir",
    ".hs": "Haskell", ".lhs": "Haskell",
    ".clj": "Clojure", ".cljs": "Clojure",
    ".lua": "Lua",
    ".r": "R", ".rmd": "R",
    ".pl": "Perl", ".pm": "Perl",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell", ".fish": "Shell",
    ".ps1": "PowerShell", ".psm1": "PowerShell",
    ".html": "HTML", ".htm": "HTML", ".xhtml": "HTML",
    ".xml": "XML", ".xsl": "XSLT", ".xslt": "XSLT",
    ".svg": "SVG",
    ".css": "CSS", ".scss": "SCSS", ".sass": "Sass", ".less": "LESS",
    ".sql": "SQL", ".ddl": "SQL", ".dml": "SQL",
    ".graphql": "GraphQL", ".gql": "GraphQL",
    ".proto": "Protobuf",
    ".json": "JSON", ".jsonc": "JSON",
    ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML",
    ".ini": "Config", ".cfg": "Config", ".conf": "Config",
    ".env": "Environment",
    ".md": "Markdown", ".mdx": "Markdown",
    ".rst": "reStructuredText",
    ".txt": "Text",
    ".tf": "Terraform", ".hcl": "HCL",
    ".gradle": "Gradle",
}

SPECIAL_FILES = {
    "dockerfile": "Docker",
    "docker-compose.yml": "Docker",
    "docker-compose.yaml": "Docker",
    ".dockerignore": "Docker",
    "makefile": "Build",
    "cmakelists.txt": "CMake",
    "jenkinsfile": "CI/CD",
    ".travis.yml": "CI/CD",
    ".github": "CI/CD",
    "package.json": "Node",
    "package-lock.json": "Node",
    "yarn.lock": "Node",
    "pnpm-lock.yaml": "Node",
    "tsconfig.json": "TypeScript",
    "jsconfig.json": "JavaScript",
    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "setup.py": "Python",
    "setup.cfg": "Python",
    "pipfile": "Python",
    "pipfile.lock": "Python",
    "go.mod": "Go",
    "go.sum": "Go",
    "cargo.toml": "Rust",
    "cargo.lock": "Rust",
    "composer.json": "PHP",
    "composer.lock": "PHP",
    "pom.xml": "Maven",
    "build.gradle": "Gradle",
    "gemfile": "Ruby",
    "gemfile.lock": "Ruby",
    ".gitignore": "Git",
    ".gitattributes": "Git",
    ".env": "Environment",
    ".env.example": "Environment",
    ".env.local": "Environment",
    ".prettierrc": "Formatter",
    ".eslintrc": "Linter",
    ".eslintrc.js": "Linter",
    ".eslintrc.json": "Linter",
    ".eslintrc.yml": "Linter",
    ".editorconfig": "Editor",
    ".babelrc": "Babel",
    "vite.config.js": "Vite",
    "vite.config.ts": "Vite",
    "webpack.config.js": "Webpack",
    "webpack.config.ts": "Webpack",
    "next.config.js": "Next.js",
    "next.config.mjs": "Next.js",
    "nuxt.config.js": "Nuxt",
    "nuxt.config.ts": "Nuxt",
    "angular.json": "Angular",
    "tailwind.config.js": "Tailwind",
    "tailwind.config.ts": "Tailwind",
    "jest.config.js": "Jest",
    "jest.config.ts": "Jest",
    "vitest.config.ts": "Vitest",
    ".mocharc.js": "Mocha",
    "license": "LICENSE",  # Added for LICENSE
}

TEST_PATH_RE = re.compile(
    r"(tests?/|specs?/|__tests?__/|\.test\.|\.spec\.|_test\.|test_\w|/test/|/spec/|Test\.\w+$|Tests\.\w+$)",
    re.IGNORECASE,
)

DEP_FILES = {
    "requirements.txt", "pipfile", "go.mod", "cargo.toml",
    "composer.json", "gemfile", "pom.xml", "build.gradle",
    "package.json",
}

# Files that look like JSON/YAML but are really config — not source code
PURE_CONFIG_NAMES = {
    "package.json", "package-lock.json", "tsconfig.json", "jsconfig.json",
    ".eslintrc.json", ".prettierrc", ".babelrc", "composer.json",
    "pom.xml", "build.gradle",
}


# ─────────────────────────────────────────────────────────────────────────────
# PATH HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def file_ext(path: str) -> str:
    name = path.rsplit("/", 1)[-1].lower()
    if "." in name:
        return "." + name.rsplit(".", 1)[-1]
    return ""


def file_name(path: str) -> str:
    return path.rsplit("/", 1)[-1]


def module(path: str) -> str:
    name = file_name(path)
    return name.rsplit(".", 1)[0] if "." in name else name


def language(path: str) -> str:
    name = file_name(path).lower()
    if name in SPECIAL_FILES:
        return SPECIAL_FILES[name]
    return EXT_LANG.get(file_ext(path), "")


def lang_icon(path: str) -> str:
    return LANG_ICON.get(language(path), "")


def is_test(path: str) -> bool:
    return bool(TEST_PATH_RE.search(path))


def is_doc(path: str) -> bool:
    return file_ext(path) in (".md", ".mdx", ".rst", ".txt", ".adoc")


def is_config(path: str) -> bool:
    name = file_name(path).lower()
    ext = file_ext(path)
    return (
            name in SPECIAL_FILES
            or name in PURE_CONFIG_NAMES
            or ext in (".ini", ".cfg", ".conf", ".env")
            or "config" in name
            or "settings" in name
            or name.startswith(".eslint")
            or name.startswith(".prettier")
            or name.startswith(".babel")
    )


def is_style(path: str) -> bool:
    return file_ext(path) in (".css", ".scss", ".sass", ".less", ".styl")


def is_markup(path: str) -> bool:
    return file_ext(path) in (".html", ".htm", ".xhtml", ".xml", ".xsl", ".xslt", ".svg")


def is_sql(path: str) -> bool:
    return file_ext(path) in (".sql", ".ddl", ".dml")


# ─────────────────────────────────────────────────────────────────────────────
# DIFF PARSER
# ─────────────────────────────────────────────────────────────────────────────

FILE_HEADER_RE = re.compile(r"^diff --git a/(.+?) b/(.+?)$")
NEW_FILE_RE = re.compile(r"^new file mode")
DELETED_RE = re.compile(r"^deleted file mode")
RENAME_TO_RE = re.compile(r"^rename to (.+)")
BINARY_RE = re.compile(r"^Binary files")
HUNK_RE = re.compile(r"^@@ [^@]+ @@\s*(.*)")


def parse_diff(diff_text: str) -> list:
    files = []
    cur = None

    for line in diff_text.splitlines():
        m = FILE_HEADER_RE.match(line)
        if m:
            if cur:
                files.append(cur)
            cur = {
                "path": m.group(2),
                "old_path": m.group(1),
                "added": [],
                "removed": [],
                "hunk_ctx": [],
                "is_new": False,
                "is_deleted": False,
                "is_rename": False,
                "is_binary": False,
            }
            continue

        if cur is None:
            continue

        if NEW_FILE_RE.match(line):
            cur["is_new"] = True
        elif DELETED_RE.match(line):
            cur["is_deleted"] = True
        elif RENAME_TO_RE.match(line):
            cur["is_rename"] = True
            cur["path"] = RENAME_TO_RE.match(line).group(1)
        elif BINARY_RE.match(line):
            cur["is_binary"] = True
        elif HUNK_RE.match(line):
            ctx = HUNK_RE.match(line).group(1).strip()
            if ctx:
                cur["hunk_ctx"].append(ctx)
        elif line.startswith("+") and not line.startswith("+++"):
            cur["added"].append(line[1:])
        elif line.startswith("-") and not line.startswith("---"):
            cur["removed"].append(line[1:])

    if cur:
        files.append(cur)

    return files


# ─────────────────────────────────────────────────────────────────────────────
# SCOPE / DEFINITION DETECTION  (per language)
# ─────────────────────────────────────────────────────────────────────────────

# Each pattern tries to capture the function/class/method name
DEF_PATTERNS = [
    # Python: def foo / async def foo / class Foo
    re.compile(r"^\s*(?:async\s+)?def\s+(\w+)", re.I),
    re.compile(r"^\s*class\s+(\w+)"),

    # JavaScript / TypeScript: function foo / const foo = / async foo
    re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+(\w+)"),
    re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:function|\()"),
    re.compile(r"^\s*(?:export\s+)?(?:async\s+)?(\w+)\s*[:=]\s*(?:async\s+)?\("),

    # Go: func FuncName( / func (recv) FuncName(
    re.compile(r"^\s*func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\("),

    # Ruby: def foo / def self.foo
    re.compile(r"^\s*def\s+(?:self\.)?(\w+[?!]?)"),

    # PHP: function foo( / public function foo(
    re.compile(r"^\s*(?:public|private|protected|static|\s)*function\s+(\w+)\s*\(", re.I),

    # Java / C# / Kotlin / Swift: public ReturnType methodName(
    re.compile(
        r"^\s*(?:public|private|protected|static|final|abstract|override|async|suspend|\s)+[\w<>\[\]]+\s+(\w+)\s*\("),

    # Kotlin: fun foo( / suspend fun foo(
    re.compile(r"^\s*(?:suspend\s+)?(?:override\s+)?fun\s+(\w+)\s*[\(<]"),

    # Swift: func foo(
    re.compile(r"^\s*(?:public|private|internal|fileprivate|open|\s)*func\s+(\w+)\s*[\(<]"),

    # Rust: fn foo(
    re.compile(r"^\s*(?:pub(?:\(\w+\))?\s+)?(?:async\s+)?fn\s+(\w+)\s*[\(<]"),

    # C / C++: return_type function_name(
    re.compile(r"^\s*(?:static\s+)?(?:inline\s+)?(?:const\s+)?(?:\w+\s+)+(\w+)\s*\([^;]*$"),

    # SQL: CREATE/ALTER TABLE/FUNCTION/PROCEDURE
    re.compile(
        r"^\s*(?:CREATE|ALTER|DROP)\s+(?:OR\s+REPLACE\s+)?(?:TABLE|VIEW|FUNCTION|PROCEDURE|INDEX|TRIGGER)\s+(?:IF\s+(?:NOT\s+)?EXISTS\s+)?[`\"]?(\w+)",
        re.I),
]

SKIP_NAMES = {
    "if", "else", "elif", "for", "while", "return", "try", "catch",
    "except", "finally", "switch", "case", "when", "do", "in",
    "import", "from", "class", "def", "function", "const", "let", "var",
    "true", "false", "null", "nil", "none", "self", "this",
}


def find_defined_names(lines: list, added_only: bool = False) -> list:
    """Extract function/class/method names defined in these lines."""
    names = []
    for line in lines:
        for pat in DEF_PATTERNS:
            m = pat.match(line)
            if m:
                name = m.group(1)
                if name and name.lower() not in SKIP_NAMES and len(name) > 1:
                    names.append(name)
                    break
    return list(dict.fromkeys(names))  # deduplicated, order preserved


def detect_scope(fd: dict) -> str:
    """Best guess at which function/class is being changed."""
    # Hunk context (@@ lines often include surrounding function name)
    for ctx in fd["hunk_ctx"]:
        for pat in DEF_PATTERNS:
            m = pat.search(ctx)
            if m:
                name = m.group(1)
                if name and name.lower() not in SKIP_NAMES:
                    return name

    # Scan nearby added/removed lines
    for line in (fd["added"] + fd["removed"])[:30]:
        for pat in DEF_PATTERNS[:6]:  # only most reliable patterns
            m = pat.match(line)
            if m:
                name = m.group(1)
                if name and name.lower() not in SKIP_NAMES:
                    return name
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE ANALYSIS PATTERNS
# ─────────────────────────────────────────────────────────────────────────────

# Bug fix keywords — scored, not boolean
FIX_KW_RE = re.compile(
    r"\b(fix|bug|patch|hotfix|correct|wrong|broken|crash|traceback"
    r"|AttributeError|TypeError|KeyError|ValueError|IndexError|NameError"
    r"|ZeroDivisionError|RuntimeError|NullPointerException|overflow"
    r"|underflow|deadlock|race\s*condition|off.by.one|segfault|regression)\b",
    re.IGNORECASE,
)

# Error handling additions
ERROR_HANDLING_RE = re.compile(
    r"^\s*(try\s*:|except\s+|catch\s*\(|rescue\s+|raise\s+|throw\s+|"
    r"finally\s*:|ensure\s+|assert\s+|guard\s+|if.*is\s+None|"
    r"if.*==\s*null|if.*===\s*null|if.*is\s+not\s+None)",
    re.IGNORECASE,
)

# Null / None checks added
NULL_CHECK_RE = re.compile(
    r"\b(is\s+None|is\s+not\s+None|== null|!= null|=== null|!== null"
    r"|is\s+nil|nil\?|\.nil\?|guard\s+let|if let|unwrap|Optional)",
    re.IGNORECASE,
)

# Import / require lines
IMPORT_RE = re.compile(
    r"^\s*(?:import\s+|from\s+\S+\s+import\s+|require\s*\(|"
    r"use\s+[\w:]+;|using\s+[\w.]+;|include\s+[\"<]|@import\s+)",
    re.IGNORECASE,
)

# Route / endpoint definitions
ROUTE_RE = re.compile(
    r"""@(?:app|router|api|blueprint|bp)\.(?:get|post|put|patch|delete|route)\s*\(\s*['"]([^'"]+)['"]"""
    r"""|@(?:Get|Post|Put|Delete|Patch|RequestMapping|GetMapping|PostMapping)\s*(?:\(\s*['"]([^'"]+)['"])?"""
    r"""|router\.(?:get|post|put|patch|delete)\s*\(\s*['"]([^'"]+)['"]"""
    r"""|path\s*\(\s*['"]([^'"]+)['"]"""
    r"""|Route::(?:get|post|put|patch|delete|any)\s*\(\s*['"]([^'"]+)['"]""",
    re.IGNORECASE,
)

# SQL operations
SQL_OP_RE = re.compile(
    r"^\s*(SELECT|INSERT\s+INTO|UPDATE|DELETE\s+FROM|CREATE\s+TABLE|"
    r"ALTER\s+TABLE|DROP\s+TABLE|CREATE\s+INDEX|CREATE\s+VIEW|"
    r"CREATE\s+(?:OR\s+REPLACE\s+)?(?:FUNCTION|PROCEDURE)|TRUNCATE)",
    re.IGNORECASE,
)

SQL_TABLE_RE = re.compile(
    r"(?:FROM|INTO|UPDATE|JOIN|TABLE)\s+[`\"]?(\w+)[`\"]?",
    re.IGNORECASE,
)

# CSS / SCSS selectors
CSS_SEL_RE = re.compile(r"^\s*([.#][\w-]+(?:[\s,>+~:[\]]*[\w.#-]+)*)\s*\{")

# CSS properties
CSS_PROP_RE = re.compile(r"^\s*([\w-]+)\s*:\s*[^/]")

# XML / Odoo field tags
XML_FIELD_RE = re.compile(r'<field\s+name=["\'](\w+)["\']', re.IGNORECASE)

# XML / Odoo widget / attribute changes
XML_ATTR_RE = re.compile(r'\b(widget|invisible|readonly|required|domain|attrs|decoration-\w+)\s*=', re.IGNORECASE)

# Return value change
RETURN_RE = re.compile(r"^\s*return\b")

# Conditional logic
COND_RE = re.compile(r"^\s*(if|elif|else if|else|elsif|unless|switch|case|when|guard)\b", re.IGNORECASE)

# Loop additions
LOOP_RE = re.compile(r"^\s*(for|while|foreach|loop)\b", re.IGNORECASE)

# Decorator / annotation
DECORATOR_RE = re.compile(r"^\s*@(\w+)")

# Console / logging
LOG_RE = re.compile(
    r"\b(console\.(log|warn|error|debug|info)|print\s*\(|logger?\.|logging\.|"
    r"log\.(debug|info|warn|error)|fmt\.Print|System\.out\.print)",
    re.IGNORECASE,
)

# Assignment / field change
ASSIGN_RE = re.compile(r"^\s*(?:self|this)\.(\w+)\s*=")


# ─────────────────────────────────────────────────────────────────────────────
# CHANGE TYPE CLASSIFIER
# ─────────────────────────────────────────────────────────────────────────────

def classify(fd: dict) -> str:
    """
    Returns one of:
      new_file | deleted | rename | binary |
      test | docs | config | style | markup | sql |
      fix | feat | refactor | update
    """
    path = fd["path"]

    if fd["is_deleted"]: return "deleted"
    if fd["is_new"]:     return "new_file"
    if fd["is_rename"]:  return "rename"
    if fd["is_binary"]:  return "binary"

    if is_test(path):   return "test"
    if is_config(path): return "config"
    if is_doc(path):    return "docs"
    if is_style(path):  return "style"
    if is_markup(path): return "markup"
    if is_sql(path):    return "sql"

    added = fd["added"]
    removed = fd["removed"]
    n_add = len(added)
    n_rem = len(removed)
    all_text = "\n".join(added + removed)

    # ── fix score (needs clear evidence, not just any keyword) ──────────
    fix_score = 0

    # Strong signal: error-handling code explicitly added
    if any(ERROR_HANDLING_RE.match(l) for l in added):
        fix_score += 3

    # Strong signal: null/None check added
    if any(NULL_CHECK_RE.search(l) for l in added):
        fix_score += 2

    # Medium signal: fix-related keywords in comments or variable names
    # (only in added lines — not just anywhere in the diff)
    if FIX_KW_RE.search("\n".join(added)):
        fix_score += 1

    # Weak signal: small targeted change
    if 0 < n_add <= 6 and 0 < n_rem <= 6:
        fix_score += 1

    if fix_score >= 3:
        return "fix"

    # ── new definitions added ────────────────────────────────────────────
    new_names = find_defined_names(added)
    old_names = find_defined_names(removed)
    genuinely_new = [n for n in new_names if n not in old_names]
    if genuinely_new and n_add > n_rem * 0.5:
        return "feat"

    # ── balanced add/remove → refactor ──────────────────────────────────
    if n_add > 20 and n_rem > 20 and 0.4 < (n_add / max(n_rem, 1)) < 2.5:
        return "refactor"

    return "update"


# ─────────────────────────────────────────────────────────────────────────────
# DETAIL EXTRACTORS  (what specifically changed?)
# ─────────────────────────────────────────────────────────────────────────────

def extract_details(fd: dict, ctype: str) -> list:
    """
    Return a list of short detail strings describing what specifically changed.
    Max 4 items — keep it readable.
    """
    path = fd["path"]
    added = fd["added"]
    removed = fd["removed"]
    details = []

    # New / deleted files — no details needed (the message says it all)
    if ctype in ("new_file", "deleted", "rename", "binary", "docs"):
        return []

    # ── CONFIG ───────────────────────────────────────────────────────────
    if ctype == "config":
        name = file_name(path).lower()
        if name in DEP_FILES or name == "package.json":
            new_deps = _extract_dep_names(added)
            rem_deps = _extract_dep_names(removed)
            if new_deps:
                details.append(f"+ {', '.join(new_deps[:4])}")
            if rem_deps:
                details.append(f"- {', '.join(rem_deps[:4])}")
        ver = _extract_version_bump(added)
        if ver:
            details.append(f"version → {ver}")
        return details[:4]

    # ── SQL ──────────────────────────────────────────────────────────────
    if ctype == "sql":
        ops = []
        tables = set()
        for l in added + removed:
            m = SQL_OP_RE.match(l)
            if m:
                ops.append(m.group(1).upper().split()[0])
            for tm in SQL_TABLE_RE.findall(l):
                if tm.lower() not in ("from", "into", "join", "table", "update", "where"):
                    tables.add(tm)
        if ops:
            details.append("ops: " + ", ".join(list(dict.fromkeys(ops))[:3]))
        if tables:
            details.append("tables: " + ", ".join(list(sorted(tables))[:4]))
        return details[:4]

    # ── STYLE ────────────────────────────────────────────────────────────
    if ctype == "style":
        sels = []
        props = []
        for l in added + removed:
            ms = CSS_SEL_RE.match(l)
            if ms:
                sels.append(ms.group(1).strip())
            mp = CSS_PROP_RE.match(l)
            if mp and mp.group(1).lower() not in ("http", "https", "src"):
                props.append(mp.group(1).lower())
        if sels:
            details.append("selectors: " + ", ".join(list(dict.fromkeys(sels))[:3]))
        if props:
            details.append("properties: " + ", ".join(list(dict.fromkeys(props))[:4]))
        return details[:4]

    # ── MARKUP / XML ─────────────────────────────────────────────────────
    if ctype == "markup":
        at = "\n".join(added)
        rt = "\n".join(removed)
        new_f = set(XML_FIELD_RE.findall(at))
        gone_f = set(XML_FIELD_RE.findall(rt))
        only_n = sorted(new_f - gone_f)
        only_g = sorted(gone_f - new_f)
        mod_f = sorted(new_f & gone_f)
        if only_n:
            details.append("+ fields: " + ", ".join(only_n[:4]))
        if only_g:
            details.append("- fields: " + ", ".join(only_g[:4]))
        if mod_f:
            attrs = list(dict.fromkeys(XML_ATTR_RE.findall(at)))
            if attrs:
                details.append(f"modified {', '.join(mod_f[:2])}: {', '.join(attrs[:3])}")
            else:
                details.append("updated: " + ", ".join(mod_f[:3]))
        return details[:4]

    # ── TEST ─────────────────────────────────────────────────────────────
    if ctype == "test":
        test_names = [
            n for l in added
            for m in [
                re.search(r"(?:def\s+test_|it\s*\(['\"]|test\s*\(['\"]|describe\s*\(['\"]|@Test)(.+?)(?:['\"]|:|\()", l,
                          re.I)]
            if m
            for n in [m.group(1).strip()[:40]]
        ]
        if test_names:
            details.append("cases: " + ", ".join(test_names[:3]))
        return details[:4]

    # ── CODE (fix / feat / refactor / update) ───────────────────────────

    # New functions/classes added
    new_names = find_defined_names(added)
    old_names = find_defined_names(removed)
    added_defs = [n for n in new_names if n not in old_names]
    removed_defs = [n for n in old_names if n not in new_names]

    if added_defs:
        details.append("added: " + ", ".join(added_defs[:4]))
    if removed_defs:
        details.append("removed: " + ", ".join(removed_defs[:4]))

    # Routes changed
    all_text = "\n".join(added + removed)
    routes = []
    for m in ROUTE_RE.finditer(all_text):
        r = next((g for g in m.groups() if g), None)
        if r:
            routes.append(r)
    if routes:
        details.append("routes: " + ", ".join(routes[:3]))

    # Fields / attributes changed
    self_fields_a = [m.group(1) for l in added for m in [ASSIGN_RE.match(l)] if m]
    self_fields_r = [m.group(1) for l in removed for m in [ASSIGN_RE.match(l)] if m]
    changed_fields = list(dict.fromkeys(f for f in self_fields_a if f in self_fields_r))
    if changed_fields and not added_defs:
        details.append("fields: " + ", ".join(changed_fields[:4]))

    # Error handling
    err_lines = [l for l in added if ERROR_HANDLING_RE.match(l)]
    if err_lines and ctype == "fix":
        # Try to extract what's being caught
        exc = re.search(r"except\s+([\w,\s]+):|catch\s*\(([\w\s|]+)\)", "\n".join(err_lines), re.I)
        if exc:
            exc_name = (exc.group(1) or exc.group(2) or "").strip()[:40]
            details.append(f"handles: {exc_name}")

    # SQL in non-SQL files (e.g. ORM queries)
    sql_ops = [SQL_OP_RE.match(l).group(1).upper() for l in added + removed if SQL_OP_RE.match(l)]
    if sql_ops and not details:
        details.append("queries: " + ", ".join(dict.fromkeys(sql_ops)[:3]))

    return details[:4]


def _extract_dep_names(lines: list) -> list:
    names = []
    dep_re = re.compile(r'["\']?([\w@/.:-]{2,40})["\']?\s*[:=><~^]')
    for l in lines:
        # Skip obviously non-dep lines
        if re.search(r"(description|license|author|main|scripts|version|name)\s*[\":=]", l, re.I):
            continue
        m = dep_re.search(l)
        if m:
            n = m.group(1).strip(".-_")
            if n and len(n) > 1:
                names.append(n)
    return list(dict.fromkeys(names))


def _extract_version_bump(lines: list) -> str:
    for l in lines:
        m = re.search(r'["\']?version["\']?\s*[:=]\s*["\']?([\d.]+)', l, re.I)
        if m:
            return m.group(1)
    return ""


# ─────────────────────────────────────────────────────────────────────────────
# PER-FILE DESCRIPTOR  (tag + summary + details)
# ─────────────────────────────────────────────────────────────────────────────

def describe_file(fd: dict) -> dict:
    """Returns {tag, summary, details, lang, path}."""
    path = fd["path"]
    added = fd["added"]
    removed = fd["removed"]
    n_add = len(added)
    n_rem = len(removed)
    mod = module(path)
    lang = language(path)
    ctype = classify(fd)
    scope = detect_scope(fd)

    scope_s = f" in {scope}()" if scope else ""
    lang_s = f" [{lang}]" if lang else ""

    # ── structural ───────────────────────────────────────────────────────
    if ctype == "deleted":
        return _r("[REMOVE]", f"Remove {mod}{lang_s}", [], path)

    if ctype == "new_file":
        if is_test(path):
            return _r("[TEST]", f"Add tests for {mod}", [], path)
        purpose = _guess_purpose(added, path)
        # Special descriptive labels
        name_lower = file_name(path).lower()
        special_desc = {
            ".gitignore": "for exclusions",
            "license": "file",
            "readme.md": "for project overview",
            "pyproject.toml": "for build config",
            "setup.py": "for packaging",
            "__init__.py": "to initialize package",
            "generate_commit_message.py": "for message generation",
            "git.py": "for git services",
        }.get(name_lower, "")
        if special_desc:
            label = f"{file_name(path)} {special_desc}"
        else:
            label = purpose or file_name(path)
            if lang and not purpose:
                label += f" ({lang})"
        return _r("[ADD]", f"Add {label}", [], path)

    if ctype == "rename":
        old_mod = module(fd["old_path"])
        return _r("[RENAME]", f"Rename {old_mod} → {mod}", [], path)

    if ctype == "binary":
        return _r("[UPDATE]", f"Update binary asset {file_name(path)}", [], path)

    # ── specialized ──────────────────────────────────────────────────────
    details = extract_details(fd, ctype)

    if ctype == "test":
        verb = "Add" if n_add > n_rem * 1.5 else "Update"
        return _r("[TEST]", f"{verb} tests for {scope or mod}", details, path)

    if ctype == "docs":
        return _r("[DOCS]", f"Update {mod} documentation", details, path)

    if ctype == "config":
        name = file_name(path).lower()
        if name in DEP_FILES or name == "package.json":
            ver = _extract_version_bump(added)
            if ver:
                return _r("[CONFIG]", f"Bump {mod} version to {ver}", details, path)
            has_new = any(l.startswith("+") for d in details for l in [d])
            verb = "Update" if details else "Update"
            return _r("[CONFIG]", f"Update {lang or mod} dependencies", details, path)
        return _r("[CONFIG]", f"Update {lang or mod} configuration", details, path)

    if ctype == "style":
        sel_detail = next((d for d in details if "selectors" in d), "")
        if sel_detail:
            sel = sel_detail.replace("selectors: ", "")
            return _r("[STYLE]", f"Update styles for {sel}", details, path)
        return _r("[STYLE]", f"Update {mod} styles", details, path)

    if ctype == "markup":
        field_detail = next((d for d in details if "fields" in d or "+" in d), "")
        if field_detail:
            return _r("[UPDATE]", f"Update {mod} view/template", details, path)
        return _r("[UPDATE]", f"Update {mod} template", details, path)

    if ctype == "sql":
        op_detail = next((d for d in details if "ops:" in d), "")
        tbl_detail = next((d for d in details if "tables:" in d), "")
        op = op_detail.replace("ops: ", "").split(",")[0].strip().capitalize() if op_detail else "Update"
        tbl = tbl_detail.replace("tables: ", "").split(",")[0].strip() if tbl_detail else mod
        return _r("[UPDATE]", f"{op} SQL query on {tbl}", details, path)

    # ── code changes ─────────────────────────────────────────────────────
    if ctype == "fix":
        return _r("[FIX]", _describe_fix(added, removed, scope, mod), details, path)

    if ctype == "feat":
        new_names = find_defined_names(added)
        old_names_ = find_defined_names(removed)
        new_only = [n for n in new_names if n not in old_names_]
        if new_only:
            joined = ", ".join(new_only[:3])
            extra = f" +{len(new_only) - 3} more" if len(new_only) > 3 else ""
            return _r("[ADD]", f"Add {joined}{extra} in {mod}", details, path)
        return _r("[ADD]", f"Add new functionality in {mod}", details, path)

    if ctype == "refactor":
        return _r("[REFACTOR]", f"Refactor {scope or mod}{lang_s}", details, path)

    # ── generic update — try to say something useful ──────────────────────
    # Route change?
    all_text = "\n".join(added + removed)
    rm = ROUTE_RE.search(all_text)
    if rm:
        route = next((g for g in rm.groups() if g), None)
        if route:
            return _r("[UPDATE]", f"Update route '{route}' in {mod}", details, path)

    # Return value change?
    if any(RETURN_RE.match(l.strip()) for l in added) and any(RETURN_RE.match(l.strip()) for l in removed):
        return _r("[UPDATE]", f"Update return value{scope_s} in {mod}", details, path)

    # Conditional logic change?
    if any(COND_RE.match(l.strip()) for l in added):
        return _r("[UPDATE]", f"Update logic{scope_s} in {mod}", details, path)

    # Pure removal?
    if n_rem > 0 and n_add == 0:
        return _r("[REMOVE]", f"Remove unused code{scope_s} in {mod}", details, path)

    # Fallback
    verb = "Update"
    return _r("[UPDATE]", f"{verb} {scope or mod}{lang_s}", details, path)


def _r(tag, summary, details, path):
    return {"tag": tag, "summary": summary, "details": details,
            "lang": language(path), "path": path}


def _guess_purpose(lines: list, path: str) -> str:
    text = "\n".join(lines[:80])
    fp = path.lower()
    mod_ = module(path)
    lang = language(path)

    if re.search(r"(models\.Model|@Entity|@Table|Schema\(|struct\s+\w+\s*{.*db:|migrate)", text, re.I):
        return f"{mod_} model [{lang}]"
    if re.search(r"(class.*Controller|@Controller|@RestController|Blueprint|@router\.|Handler)", text, re.I):
        return f"{mod_} controller [{lang}]"
    if re.search(r"(class.*View|View\(|TemplateView|APIView|viewset)", text, re.I):
        return f"{mod_} view [{lang}]"
    if re.search(r"(Component|render\s*\(|template:|export default.*function|defineComponent)", text, re.I):
        return f"{mod_} component [{lang}]"
    if re.search(r"(Service|Repository|Dao|@Service|@Injectable)", text, re.I):
        return f"{mod_} service [{lang}]"
    if re.search(r"(middleware|Middleware)", text, re.I):
        return f"{mod_} middleware [{lang}]"
    if re.search(r"(migration|migrate\.|CREATE TABLE|ALTER TABLE)", text, re.I):
        return f"{mod_} migration [SQL]"
    if "util" in fp or "helper" in fp or "lib" in fp:
        return f"{mod_} utility [{lang}]"
    if "hook" in fp:
        return f"{mod_} hook [{lang}]"
    if "type" in fp or "interface" in fp or "types." in fp:
        return f"{mod_} types [{lang}]"
    lang_s = f" [{lang}]" if lang else ""
    return f"{mod_}{lang_s}"


def _describe_fix(added: list, removed: list, scope: str, mod: str) -> str:
    scope_s = f" in {scope}()" if scope else f" in {mod}"
    all_add = "\n".join(added)

    if NULL_CHECK_RE.search(all_add):
        return f"Fix null/None handling{scope_s}"
    if re.search(r"\b(valid|sanitize|assert|check)\b", all_add, re.I):
        return f"Fix validation{scope_s}"
    m = re.search(r"except\s+([\w]+)|catch\s*\(([\w\s|]+)\)", all_add)
    if m:
        exc = (m.group(1) or m.group(2) or "").strip()
        return f"Fix {exc or 'exception'} handling{scope_s}"
    if re.search(r"\b(index|bounds|range|length|size|offset)\b", all_add, re.I):
        return f"Fix index/bounds error{scope_s}"
    if re.search(r"\b(type|cast|convert|parse|coerce)\b", all_add, re.I):
        return f"Fix type mismatch{scope_s}"
    if re.search(r"\b(permission|access|auth|unauthorized|403|401)\b", all_add, re.I):
        return f"Fix access control{scope_s}"
    return f"Fix bug{scope_s}"


# ─────────────────────────────────────────────────────────────────────────────
# COMMIT MESSAGE COMPOSER
# ─────────────────────────────────────────────────────────────────────────────

TAG_PRIORITY = [
    "[FIX]", "[ADD]", "[REMOVE]", "[REFACTOR]",
    "[UPDATE]", "[STYLE]", "[DOCS]", "[CONFIG]",
    "[TEST]", "[RENAME]", "[CHORE]",
]


def _pick_tag(counts: dict) -> str:
    total = sum(counts.values())
    for tag in TAG_PRIORITY:
        if counts.get(tag, 0) / total >= 0.5:
            return tag
    for tag in TAG_PRIORITY:
        if tag in counts:
            return tag
    return "[UPDATE]"


def _trim(text: str, limit: int = 70) -> str:
    if len(text) <= limit:
        return text
    cut = text[:limit].rfind(" ")
    return (text[:cut] if cut > int(limit * 0.6) else text[:limit - 3]) + "..."


def create_commit_message(git_diff: str, branch: str = "") -> dict:
    """
    Returns a dict with:
      subject  — one-line commit summary (plain text, for git commit -m)
      display  — full colored terminal output
    """
    if not git_diff or not git_diff.strip():
        return {"subject": "[UPDATE] Minor changes", "display": ""}

    file_diffs = parse_diff(git_diff)
    if not file_diffs:
        return {"subject": "[UPDATE] Minor changes", "display": ""}

    results = []
    tag_counts = defaultdict(int)
    total_add = 0
    total_rem = 0

    for fd in file_diffs:
        info = describe_file(fd)
        results.append(info)
        tag_counts[info["tag"]] += 1
        total_add += len(fd["added"])
        total_rem += len(fd["removed"])

    primary_tag = _pick_tag(tag_counts)
    branch_part = f"[{branch}]" if branch else ""

    # ── build plain subject (tag must match the lead message) ──────────────
    if len(results) == 1:
        lead_tag = results[0]["tag"]
        subject_body = results[0]["summary"]
    else:
        lead_result = next(
            (r for tag in TAG_PRIORITY for r in results if r["tag"] == tag),
            results[0],
        )
        lead_tag = lead_result["tag"]
        extra = len(results) - 1
        subject_body = f"{lead_result['summary']} (+{extra} more)"

    plain_subject = _trim(f"{lead_tag}{branch_part} {subject_body}")

    # ── build colored display ─────────────────────────────────────────────
    display = _render(plain_subject, lead_tag, branch, results,
                      total_add, total_rem, tag_counts)

    return {"subject": plain_subject, "display": display, '_files': results}


def _render(subject, primary_tag, branch, results, total_add, total_rem, tag_counts) -> str:
    W = 66  # inner width
    bar = C.dim("─" * W)

    lines = []
    lines.append("")
    lines.append(C.dim("╭" + "─" * W + "╮"))

    # ── Header ───────────────────────────────────────────────────────────
    header_label = f"  {C.bold(C.cyan('git commit message'))}"
    if branch:
        header_label += C.dim(f"  •  branch: ") + C.yellow(branch)
    lines.append(C.dim("│") + header_label)
    lines.append(C.dim("├") + bar[len(C.dim("")):])  # separator

    # ── Subject line ─────────────────────────────────────────────────────
    icon = TAG_ICON.get(primary_tag, "●")
    colored = C.tag(primary_tag)
    plain_s = subject[len(primary_tag):]  # strip tag for separate coloring
    branch_display = ""
    if branch and f"[{branch}]" in plain_s:
        plain_s = plain_s.replace(f"[{branch}]", "").strip()
        branch_display = C.dim(f"[{branch}]") + " "
    lines.append(C.dim("│") + f"  {colored} {branch_display}{C.bold(plain_s.strip())}")
    lines.append(C.dim("│"))

    # ── Per-file breakdown ────────────────────────────────────────────────
    lines.append(C.dim(
        "│") + f"  {C.bold(C.white('Changes'))}  {C.dim(str(len(results)) + ' file' + ('s' if len(results) != 1 else ''))}")
    lines.append(C.dim("│") + f"  {bar}")

    for r in results:
        tag = r["tag"]
        icon_c = C.tag(tag)
        icon_s = TAG_ICON.get(tag, "●")
        li = LANG_ICON.get(r["lang"], "")
        path_disp = r["path"]

        # Truncate long paths nicely
        if len(path_disp) > 42:
            parts = path_disp.split("/")
            if len(parts) > 2:
                path_disp = "…/" + "/".join(parts[-2:])

        lang_badge = f" {C.dim(li + ' ' + r['lang'])}" if r["lang"] else ""

        lines.append(
            C.dim("│") +
            f"  {icon_c} {C.white(r['summary'])}{lang_badge}"
        )
        lines.append(
            C.dim("│") +
            f"     {C.dim('↳ ' + path_disp)}"
        )

        # Detail sub-bullets
        for d in r["details"]:
            # Color + / - prefixes
            if d.startswith("+"):
                lines.append(C.dim("│") + f"       {C.green('+')} {C.dim(d[2:])}")
            elif d.startswith("-"):
                lines.append(C.dim("│") + f"       {C.red('-')} {C.dim(d[2:])}")
            else:
                lines.append(C.dim("│") + f"       {C.dim('· ' + d)}")

        lines.append(C.dim("│"))

    # ── Stats footer ─────────────────────────────────────────────────────
    lines.append(C.dim("├") + bar[len(C.dim("")):])
    files_s = C.bold(str(len(results)))
    add_s = C.green(f"+{total_add}")
    rem_s = C.red(f"-{total_rem}")
    net = total_add - total_rem
    net_s = (C.green(f"net +{net}") if net > 0 else C.red(f"net {net}") if net < 0 else C.dim("net 0"))

    # Tag summary
    tag_summary = "  ".join(
        f"{C.tag(t)} {C.dim('×' + str(c))}"
        for t, c in sorted(tag_counts.items(), key=lambda x: -x[1])
    )

    lines.append(C.dim("│") + f"  {C.dim('Files')} {files_s}  {add_s}  {rem_s}  {net_s}")
    if len(tag_counts) > 1:
        lines.append(C.dim("│") + f"  {tag_summary}")
    lines.append(C.dim("╰") + "─" * W + "╯")

    # ── Plain text block (for copying to git) ────────────────────────────
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def generate_commit_message(diff, branch):
    if not diff.strip():
        print("\n  No diff found.")
        print("  → Stage changes with: git add <files>")
        print("  → Or use:  --source=unstaged  for unstaged changes\n")
        sys.exit(0)

    result = create_commit_message(diff, branch)

    return result