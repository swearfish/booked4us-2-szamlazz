import subprocess

import flet as ft
from flet.core.types import ScrollMode

from converter import Converter, FieldType


# noinspection SpellCheckingInspection
class ConverterApp:
    def __init__(self, page: ft.Page):
        self._page = page
        self._page.theme_mode = ft.ThemeMode.LIGHT
        self._page.padding = 0

        self._page.window.maximized = True

        self._page.title = "Kutyaguru Bookd4us --> Számlázz.hu konvertáló"
        self._page.vertical_alignment = ft.MainAxisAlignment.CENTER

        self._status_bar = ft.Container(
            bgcolor=ft.Colors.GREY,
            height=32,
            padding=4,
            margin=0

        )
        self._toolbar = ft.Container(
            content = self.build_toolbar(),
            bgcolor=ft.Colors.LIGHT_BLUE,
            padding=4,
            margin=0)

        self._table_container = ft.Container(expand=True)
        self._tab_table = ft.Tab(text="Táblázat", content=self.build_layout())
        self._tab_fields = ft.Tab(text="Mezők")

        self._tab_bar = ft.Tabs(
            tabs=[
                self._tab_table,
                self._tab_fields,
            ],
            expand=True
        )

        self._page.add(self._tab_bar)
        self._page.update()

        try:
            self._converter = Converter()
        except Exception as e:
            self.show_alert_message("Hiba az indításkor", str(e))

        self._tab_fields.content = self._build_fields_table()
        self._page.update()


    def show_alert_message(self, title: str, message: str):
        dlg = ft.AlertDialog(
            title=ft.Text(title),
            content=ft.Text(message),
            modal=True,
            actions=[
                ft.TextButton("OK", on_click=lambda _: self._page.close(dlg))
            ]
        )
        self._page.open(dlg)

    def build_layout(self):
        col = ft.Column(
            [self._toolbar, self._table_container, self._status_bar],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER
        )
        return col

    def build_toolbar(self):

        input_path = ft.Text('Nincs Excel fájl megnyitva!')
        self._status_bar.content = input_path

        def on_booked4us_excel_selected(path):
            input_path.value = path
            self._converter.load_excel_file(path)
            excel_sheet_dropdown.options = [ft.dropdown.Option(sheet) for sheet in self._converter.sheet_names]
            excel_sheet_dropdown.value = self._converter.sheet_names[0]
            excel_sheet_selected(self._converter.sheet_names[0])

        btn_open_booked4us_xlsx = self._build_open_file_btn(
            tooltip="Booked4us Excel fájl megnyitása",
            icon=ft.Icons.FILE_OPEN,
            extensions=["xlsx"],
            on_open=on_booked4us_excel_selected
        )

        def excel_sheet_selected(sheet):
            self._converter.read_booked4us_excel_sheet(sheet)
            self._table_container.content = self.build_table()
            self._page.update()

        excel_sheet_dropdown = ft.Dropdown(
            enable_filter=False,
            editable=False,
            label="Excel munkalap kiválasztása",
            width=300,
            on_change=lambda e: excel_sheet_selected(e.control.value),
            options=[])

        def btn_import_click(path: str):
            self._converter.import_from_work_xlsx(path)
            excel_sheet_dropdown.options = []
            excel_sheet_dropdown.value = None
            input_path.value = path
            self._table_container.content = self.build_table()

        btn_import_temp_xlsx = self._build_open_file_btn(
            tooltip="Köztes adatok betöltése Excel fájlból",
            icon=ft.Icons.IMPORT_EXPORT,
            extensions=["xlsx"],
            on_open=btn_import_click
        )

        def btn_export_click(path: str):
            if not path.endswith(".xlsx"):
                path += ".xlsx"
            self._converter.export_to_work_xlsx(path)
            subprocess.run(["open", path])

        btn_export_temp_xlsx = self._build_save_btn(
            tooltip="Köztes adatok mentése Excelbe szerkesztésre",
            icon=ft.Icons.FILE_DOWNLOAD,
            extensions=["xlsx"],
            on_save=btn_export_click
        )

        btn_save_csv = self._btn_save_szamlazz_csv()

        return ft.Column(
            [
                ft.Row([
                    btn_open_booked4us_xlsx,
                    excel_sheet_dropdown,
                    ft.Divider(),
                    btn_export_temp_xlsx,
                    btn_import_temp_xlsx,
                    ft.Divider(),
                    btn_save_csv
                ], alignment=ft.MainAxisAlignment.CENTER),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )

    def build_table(self):
        df = self._converter.data

        if df is None or df.empty or len(df.columns) == 0:
            return ft.Text("Nincs adat vagy nincs Excel fájl megnyitva!")

        columns = [ft.DataColumn(ft.Text(col, width=160)) for col in df.columns]

        # Create DataTable rows
        rows = []
        for index, row in df.iterrows():
            cells = []
            for name, value in row.items():
                def on_change(control):
                    row_index, column_name = control.data
                    self._converter.data.at[row_index, column_name] = control.value
                content = ft.TextField(
                    str(value), data=(index, name),
                    on_change=lambda e: on_change(e.control))
                cell = ft.DataCell(content)
                cells.append(cell)
            color = ft.Colors.GREY_200 if index % 2 == 0 else ft.Colors.WHITE
            rows.append(ft.DataRow(cells=cells, color=color))

        # Create the DataTable
        data_table = ft.DataTable(
            columns=columns,
            rows=rows,
            show_bottom_border=True,
        )

        row = ft.Row([data_table], scroll=ScrollMode.ALWAYS, expand=True, alignment=ft.MainAxisAlignment.START)
        col = ft.Column([row], scroll=ScrollMode.ALWAYS, expand=True, alignment=ft.MainAxisAlignment.START)

        return col

    def _build_fields_table(self):
        fields = self._converter.fields
        columns = [
            ft.DataColumn(ft.Text("Mező", width=160)),
            ft.DataColumn(ft.Text("Típus", width=160)),
            ft.DataColumn(ft.Text("Érték", width=160)),
        ]
        rows = []
        for name, field in fields.items():
            if field.field_type == FieldType.MAPPING:
                value = field.mapping
                value_cell = ft.Text(value)
                type_name = "EXCEL-ből"
            elif field.field_type == FieldType.CONST:
                value = field.value
                value_cell = ft.Text(value)
                type_name = "KONSTANS"
            else:
                value = str(field.value)
                def on_change(control):
                    field_name, field_ref = control.data
                    field_ref.value = control.value
                    self._converter.fields[field_name] = field_ref
                value_cell = ft.TextField(value, data=(name, field), on_change=lambda e: on_change(e.control))
                type_name = "SZERKESZTHETŐ"
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(name)),
                ft.DataCell(ft.Text(type_name)),
                ft.DataCell(value_cell),
            ]))

        data_table = ft.DataTable(
            columns=columns,
            rows=rows,
            show_bottom_border=True,
        )

        return data_table

    def _btn_save_szamlazz_csv(self):

        def output_csv_file_selected(path):
            self._converter.convert_and_save_csv(path)
            self.show_alert_message("Siker", f"Mentve a {path} fájlba")

        return self._build_save_btn(
            tooltip="Számlázz.hu CSV mentése",
            icon=ft.Icons.SAVE,
            extensions=["csv"],
            on_save=output_csv_file_selected
        )

    def _build_open_file_btn(self, tooltip, icon, extensions, on_open):
        def input_file_selected(e):
            if e.files:
                self._converter.load_excel_file(e.files[0].path)
                on_open(e.files[0].path)
                self._page.update()

        input_picker = ft.FilePicker(on_result=input_file_selected)
        self._page.overlay.extend([input_picker])

        return ft.IconButton(
            tooltip=tooltip,
            icon=icon,
            on_click=lambda _: input_picker.pick_files(allowed_extensions=extensions, allow_multiple=False)
        )

    def _build_save_btn(self, tooltip, icon, extensions, on_save):

        def output_csv_file_selected(e):
            if e.path:
                try:
                    on_save(e.path)
                except Exception as ex:
                    self.show_alert_message("Hiba!", str(ex))
            self._page.update()

        def save_file_clicked(_):
            if not self._converter.has_data:
                self.show_alert_message("Hiba!", "Nincs még Excel fájl vagy munkalap megnyitva!")
            else:
                output_picker.save_file(allowed_extensions=extensions)

        output_picker = ft.FilePicker(on_result=output_csv_file_selected)
        self._page.overlay.extend([output_picker])

        return ft.IconButton(
            tooltip=tooltip,
            icon=icon,
            on_click=save_file_clicked
        )

def main(page: ft.Page):
    ConverterApp(page)

if __name__ == "__main__":
    # noinspection SpellCheckingInspection
    ft.app(main, name="Booked4us --> Számlázz.hu")
