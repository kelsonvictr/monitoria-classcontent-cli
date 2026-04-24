"""Local code analyzer — offline syntax checking without API.

Provides basic syntax/pattern analysis using regex and heuristics.
This is the offline fallback when the API is not available.
For full AI analysis, the backend worker uses Claude Haiku.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Issue:
    """A code issue found by the analyzer."""

    file: str
    line: int
    severity: str  # "error" | "warning" | "info"
    category: str  # "syntax" | "naming" | "pattern" | "style"
    message: str
    suggestion: str = ""


@dataclass
class AnalysisResult:
    """Result of analyzing all files."""

    issues: list[Issue] = field(default_factory=list)
    score: int = 100
    files_analyzed: int = 0
    total_lines: int = 0

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "error")

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "warning")

    @property
    def info_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == "info")


def analyze_files(files: list[dict]) -> AnalysisResult:
    """Analyze a list of file dicts and return issues found.

    Each file dict: {"path": str, "content": str, "language": str}
    """
    result = AnalysisResult(files_analyzed=len(files))

    for f in files:
        content = f["content"]
        lang = f["language"]
        path = f["path"]
        lines = content.split("\n")
        result.total_lines += len(lines)

        if lang == "java":
            result.issues.extend(_analyze_java(path, content, lines))
        elif lang == "python":
            result.issues.extend(_analyze_python(path, content, lines))
        elif lang in ("javascript", "typescript"):
            result.issues.extend(_analyze_js_ts(path, content, lines))

        # Language-agnostic checks
        result.issues.extend(_analyze_generic(path, content, lines))

    # Calculate score
    penalty = (
        result.error_count * 10
        + result.warning_count * 3
        + result.info_count * 1
    )
    result.score = max(0, 100 - penalty)

    return result


# ──────────────────────────────────────────────
# Java analyzer
# ──────────────────────────────────────────────

def _analyze_java(path: str, content: str, lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []

    # 1. Bracket matching
    issues.extend(_check_brackets(path, content, lines, "{", "}"))
    issues.extend(_check_brackets(path, content, lines, "(", ")"))

    # 2. Missing semicolons (simple heuristic)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
            continue
        # Lines that should end with ;
        if (
            re.match(r'^(return |System\.|int |String |double |float |boolean |long |char |var |final )', stripped)
            and not stripped.endswith(";")
            and not stripped.endswith("{")
            and not stripped.endswith("}")
            and not stripped.endswith(",")
            and "{" not in stripped
        ):
            issues.append(Issue(
                file=path, line=i, severity="error", category="syntax",
                message=f"Possível ';' faltando no final da linha",
                suggestion="Adicione ';' ao final desta linha",
            ))

    # 3. Class naming convention
    class_matches = re.finditer(r'class\s+([a-z]\w*)', content)
    for m in class_matches:
        line_num = content[:m.start()].count("\n") + 1
        issues.append(Issue(
            file=path, line=line_num, severity="warning", category="naming",
            message=f"Nome de classe '{m.group(1)}' deve começar com maiúscula (PascalCase)",
            suggestion=f"Renomeie para '{m.group(1)[0].upper() + m.group(1)[1:]}'",
        ))

    # 4. Variable naming — single letter (except i, j, k in loops)
    var_pattern = re.compile(r'(?:int|String|double|float|boolean|long|char|var)\s+([a-zA-Z])\s*[=;]')
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("for") or stripped.startswith("//"):
            continue
        m = var_pattern.search(stripped)
        if m and m.group(1) not in ("i", "j", "k", "e", "x", "y"):
            issues.append(Issue(
                file=path, line=i, severity="warning", category="naming",
                message=f"Variável '{m.group(1)}' — nome muito curto, use algo descritivo",
                suggestion="Use um nome que descreva o propósito (ex: count, name, value)",
            ))

    # 5. Empty catch blocks
    catch_pattern = re.compile(r'catch\s*\([^)]*\)\s*\{\s*\}')
    for m in catch_pattern.finditer(content):
        line_num = content[:m.start()].count("\n") + 1
        issues.append(Issue(
            file=path, line=line_num, severity="warning", category="pattern",
            message="Bloco catch vazio — exceção engolida silenciosamente",
            suggestion="Adicione pelo menos um log: e.printStackTrace() ou logger.error()",
        ))

    # 6. System.out.println in non-Main classes
    if "Main" not in path and "Test" not in path:
        for i, line in enumerate(lines, 1):
            if "System.out.println" in line and not line.strip().startswith("//"):
                issues.append(Issue(
                    file=path, line=i, severity="info", category="pattern",
                    message="System.out.println — considere usar um Logger",
                    suggestion="Use SLF4J/Log4j: logger.info() em vez de System.out.println()",
                ))

    return issues


# ──────────────────────────────────────────────
# Python analyzer
# ──────────────────────────────────────────────

def _analyze_python(path: str, content: str, lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []

    # 1. Indentation consistency
    indent_sizes = set()
    for i, line in enumerate(lines, 1):
        if line and not line.strip().startswith("#") and line[0] == " ":
            spaces = len(line) - len(line.lstrip())
            if spaces > 0:
                indent_sizes.add(spaces)

    # Check for mixed indentation
    has_tabs = any("\t" in line for line in lines)
    has_spaces = any(line.startswith(" ") for line in lines if line.strip())
    if has_tabs and has_spaces:
        issues.append(Issue(
            file=path, line=1, severity="error", category="style",
            message="Indentação mista: tabs E espaços no mesmo arquivo",
            suggestion="Use apenas espaços (4 por nível) — padrão PEP8",
        ))

    # 2. Bracket matching
    issues.extend(_check_brackets(path, content, lines, "(", ")"))
    issues.extend(_check_brackets(path, content, lines, "[", "]"))
    issues.extend(_check_brackets(path, content, lines, "{", "}"))

    # 3. Missing colon after def/class/if/for/while
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if re.match(r'^(def |class |if |elif |else|for |while |try|except|finally|with )', stripped):
            # Check if this line or continuation ends with :
            if not stripped.endswith(":") and not stripped.endswith(":\\"):
                # Could be multi-line — only flag if it looks complete
                if "(" not in stripped or ("(" in stripped and ")" in stripped):
                    issues.append(Issue(
                        file=path, line=i, severity="error", category="syntax",
                        message=f"Possível ':' faltando no final da declaração",
                        suggestion="Adicione ':' ao final desta linha",
                    ))

    # 4. Variable naming — CamelCase in Python (should be snake_case)
    var_pattern = re.compile(r'^(\s*)([a-z]+[A-Z]\w*)\s*=')
    for i, line in enumerate(lines, 1):
        m = var_pattern.match(line)
        if m and not line.strip().startswith("#"):
            name = m.group(2)
            snake = re.sub(r'([A-Z])', r'_\1', name).lower()
            issues.append(Issue(
                file=path, line=i, severity="info", category="naming",
                message=f"Variável '{name}' usa camelCase — Python usa snake_case (PEP8)",
                suggestion=f"Renomeie para '{snake}'",
            ))

    # 5. Bare except
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == "except:" or stripped == "except :":
            issues.append(Issue(
                file=path, line=i, severity="warning", category="pattern",
                message="'except:' genérico — captura todas as exceções (inclusive SystemExit, KeyboardInterrupt)",
                suggestion="Use 'except Exception:' ou uma exceção específica",
            ))

    return issues


# ──────────────────────────────────────────────
# JavaScript/TypeScript analyzer
# ──────────────────────────────────────────────

def _analyze_js_ts(path: str, content: str, lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []

    # 1. Bracket matching
    issues.extend(_check_brackets(path, content, lines, "{", "}"))
    issues.extend(_check_brackets(path, content, lines, "(", ")"))
    issues.extend(_check_brackets(path, content, lines, "[", "]"))

    # 2. var usage (should be let/const)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if re.match(r'^var\s+', stripped) and not stripped.startswith("//"):
            issues.append(Issue(
                file=path, line=i, severity="warning", category="pattern",
                message="'var' está obsoleto — use 'let' ou 'const'",
                suggestion="Troque 'var' por 'const' (se não reatribuir) ou 'let'",
            ))

    # 3. console.log left behind
    if "test" not in path.lower() and "spec" not in path.lower():
        for i, line in enumerate(lines, 1):
            if "console.log(" in line and not line.strip().startswith("//"):
                issues.append(Issue(
                    file=path, line=i, severity="info", category="pattern",
                    message="console.log() encontrado — remova antes de entregar",
                    suggestion="Remova ou substitua por um logger apropriado",
                ))

    # 4. == instead of === (JS)
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        # Match == but not ===
        if re.search(r'[^!=]==[^=]', stripped):
            issues.append(Issue(
                file=path, line=i, severity="warning", category="pattern",
                message="'==' faz coerção de tipo — prefira '===' (comparação estrita)",
                suggestion="Troque '==' por '===' para comparação segura",
            ))

    return issues


# ──────────────────────────────────────────────
# Generic (all languages)
# ──────────────────────────────────────────────

def _analyze_generic(path: str, content: str, lines: list[str]) -> list[Issue]:
    issues: list[Issue] = []

    # 1. Very long lines (>150 chars)
    for i, line in enumerate(lines, 1):
        if len(line) > 150:
            issues.append(Issue(
                file=path, line=i, severity="info", category="style",
                message=f"Linha muito longa ({len(line)} caracteres) — difícil de ler",
                suggestion="Quebre a linha em múltiplas linhas (máx ~120 caracteres)",
            ))

    # 2. TODO/FIXME/HACK comments
    for i, line in enumerate(lines, 1):
        if re.search(r'\b(TODO|FIXME|HACK|XXX)\b', line):
            issues.append(Issue(
                file=path, line=i, severity="info", category="pattern",
                message=f"Comentário pendente encontrado — resolver antes de entregar",
                suggestion="Resolva o TODO/FIXME ou remova se já resolvido",
            ))

    # 3. Trailing whitespace
    trailing_count = sum(1 for line in lines if line != line.rstrip())
    if trailing_count > 5:
        issues.append(Issue(
            file=path, line=1, severity="info", category="style",
            message=f"{trailing_count} linhas com espaços em branco no final",
            suggestion="Configure seu editor para remover trailing whitespace ao salvar",
        ))

    return issues


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _check_brackets(path: str, content: str, lines: list[str], open_b: str, close_b: str) -> list[Issue]:
    """Check for mismatched brackets, ignoring strings and comments."""
    issues: list[Issue] = []
    stack: list[tuple[int, int]] = []  # (line_number, char_position)

    in_string = False
    string_char = ""
    in_line_comment = False
    in_block_comment = False

    for i, line in enumerate(lines, 1):
        in_line_comment = False
        for j, ch in enumerate(line):
            # Track string state
            if not in_line_comment and not in_block_comment:
                if ch in ('"', "'", "`") and (j == 0 or line[j - 1] != "\\"):
                    if in_string and ch == string_char:
                        in_string = False
                    elif not in_string:
                        in_string = True
                        string_char = ch

            if in_string:
                continue

            # Track comment state
            if not in_block_comment and j < len(line) - 1:
                if line[j:j + 2] == "//":
                    in_line_comment = True
                elif line[j:j + 2] == "/*":
                    in_block_comment = True
            if in_block_comment and j > 0 and line[j - 1:j + 1] == "*/":
                in_block_comment = False
                continue

            if in_line_comment or in_block_comment:
                continue

            if ch == open_b:
                stack.append((i, j))
            elif ch == close_b:
                if stack:
                    stack.pop()
                else:
                    issues.append(Issue(
                        file=path, line=i, severity="error", category="syntax",
                        message=f"'{close_b}' extra sem '{open_b}' correspondente",
                        suggestion=f"Remova o '{close_b}' ou adicione o '{open_b}' que falta",
                    ))

    for line_num, _ in stack:
        issues.append(Issue(
            file=path, line=line_num, severity="error", category="syntax",
            message=f"'{open_b}' aberto na linha {line_num} nunca foi fechado com '{close_b}'",
            suggestion=f"Adicione '{close_b}' no local correto",
        ))

    return issues
