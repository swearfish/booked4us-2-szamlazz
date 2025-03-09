from os import PathLike

from pandas import DataFrame


def convert_and_save_csv(output_file_name: PathLike,
                         header: list[str],
                         columns: list[list[str]],
                         data: DataFrame,
                         encoding="ISO-8859-2"):
    with open(output_file_name, "w", encoding=encoding) as output_file:
        for line in header:
            output_file.write(line + "\n")
        for line in columns:
            output_file.write(";".join(line) + "\n")
        for index, row in data.iterrows():
            num = int(str(index)) + 1
            output_file.write(f"{num}")
            for line in columns:
                for column in line:
                    cell = row[column] if column in row else ""
                    output_file.write(f"{cell};")
                output_file.write("\n")
