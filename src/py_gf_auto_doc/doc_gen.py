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


def get_prog_elems(code: str) -> list[tuple[str, str, str | None]]:
    """Возвращает все элементы программы (функции, классы, методы)."""
    body = ast.parse(code).body
    result = []
    for elem in body:
        match elem:
            case ast.FunctionDef():
                signature = ast.unparse(elem).splitlines()[0][4:-1]
                if (not signature.startswith('_')) or signature.startswith('__'):
                    result.append(('func', signature,
                                   ast.get_docstring(elem)))
    return result
