"""파일 길이와 설명서 형식이 이후 변경에서도 유지되는지 검사한다."""

import ast
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def python_sources():
    """프로젝트가 관리하는 Python 파일만 모은다.

    Args:
        없음.

    Returns:
        list[Path]: 가상환경을 제외한 app, scripts, tests의 Python 파일 목록.
    """
    return [
        path
        for folder in ("app", "scripts", "tests")
        for path in (PROJECT_ROOT / folder).rglob("*.py")
    ]


def test_each_python_file_has_at_most_250_lines():
    """빈 줄과 docstring을 포함해 파일당 250줄 제한을 검사한다.

    Args:
        없음.

    Returns:
        None: 길이 제한을 넘는 파일이 있으면 assertion으로 경로와 줄 수를 표시한다.
    """
    oversized = {
        str(path.relative_to(PROJECT_ROOT)): len(path.read_text().splitlines())
        for path in python_sources()
        if len(path.read_text().splitlines()) > 250
    }
    assert not oversized, oversized


def test_classes_and_functions_document_parameters_and_returns():
    """모든 클래스·함수의 역할, 파라미터와 반환값 설명을 확인한다.

    Args:
        없음.

    Returns:
        None: 설명이 누락되면 해당 파일과 선언문의 이름을 표시한다.
    """
    missing = []
    for path in python_sources():
        for node in ast.walk(ast.parse(path.read_text())):
            if not isinstance(
                node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)
            ):
                continue
            doc = ast.get_docstring(node) or ""
            label = f"{path.relative_to(PROJECT_ROOT)}:{node.lineno} {node.name}"
            if not doc.splitlines() or "Args:" not in doc or "Returns:" not in doc:
                missing.append(label)
                continue
            if isinstance(node, ast.ClassDef):
                continue
            arguments = node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            arguments += [arg for arg in (node.args.vararg, node.args.kwarg) if arg]
            args_section = doc.split("Args:", 1)[1].split("Returns:", 1)[0]
            for argument in arguments:
                if argument.arg in {"self", "cls"}:
                    continue
                if not re.search(
                    rf"^\s+{re.escape(argument.arg)}(?:\s|:)", args_section, re.M
                ):
                    missing.append(f"{label}: {argument.arg}")
    assert not missing, missing
