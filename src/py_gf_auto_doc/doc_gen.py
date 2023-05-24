"""В этом модуле находится код генерирования документации."""
import ast
from collections.abc import Iterable
from typing import TypeAlias
import os

FuncT: TypeAlias = tuple[str, str, str, str | None]
ClassT: TypeAlias = tuple[str, str, str | None, list[FuncT]]

BASE_PATH = os.path.dirname(__file__)

FILE_TEMPLATE = open(f'{BASE_PATH}/templates/file.txt', encoding='utf-8').read()
FUNC_TEMPLATE = open(f'{BASE_PATH}/templates/func.txt', encoding='utf-8').read()
CLASS_TEMPLATE = open(f'{BASE_PATH}/templates/class.txt', encoding='utf-8').read()


def generate_doc(path: str, out_dir: str) -> None:
    """Главная функция генерирования документации."""
    if not os.path.exists(out_dir):
        raise FileNotFoundError(f'Каталог {out_dir} не существует.')
    path = os.path.abspath(path)

    _generate_doc(path, out_dir)

    with open(os.path.join(out_dir, 'README.md'), 'w', encoding='utf-8') as f:
        f.write('> Эта документация сгенерирована утилитой `py_gf_auto_doc`.\n')


def _generate_doc(path: str, out_dir: str, inner_dir: str = ''):
    """Основная логика генерирования документации."""
    if inner_dir and not os.path.exists(os.path.join(out_dir, inner_dir)):
        os.mkdir(os.path.join(out_dir, inner_dir))

    for py_file in get_py_files(os.path.join(path, inner_dir)):
        py_objs = get_prog_elems(open(os.path.join(path, os.path.join(inner_dir, py_file)),
                                      encoding='utf-8').read())

        classes = _get_classes_templates(filter(lambda elem: elem[0] == 'class', py_objs))  # type: ignore[arg-type]
        funcs = _get_funcs_templates(filter(lambda elem: elem[0] == 'func', py_objs))  # type: ignore[arg-type]

        out_text = FILE_TEMPLATE.format(filename=py_file,
                                        classes='\n'.join(classes),
                                        funcs='\n'.join(funcs))

        with open(os.path.join(os.path.join(out_dir, inner_dir),
                               '.'.join(py_file.split('.')[:-1])) + '.md',
                  'w', encoding='utf-8') as f:
            f.write(out_text)

    for directory in (item for item in os.listdir(path)
                      if os.path.isdir(os.path.join(path, os.path.join(inner_dir, item)))
                      and item != '.'):
        _generate_doc(path, out_dir, os.path.join(inner_dir, directory))

    _clean_empty_dirs(out_dir)


def _get_classes_templates(classes: Iterable[ClassT]) -> list[str]:
    result = []
    for typ, signature, docstring, meths in classes:
        meths_templates = []
        for _, meth_name, meth_signature, meth_docstring in meths:
            meths_templates.append(FUNC_TEMPLATE.format(name=meth_name,
                                                        signature=meth_signature,
                                                        docstring=meth_docstring or ''
                                                        )
                                   )
        class_template = CLASS_TEMPLATE.format(signature=signature,
                                               docstring=docstring or '',
                                               meths='\n'.join(meths_templates))
        result.append(class_template)
    return result


def _get_funcs_templates(funcs: Iterable[FuncT]) -> list[str]:
    result = []
    for typ, name, signature, docstring in funcs:
        func_template = FUNC_TEMPLATE.format(name=name,
                                             signature=signature,
                                             docstring=docstring or '')
        result.append(func_template)
    return result


def _clean_empty_dirs(path: str) -> None:
    """Рекурсивно обходит дерево каталогов, начиная с `path`, удаляя все пустые каталоги."""
    for item in os.listdir(path):
        if os.path.isdir(os.path.join(path, item)):
            if len(os.listdir(os.path.join(path, item))) == 0:
                os.rmdir(os.path.join(path, item))
            else:
                _clean_empty_dirs(os.path.join(path, item))


def get_py_files(path: str) -> list[str]:
    """Возвращает список файлов с расширением `.py`."""
    result: list[str] = []
    for item in os.listdir(path):
        if os.path.isfile(os.path.join(path, item)) and item.endswith('.py'):
            result.append(item)
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
                    result.append(('func', elem.name, signature,
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
                                    attrs.append(('meth', node.name, meth_signature,
                                                  ast.get_docstring(node)))

                    result.append(('class', signature, ast.get_docstring(elem), attrs))
    return result
