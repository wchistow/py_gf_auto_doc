"""В этом модуле находится код генерирования документации."""
import ast
from typing import TypeAlias
import os

FuncT: TypeAlias = tuple[str, str, str | None]
ClassT: TypeAlias = tuple[str, str, str | None, list[FuncT]]


def generate_doc(path: str):
    """Главная функция генерирования документации."""
    files = get_py_files(path)
    print(files)


def get_py_files(path: str) -> list[str | list]:
    """Возвращает список файлов с расширением `.py`."""
    result: list[str | list] = []
    for item in os.listdir(path):
        if os.path.isfile(item) and item.endswith('.py'):
            result.append(item)
        elif os.path.isdir(item):
            inner_result = get_py_files(item)
            if inner_result:  # Если во вложенной папке есть файлы `.py`.
                result.append(inner_result)
    return result


def get_prog_elems(code: str) -> list[FuncT | ClassT]:
    """Возвращает все элементы программы (функции, классы, методы)."""
    body = ast.parse(code).body
    result: list[FuncT | ClassT] = []
    for elem in body:
        match elem:
            case ast.FunctionDef():
                signature = ast.unparse(elem).splitlines()[0][4:-1]
                if (not signature.startswith('_')) or \
                        (signature.startswith('__') and signature.endswith('__')):
                    result.append(('func', signature,
                                   ast.get_docstring(elem)))
            case ast.ClassDef():
                signature = ast.unparse(elem).splitlines()[0][6:-1]
                if not signature.startswith('_'):
                    attrs = []
                    for node in elem.body:
                        match node:
                            case ast.FunctionDef():
                                meth_signature = ast.unparse(node).splitlines()[0][4:-1]
                                if (not signature.startswith('_')) or \
                                        (signature.startswith('__') and signature.endswith('__')):
                                    attrs.append(('meth', meth_signature, ast.get_docstring(node)))

                    result.append(('class', signature, ast.get_docstring(elem), attrs))
    return result
