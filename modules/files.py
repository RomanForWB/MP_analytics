from json import load as json_load, dump as json_dump
from os import mkdir as mkdir
from subprocess import check_output as subprocess_check_output
from shutil import rmtree as rmdir
from time import sleep

google_keys = None
wb_keys = None
paths = None
mpstats_tokens = None


def open_lines(filename, encoding='utf-8', errors=None):
    """Open file as a list of lines.

    :param filename: file path and file name with extension
    :type filename: str

    :param encoding: name of the encoding used to decode or encode the file
    :type encoding: str

    :param errors: 'strict' or None to raise a ValueError if there is an encoding error
    :type errors: str

    :return: list of string lines
    :rtype: list
    """
    with open(filename, 'r', encoding=encoding, errors=errors) as file:
        return file.read().splitlines()


def open_text(filename, encoding='utf-8', errors=None):
    """Open file as a text.

    :param filename: file path and file name with extension
    :type filename: str

    :param encoding: name of the encoding used to decode or encode the file
    :type encoding: str

    :param errors: 'strict' or None to raise a ValueError if there is an encoding error
    :type errors: str

    :return: string with the text
    :rtype: str
    """
    with open(filename, 'r', encoding=encoding, errors=errors) as file:
        return file.read()


def write_lines(lines, filename, encoding='utf-8', errors=None):
    """Write a list of lines in file.
    String lines should not end with newline symbol.

    :param lines: lines to be write
    :type lines: list

    :param filename: file path and file name with extension
    :type filename: str

    :param encoding: name of the encoding used to decode or encode the file
    :type encoding: str

    :param errors: 'strict' or None to raise a ValueError if there is an encoding error
    :type errors: str
    """
    with open(filename, 'w', encoding=encoding, errors=errors) as file:
        for i in range(len(lines)):
            try: file.write(lines[i] + '\n')
            except UnicodeEncodeError:
                print(f"Внимание - при записи {filename} пропущена строка №{i+1}: {lines[i]}")
                file.write(f'// пропущенная строка №{i+1}\n')
    return lines


def write_text(text, filename, encoding='utf-8', errors=None):
    """Write a string in file.

    :param text: string to be write
    :type text: str

    :param filename: file path and file name with extension
    :type filename: str

    :param encoding: name of the encoding used to decode or encode the file
    :type encoding: str

    :param errors: 'strict' or None to raise a ValueError if there is an encoding error
    :type errors: str
    """
    try:
        with open(filename, 'w', encoding=encoding, errors=errors) as file: file.write(text)
    except UnicodeEncodeError:
        write_lines(text.splitlines(), filename, encoding, errors)


def write_json(to_json, filename):
    """Write json-like object in a presentative form.

    :param to_json: object to be saved

    :param filename: file path and file name with extension
    :type filename: str
    """
    with open(filename, 'w') as file:
        json_dump(to_json, file, indent=4)


def open_with_notepad(path):
    """Open file/multiple files in Notepad++.
    The path to Notepad++ executable can be changed in keys/paths.json

    :param path: path to the folder / path to only one file
    :type path: str
    """
    notepad_path = get_path('notepad++').replace('.exe', '')
    return subprocess_check_output('\"{}\" -multiInst -nosession \"{}\"'.format(notepad_path, path))


def delete_folder(folder):
    """Delete the folder and its contents.

    :param folder: path to the folder
    :type folder: str
    """
    try:
        rmdir(folder)
    except: pass


def clean_folder(folder):
    """Delete folder contents (the folder remains).

    :param folder: path to the folder
    :type folder: str
    """
    delete_folder(folder)
    sleep(0.5)
    mkdir(folder)


def create_folder(folder):
    """Create folder in a specific path.

    :param folder: path to the folder
    :type folder: str
    """
    mkdir(folder)


def get_path(identifier):
    """Get file path by identifier.
    File paths can be expanded in keys/paths.json.

    :param identifier: one of:
        'wb_analytics',
        'notepad++',
        'chrome_driver'
    :type identifier: str

    :return: file path
    :rtype: str
    """
    global paths
    if paths is None:
        with open("keys/paths.json", "r") as json_file:
            paths = json_load(json_file)
    path = paths[identifier]
    return path
