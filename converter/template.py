from os import PathLike
from typing import TextIO


def read_template_file(template_file_name: PathLike, encoding="ISO-8859-2") -> (list, list):
    """
    Reads a template file and returns the header lines and column definitions.

    The return value is a tuple of two lists. The first list contains the header
    lines, the second list contains the column definitions. Each column definition
    is a list of strings, where the first string is the column name and the rest are
    the values for that column.

    :param template_file_name: The name of the file to read
    :param encoding: The encoding of the file. Default is "ISO-8859-2"
    :return: A tuple containing the header lines and the column definitions
    :rtype: (list, list)
    """
    with open(template_file_name, "r", encoding=encoding) as template_file:
        return _process_template_file(template_file)

def _process_template_file(template_file: TextIO) -> (list, list):
    """
    Reads columns from a template file and returns them in a tuple of two lists.

    The first list contains the header lines, the second list contains the column
    definitions. Each column definition is a list of strings, where the first string
    is the column name and the rest are the values for that column.

    The file is read line by line. If a line is empty or does not start with a
    semicolon, the reading is stopped. If a line starts with two semicolons,
    it is considered a header line and appended to the header list. Otherwise,
    it is split into columns and appended to the columns list.

    :param template_file: A file object from which the columns are read
    :return: A tuple containing the header lines and the column definitions
    :rtype: (list, list)
    """
    header = []
    columns = []
    while True:
        line = template_file.readline().strip("\n")
        if line == "" or not line.startswith(";"):
            break
        if line.startswith(";;"):
            header += [line]
        else:
            columns += [line]

    result = []
    for line in columns:
        line_columns = line.split(";")
        result += [line_columns]
    return header, result
