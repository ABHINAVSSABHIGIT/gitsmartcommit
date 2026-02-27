import pytest
from gitsmartcommit.generate_commit_message import create_commit_message, parse_diff, classify, describe_file, extract_details, detect_scope, language, find_defined_names

# Helper to create a simple file diff dict for testing classify and describe
def make_fd(path, added=None, removed=None, is_new=False, is_deleted=False, is_rename=False, is_binary=False, hunk_ctx=None, **kwargs):
    return {
        "path": path,
        "old_path": path if not is_rename else "old/" + path,
        "added": added or [],
        "removed": removed or [],
        "hunk_ctx": hunk_ctx or [],
        "is_new": is_new,
        "is_deleted": is_deleted,
        "is_rename": is_rename,
        "is_binary": is_binary,
    }

def test_empty_diff():
    result = create_commit_message("")
    assert result["subject"] == "[UPDATE] Minor changes"
    assert result["display"] == ""

def test_no_file_diffs():
    result = create_commit_message("diff --git a/file b/file")  # Returns something because it parses a file but no changes
    assert "[UPDATE]" in result["subject"]

def test_simple_add_new_file():
    diff = """diff --git a/new_file.py b/new_file.py
new file mode 100644
--- /dev/null
+++ b/new_file.py
@@ -0,0 +1 @@
+print("hello")
"""
    result = create_commit_message(diff)
    assert "[ADD]" in result["subject"]
    assert "Add new_file" in result["subject"]
    assert "Python" in result["display"]  # Language detection

def test_simple_delete_file():
    diff = """diff --git a/old_file.py b/old_file.py
deleted file mode 100644
--- a/old_file.py
+++ /dev/null
@@ -1 +0,0 @@
-print("hello")
"""
    result = create_commit_message(diff)
    assert "[REMOVE]" in result["subject"]
    assert "Remove old_file" in result["subject"]

def test_rename_file():
    diff = """diff --git a/old.py b/new.py
similarity index 100%
rename from old.py
rename to new.py
"""
    result = create_commit_message(diff)
    assert "[RENAME]" in result["subject"]
    assert "Rename old → new" in result["subject"]

def test_binary_file():
    diff = """diff --git a/image.png b/image.png
Binary files a/image.png and b/image.png differ
"""
    result = create_commit_message(diff)
    assert "[UPDATE]" in result["subject"]
    assert "binary asset" in result["subject"]

def test_test_file_add():
    diff = """diff --git a/tests/test_foo.py b/tests/test_foo.py
new file mode 100644
--- /dev/null
+++ b/tests/test_foo.py
@@ -0,0 +1 @@
+def test_foo(): pass
"""
    result = create_commit_message(diff)
    assert "[TEST]" in result["subject"]
    assert "Add tests for test_foo" in result["subject"]

def test_docs_update():
    diff = """diff --git a/README.md b/README.md
index 123..456
--- a/README.md
+++ b/README.md
@@ -1 +1,2 @@
 # Project
+New docs
"""
    result = create_commit_message(diff)
    assert "[DOCS]" in result["subject"]
    assert "Update README documentation" in result["subject"]

def test_config_update_deps():
    diff = """diff --git a/requirements.txt b/requirements.txt
index 123..456
--- a/requirements.txt
+++ b/requirements.txt
@@ -1 +1,2 @@
 numpy==1.0
+pandas==2.0
"""
    result = create_commit_message(diff)
    assert "[CONFIG]" in result["subject"]
    assert "dependencies" in result["subject"]
    assert any("pandas" in d for d in result["display"].splitlines())  # Check details

def test_style_update():
    diff = """diff --git a/style.css b/style.css
index 123..456
--- a/style.css
+++ b/style.css
@@ -1 +1,2 @@
 .class { color: red; }
+.new { font-size: 12px; }
"""
    result = create_commit_message(diff)
    assert "[STYLE]" in result["subject"]
    assert "Update style styles" in result["subject"] or "selectors" in result["display"]

def test_markup_update():
    diff = """diff --git a/template.html b/template.html
index 123..456
--- a/template.html
+++ b/template.html
@@ -1 +1 @@
-<div>old</div>
+<div>new <field name="foo"/></div>
"""
    result = create_commit_message(diff)
    assert "[UPDATE]" in result["subject"]
    assert "template" in result["subject"]

def test_sql_update():
    diff = """diff --git a/query.sql b/query.sql
index 123..456
--- a/query.sql
+++ b/query.sql
@@ -1 +1 @@
-SELECT * FROM users
+INSERT INTO users (name) VALUES ('foo')
"""
    result = create_commit_message(diff)
    assert "[UPDATE]" in result["subject"]
    assert "SQL query" in result["subject"]

def test_fix_with_error_handling():
    diff = """diff --git a/app.py b/app.py
index 123..456
--- a/app.py
+++ b/app.py
@@ -1,2 +1,4 @@
 def foo():
     x = None
-    print(x.y)
+    try:
+        print(x.y)
+    except AttributeError:
+        pass
"""
    result = create_commit_message(diff)
    assert "[FIX]" in result["subject"]
    assert "handling" in result["subject"]

def test_feat_new_def():
    diff = """diff --git a/app.js b/app.js
index 123..456
--- a/app.js
+++ b/app.js
@@ -0,0 +1 @@
+function newFeature() { console.log('new'); }
"""
    result = create_commit_message(diff)
    assert "[ADD]" in result["subject"]
    assert "newFeature" in result["subject"]

def test_refactor_balanced():
    diff = """diff --git a/app.go b/app.go
index 123..456
--- a/app.go
+++ b/app.go
@@ -1,25 +1,25 @@
-old line
+new line
""" * 25  # Simulate large balanced change
    result = create_commit_message(diff)
    assert "[REFACTOR]" in result["subject"] or "[UPDATE]" in result["subject"]  # Depending on exact count

def test_update_generic():
    diff = """diff --git a/script.sh b/script.sh
index 123..456
--- a/script.sh
+++ b/script.sh
@@ -1 +1 @@
-echo "old"
+echo "new"
"""
    result = create_commit_message(diff)
    assert "[UPDATE]" in result["subject"]
    assert "Update script" in result["subject"]

def test_multiple_files():
    diff = """diff --git a/file1.py b/file1.py
new file mode 100644
--- /dev/null
+++ b/file1.py
@@ -0,0 +1 @@
+print(1)
diff --git a/file2.js b/file2.js
new file mode 100644
--- /dev/null
+++ b/file2.js
@@ -0,0 +1 @@
+console.log(2)
"""
    result = create_commit_message(diff)
    assert "(+1 more)" in result["subject"]
    assert len(result["_files"]) == 2

def test_unicode_no_crash():
    diff = """diff --git a/file.txt b/file.txt
index 123..456
--- a/file.txt
+++ b/file.txt
@@ -1 +1 @@
-hello 🌍
+hello 🪐
"""
    result = create_commit_message(diff)
    assert isinstance(result["subject"], str)
    assert "Update file" in result["subject"]

def test_malformed_diff_no_crash():
    diff = "invalid diff content"
    result = create_commit_message(diff)
    assert "Minor changes" in result["subject"]

def test_large_diff_no_crash():
    large_diff = "diff --git a/large.py b/large.py\n" + "@@ -0,0 +1,1000 @@\n" + "".join(f"+line {i}\n" for i in range(1000))
    result = create_commit_message(large_diff)
    assert result  # No crash

def test_various_languages():
    langs = [
        (".py", "Python", "🐍"),
        (".js", "JavaScript", "🟨"),
        (".ts", "TypeScript", "🔷"),
        (".java", "Java", "☕"),
        (".go", "Go", "🐹"),
        (".rs", "Rust", "🦀"),
        (".php", "PHP", "🐘"),
        (".rb", "Ruby", "💎"),
        (".swift", "Swift", "🦅"),
        (".kt", "Kotlin", "🎯"),
        (".sql", "SQL", "🗄"),
        (".html", "HTML", "🌐"),
        (".css", "CSS", "🎨"),
        (".md", "Markdown", "📝"),
        (".yaml", "YAML", "⚙"),
        (".gitignore", "Git", "📄"),
        ("LICENSE", "LICENSE", "📄"),
    ]
    for ext, expected_lang, icon in langs:
        path = ext if ext in ("LICENSE", ".gitignore") else "file" + ext
        diff = f"""diff --git a/{path} b/{path}
new file mode 100644
--- /dev/null
+++ b/{path}
@@ -0,0 +1 @@
+content
"""
        result = create_commit_message(diff)
        assert expected_lang in result["display"], f"Failed on {ext}: expected {expected_lang} in dict"
        assert icon in result["display"]

def test_scope_detection_python():
    fd = make_fd("app.py", added=["def my_func(): pass"], hunk_ctx=["def my_func():"])
    scope = detect_scope(fd)
    assert scope == "my_func"

def test_scope_detection_js():
    fd = make_fd("app.js", added=["function myFunc() {}"])
    scope = detect_scope(fd)
    assert scope == "myFunc"

def test_fix_score_threshold():
    # Low score - not fix
    fd = make_fd("app.py", added=["print('fix')"])  # Keyword but not in added strongly
    assert classify(fd) == "update"

    # High score - fix
    fd = make_fd("app.py", added=["try: pass", "except: pass"])
    assert classify(fd) == "fix"

def test_details_config_deps():
    fd = make_fd("requirements.txt", added=["pandas==1.0"], ctype="config")
    details = extract_details(fd, "config")
    assert any("pandas" in d for d in details)

def test_details_sql():
    fd = make_fd("query.sql", added=["INSERT INTO users VALUES (1)"])
    details = extract_details(fd, "sql")
    assert any("ops: INSERT" in d for d in details)
    assert any("tables: users" in d for d in details)

def test_branch_inclusion():
    diff = """diff --git a/file.py b/file.py
new file mode 100644
--- /dev/null
+++ b/file.py
@@ -0,0 +1 @@
+print("hello")
"""
    result = create_commit_message(diff, branch="feature")
    assert "[feature]" in result["subject"]

def test_invalid_path_language():
    fd = make_fd("unknown.ext")
    assert language(fd["path"]) == ""  # No crash

def test_skip_names_in_defs():
    fd = make_fd("app.py", added=["def if(): pass"])  # Invalid but skip
    names = find_defined_names(fd["added"])
    assert not names  # Skipped 'if'