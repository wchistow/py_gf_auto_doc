"""В этом модуле находится код генерирования документации."""
import ast
from collections.abc import Iterable
from pathlib import Path
from typing import TypeAlias
import os

FuncT: TypeAlias = tuple[str, str, str, str | None]
ClassT: TypeAlias = tuple[str, str, str | None, list[FuncT]]

BASE_PATH = os.path.dirname(__file__)

with open(f'{BASE_PATH}/templates/file.txt', encoding='utf-8') as f:
    FILE_TEMPLATE = f.read()
with open(f'{BASE_PATH}/templates/func.txt', encoding='utf-8') as f:
    FUNC_TEMPLATE = f.read()
with open(f'{BASE_PATH}/templates/class.txt', encoding='utf-8') as f:
    CLASS_TEMPLATE = f.read()


def generate_doc(path: str, out_dir: str) -> None:
    """Главная функция генерирования документации."""
    if not os.path.exists(out_dir):
        raise FileNotFoundError(f'Каталог {out_dir} не существует.')
    path = os.path.abspath(path)

    summary = '\n'.join(_generate_doc(path, out_dir))

    with open(os.path.join(out_dir, 'README.md'), 'w', encoding='utf-8') as readme:
        readme.write('> Эта документация сгенерирована утилитой `py_gf_auto_doc`.\n')

    with open(os.path.join(out_dir, 'SUMMARY.md'), 'w', encoding='utf-8') as summ:
        summ.write(summary)


def _generate_doc(path: str, out_dir: str, inner_dir: str = '') -> list[str]:
    """Основная логика генерирования документации."""
    summary: list[str] = []
    indent = ' ' * (4 * len(Path(inner_dir).parents))

    if inner_dir and not os.path.exists(os.path.join(out_dir, inner_dir)):
        os.mkdir(os.path.join(out_dir, inner_dir))

    for py_file in get_py_files(os.path.join(path, inner_dir)):
        with open(os.path.join(path, inner_dir, py_file), encoding='utf-8') as py_f:
            py_objs = get_prog_elems(py_f.read())

        classes = '\n'.join(_get_classes_templates(
            filter(lambda elem: elem[0] == 'class', py_objs)))  # type: ignore[arg-type]
        funcs = '\n'.join(_get_funcs_templates(
            filter(lambda elem: elem[0] == 'func', py_objs)))  # type: ignore[arg-type]

        out_text = FILE_TEMPLATE.format(filename=py_file,
                                        classes=classes or '*Нет классов*',
                                        funcs=funcs or '*Нет функций*'
                                        )

        filename = '.'.join(py_file.split('.')[:-1])

        with open(os.path.join(out_dir, inner_dir, filename + '.md'),
                  'w', encoding='utf-8') as result:
            result.write(out_text)

        summary.append(f'{indent}* [{filename}]({os.path.join(inner_dir, filename + ".md")})')

    for directory in (item for item in os.listdir(path)
                      if os.path.isdir(os.path.join(path, inner_dir, item))
                      and item != '.'):
        if len(get_py_files(os.path.join(path, inner_dir, directory))) != 0:
            summary.append(f'{indent}* [{directory}]()')
            summary.extend(_generate_doc(path, out_dir, os.path.join(inner_dir, directory)))

    return summary


def _get_classes_templates(classes: Iterable[ClassT]) -> list[str]:
    """Возвращает список шаблонов `CLASS_TEMPLATE` отформатированных данными из `classes`."""
    result = []
    for _, signature, docstring, meths in classes:
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
    """Возвращает список шаблонов `FUNC_TEMPLATE` отформатированных данными из `funcs`."""
    result = []
    for _, name, signature, docstring in funcs:
        func_template = FUNC_TEMPLATE.format(name=name,
                                             signature=signature,
                                             docstring=docstring or '')
        result.append(func_template)
    return result


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
