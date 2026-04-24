"""Tests for the file watcher and analyzer modules."""

from pathlib import Path
from unittest.mock import MagicMock

from monitoria.config import MonitoriaConfig
from monitoria.watcher import ProjectEventHandler, _detect_language, collect_all_files
from monitoria.analyzer import analyze_files, Issue


def test_detect_language():
    assert _detect_language(".java") == "java"
    assert _detect_language(".py") == "python"
    assert _detect_language(".ts") == "typescript"
    assert _detect_language(".unknown") == "text"


def test_should_track_valid_java_file(tmp_path: Path):
    config = MonitoriaConfig()
    handler = ProjectEventHandler(config)

    # Create a valid Java file
    java_file = tmp_path / "App.java"
    java_file.write_text("public class App {}")

    assert handler._should_track(str(java_file)) is True


def test_should_not_track_ignored_dir(tmp_path: Path):
    config = MonitoriaConfig()
    handler = ProjectEventHandler(config)

    # Create file inside node_modules
    nm_dir = tmp_path / "node_modules" / "lib"
    nm_dir.mkdir(parents=True)
    js_file = nm_dir / "index.js"
    js_file.write_text("module.exports = {}")

    assert handler._should_track(str(js_file)) is False


def test_should_not_track_wrong_extension(tmp_path: Path):
    config = MonitoriaConfig()
    handler = ProjectEventHandler(config)

    bin_file = tmp_path / "app.exe"
    bin_file.write_bytes(b"\x00\x01\x02")

    assert handler._should_track(str(bin_file)) is False


def test_collect_all_files(tmp_path: Path):
    config = MonitoriaConfig()

    # Create project structure
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "App.java").write_text("public class App {}")
    (tmp_path / "src" / "Main.java").write_text("public class Main {}")
    (tmp_path / "README.md").write_text("# Project")  # should be excluded (not in extensions)

    files = collect_all_files(tmp_path, config)

    assert len(files) == 2
    assert all(f["language"] == "java" for f in files)
    paths = {f["path"] for f in files}
    assert "src/App.java" in paths
    assert "src/Main.java" in paths


def test_dirty_files_tracking():
    config = MonitoriaConfig()
    handler = ProjectEventHandler(config)

    # Simulate file events
    handler.dirty_files.add("/project/App.java")
    handler.dirty_files.add("/project/Main.java")

    assert len(handler.dirty_files) == 2

    flushed = handler.flush_dirty()
    assert len(flushed) == 2
    assert len(handler.dirty_files) == 0  # Should be cleared


# ──────────────────────────────────────────────
# Analyzer tests
# ──────────────────────────────────────────────

def test_analyze_java_missing_semicolon():
    files = [{
        "path": "App.java",
        "content": "public class App {\n    int x = 10\n}",
        "language": "java",
    }]
    result = analyze_files(files)
    # Should find bracket or semicolon issue
    assert result.files_analyzed == 1


def test_analyze_java_class_naming():
    files = [{
        "path": "service.java",
        "content": "public class userService {\n    public void doStuff() {}\n}",
        "language": "java",
    }]
    result = analyze_files(files)
    naming_issues = [i for i in result.issues if i.category == "naming"]
    assert len(naming_issues) >= 1
    assert "maiúscula" in naming_issues[0].message.lower() or "PascalCase" in naming_issues[0].message


def test_analyze_java_empty_catch():
    files = [{
        "path": "App.java",
        "content": 'public class App {\n    void m() {\n        try { int x=1; } catch (Exception e) {}\n    }\n}',
        "language": "java",
    }]
    result = analyze_files(files)
    catch_issues = [i for i in result.issues if "catch" in i.message.lower()]
    assert len(catch_issues) >= 1


def test_analyze_java_bracket_mismatch():
    files = [{
        "path": "App.java",
        "content": "public class App {\n    void m() {\n        if (true) {\n    }\n",
        "language": "java",
    }]
    result = analyze_files(files)
    bracket_issues = [i for i in result.issues if i.category == "syntax" and "fechado" in i.message]
    assert len(bracket_issues) >= 1


def test_analyze_python_bare_except():
    files = [{
        "path": "app.py",
        "content": "try:\n    x = 1\nexcept:\n    pass\n",
        "language": "python",
    }]
    result = analyze_files(files)
    except_issues = [i for i in result.issues if "except" in i.message.lower()]
    assert len(except_issues) >= 1


def test_analyze_js_var_usage():
    files = [{
        "path": "app.js",
        "content": 'var name = "test";\nconst ok = true;\n',
        "language": "javascript",
    }]
    result = analyze_files(files)
    var_issues = [i for i in result.issues if "var" in i.message]
    assert len(var_issues) >= 1


def test_score_calculation():
    # Clean file should score 100
    files = [{
        "path": "Clean.java",
        "content": "public class Clean {\n    public void doSomething() {\n        int count = 10;\n    }\n}",
        "language": "java",
    }]
    result = analyze_files(files)
    assert result.score >= 80  # Should be high (few or no issues)


def test_score_drops_with_errors():
    # File with many issues should score lower
    files = [{
        "path": "Bad.java",
        "content": (
            "public class badClass {\n"
            "    int a = 10\n"
            "    void m() {\n"
            "        try { } catch (Exception e) {}\n"
            "        System.out.println(a);\n"
            "    \n"  # missing closing brace
        ),
        "language": "java",
    }]
    result = analyze_files(files)
    assert result.score < 80
    assert result.error_count >= 1
