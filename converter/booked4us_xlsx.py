from pandas import ExcelFile, DataFrame

from .field import Field, FieldType


def read_booked4us_excel_sheet(excel_file: ExcelFile, fields: dict[str, Field], sheet=None):
    if sheet is None:
        sheet = excel_file.sheet_names[0]
    input_df = excel_file.parse(sheet)
    output_cols = {}
    for field in fields:
        output_cols[field] = []

    for index, row in input_df.iterrows():
        for field_name, field in fields.items():
            if field.field_type == FieldType.MAPPING:
                if field.mapping in row:
                    output_cols[field_name].append(row[field.mapping])
                else:
                    output_cols[field_name].append("")
            else:
                output_cols[field_name].append(field.value)
    return DataFrame(output_cols)
