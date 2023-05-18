"""В этом модуле находится код генерирования документации."""
import ast
import os


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


def get_prog_elems(file: str) -> list[tuple[str, str, str | None]]:
    """Возвращает все элементы программы (функции, классы, методы)."""
    body = ast.parse(open(file, encoding='utf-8').read()).body
    result = []
    for elem in body:
        match elem:
            case ast.FunctionDef():
                result.append(_handle_func(elem))
    return result


def _handle_func(elem: ast.FunctionDef) -> tuple[str, str, str | None]:
    """
    Возвращает кортеж из типа элемента (здесь всегда `'func'`),
    сигнатуры и строки документации (может быть `None`).
    """
    args = elem.args
    pos_only_args = [f'{arg.arg}' +
                     f'{(": " + ast.unparse(arg.annotation)) if arg.annotation else ""}'
                     for arg in args.posonlyargs]
    other_args = [f'{arg.arg}' +
                  f'{(": " + ast.unparse(arg.annotation)) if arg.annotation else ""}'
                  for arg in args.args]
    kw_only_args = [f'{arg.arg}' +
                    f'{(": " + ast.unparse(arg.annotation)) if arg.annotation else ""}'
                    for arg in args.kwonlyargs]
    return (
            'func',
            f'{elem.name}({", ".join(pos_only_args)}{"/, " if pos_only_args else ""}' +
            f'{", ".join(other_args)}{", " if kw_only_args else ""}' +
            f'{"*, " if kw_only_args else ""}{", ".join(kw_only_args)})' +
            f'{(" -> " + ast.unparse(elem.returns)) if elem.returns else ""}',
            ast.get_docstring(elem)
           )
