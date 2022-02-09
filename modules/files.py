from openpyxl import load_workbook
from json import load as json_load, dump as json_dump
from os import mkdir as mkdir
from subprocess import check_output as subprocess_check_output
from shutil import rmtree as rmdir
from time import sleep

google_keys = None
wb_keys = None
paths = None

# открыть файл и получить его в виде списка строк
def open_lines(filename, codirovka = 'utf-8', errors = ''):
    if errors != '':
        with open(filename, 'r', encoding=codirovka, errors=errors) as file:
            lines = file.read().splitlines()
        return lines
    else:
        with open(filename, 'r', encoding=codirovka) as file:
            lines = file.read().splitlines()
        return lines

# открыть файл и получить его в виде одной строки с текстом
def open_text(filename, codirovka = 'utf-8', errors = ''):
    if errors != '':
        with open(filename, 'r', encoding=codirovka, errors=errors) as file:
            text = file.read()
        return text
    else:
        with open(filename, 'r', encoding=codirovka) as file:
            text = file.read()
        return text

# записать в файл список строк
def write_lines(lines, filename, codirovka = 'utf-8', errors = None):
    with open(filename, 'w', encoding=codirovka, errors=errors) as file:
        for i in range(len(lines)):
            try:
                file.write(lines[i] + '\n')
            except UnicodeEncodeError:
                if filename.startswith('history/'): pass
                else: print("Внимание - при записи {} пропущена строка №{}: {}".format(filename, i+1, lines[i]))
                file.write('// missing_line \n')
    return lines


def write_text(text, filename, encoding = 'utf-8', errors = None):
    """Write a string in file.

    :param text: string to be write
    :type text: str

    :param filename: file path and file name with extension
    :type filename: str

    :param encoding: name of the encoding used to decode or encode the file
    :type encoding: str

    :param errors: 'strict' or None to raise a ValueError if there is an encoding error
    (the default of None has the same effect), 'ignore' to ignore errors.
    :type errors: str
    """
    try:
        with open(filename, 'w', encoding=encoding, errors=errors) as file: file.write(text)
    except UnicodeEncodeError:
        write_lines(text.splitlines(), filename, encoding)


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
    output = subprocess_check_output('\"{}\" -multiInst -nosession \"{}\"'.format(notepad_path, path))


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


def get_wb_key(type, supplier):
    """Get wildberries key or token.
    New suppliers and tokens can be added in keys/wb.json.

    :param type: one of: 'token', 'x32', 'x64'
    :type type: str

    :param supplier: one of the suppliers in supplier's dictionary in main
    :type supplier: str

    :return: wildberries key or token string
    :rtype: str
    """
    global wb_keys
    if wb_keys is None:
        with open("keys/wb.json", "r") as json_file:
            wb_keys = json_load(json_file)
    key = wb_keys[type][supplier]
    return key


def get_google_key(identifier):
    """Get google document key.
    Google keys can be expanded in keys/google.json.

    :param identifier: one of: 'wb_analytics'
    :type identifier: str

    :return: google key
    :rtype: str
    """
    global google_keys
    if google_keys is None:
        with open("keys/google.json", "r") as json_file:
            google_keys = json_load(json_file)
    key = google_keys[identifier]
    return key


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

