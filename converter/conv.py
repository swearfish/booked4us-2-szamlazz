from os import PathLike
from pathlib import Path

import pandas as pd

from converter.booked4us_xlsx import read_booked4us_excel_sheet
from converter.field import read_fields_file
from converter.szamlazz_csv import convert_and_save_csv
from converter.template import read_template_file


class Converter:
    def __init__(self,
                 asset_path: PathLike = None,
                 template_file_name: PathLike = None,
                 fields_file_name: PathLike = None):
        if asset_path is None:
            asset_path = Path("assets")
        if template_file_name is None:
            template_file_name =  asset_path.joinpath("basic sablon.csv")
        if fields_file_name is None:
            fields_file_name = asset_path.joinpath("fields.yaml")
        self.output_header, self.output_columns = read_template_file(template_file_name)
        self.fields = read_fields_file(fields_file_name)
        self._excel_file = None
        self.data = pd.DataFrame()

    @property
    def is_excel_file_loaded(self):
        return self._excel_file is not None

    @property
    def has_data(self):
        return self.data is not None and not self.data.empty

    def load_excel_file(self, input_file_name: PathLike):
        self._excel_file = pd.ExcelFile(input_file_name)

    @property
    def sheet_names(self):
        return self._excel_file.sheet_names

    def read_booked4us_excel_sheet(self, sheet=None):
        self.data = read_booked4us_excel_sheet(self._excel_file, self.fields, sheet)

    def convert_and_save_csv(self, output_file_name: PathLike, encoding="ISO-8859-2"):
        convert_and_save_csv(output_file_name, self.output_header, self.output_columns, self.data, encoding)

    def import_from_work_xlsx(self, path):
        self.data = pd.read_excel(path)

    def export_to_work_xlsx(self, path):
        self.data.to_excel(path, index=False)

