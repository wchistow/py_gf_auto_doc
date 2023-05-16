import os


def generate_doc(path: str):
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
