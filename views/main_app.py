import os
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from UI_Main import Ui_EasyConnectACAD  # Import the auto_generate


def highlight_text(line_edit):
    line_edit.selectAll()

def add_click_event_to_line_edits(widget):
    for child in widget.findChildren(QLineEdit):
        child.mousePressEvent = lambda event, le=child: highlight_text(le)

class MainApp(QMainWindow, Ui_EasyConnectACAD):

    def __init__(self):
        super().__init__()

        ################################################################################################################
        # Get the font from file path
        self.animation = None
        self.good_qline = None

        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Set the window icon using a relative path
        relative_icon_path = r"Fonts\JetBrainsMono-Bold.ttf"  # Replace this with the relative path of your icon image
        whole_path = os.path.join(current_dir, relative_icon_path)
        whole_path = whole_path.replace("\\", "/")

        font_id = QFontDatabase.addApplicationFont(whole_path)  # Replace with the actual path to your font file
        print(whole_path)
        print(font_id)

        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            custom_font = QFont(font_family)
        else:
            custom_font = QFont()

        # --------------------------------------------------------------------------------------------------------------
        # Setup the UI

        # Center and resize the window to avoid covering the taskbar

        self.setupUi(self)

        # --------------------------------------------------------------------------------------------------------------
        # Set the font for every single Label
        for label in self.findChildren(QLabel):  # Find all QLabel widgets in the UI
            label.setFont(custom_font)
        # --------------------------------------------------------------------------------------------------------------

    # =========  GETTERS  =========

    def get_data(self) -> dict:
        """Reads UI data"""
        return {
            # GENERAL DATA
            # QLineEdits
            "so": self.i_so.text().strip(),
            "ct_groups_qty": self.i_ct_groups_qty.text().strip(),
            "transformer_kVA": self.i_transformer_kVA.text().strip(),
            "HV_voltage": self.i_HV_voltage.text().strip(),
            "HV_amps": self.o_HV_amps.text().strip(),
            "LV_voltage": self.i_LV_voltage.text().strip(),
            "LV_amps": self.o_HV_amps.text().strip(),
            "frequency": self.i_frequency.text().strip(),
            "ct_pocket_H": self.i_ct_pocket_H.text().strip(),
            "ct_pocket_H0": self.i_ct_pocket_H0.text().strip(),
            # QComboBox
            "cooling_class": self.box_Cooling_Class.currentText().strip(),


            # HV CTH INPUTS
            # QLineEdits
            "CTH1_tag": self.i_CTH1_tag.text().strip(),
            "Bushing_OD": self.i_Bushing_OD.text().strip(),
            "CTH1_height_override": self.i_CTH1_height_override.text().strip(),
            "CTH1_ratio_override": self.i_CTH1_ratio_override.text().strip(),
            "CTH1_accuracy_override": self.i_CTH1_accuracy_override.text().strip(),
            "CTH1_ratio_type": self.i_CTH1_ratio_type.text().strip(),
            "CTH1_thermal_factor": self.i_CTH1_thermal_factor.text().strip(),
            # QComboBox
            "box_CTH1_Application": self.box_CTH1_Application.currentText().strip(),
            "box_CTH1_Type": self.box_CTH1_Type.currentText().strip(),
            "box_CTH1_bushing_angled": self.box_CTH1_bushing_angled.currentText().strip(),
            "box_CTH1_STD": self.box_CTH1_STD.currentText().strip(),

            # QTableWidgets
            # "ct_table_1": self._get_table(self.CT_TABLE_1),
        }

    def _get_table(self, table: QTableWidget):
        rows = table.rowCount()
        cols = table.columnCount()
        matrix = []
        for r in range(rows):
            row = []
            for c in range(cols):
                it = table.item(r, c)
                row.append("" if it is None else it.text())
            matrix.append(row)
        return matrix

    # =========  SETTERS  =========
    # ==========================
    # HELPERS
    # ==========================

    def set_data(self, data: dict) -> None:
        outputs_map = {
            "HV_amps": self.o_HV_amps,
            "LV_amps": self.o_LV_amps,
            # "something_else": self.o_something_else,
        }

        for key, widget in outputs_map.items():
            if key in data:
                widget.setText("" if data[key] is None else str(data[key]))

        # Ejemplo line edit:
        # if "customer" in data:
        #     self.le_customer.setText(str(data["customer"]))

        # Ejemplo tabla:
        # if "ct_table_1" in data:
        #     self._set_table(self.CT_TABLE_1, data["ct_table_1"])

    def _set_combobox_by_text(self, cb: QComboBox, value) -> None:
        txt = "" if value is None else str(value)
        idx = cb.findText(txt)
        if idx >= 0:
            cb.setCurrentIndex(idx)
        else:
            if cb.isEditable():
                cb.setCurrentText(txt)

    def _set_table(self, table: QTableWidget, matrix) -> None:
        for r, row in enumerate(matrix):
            for c, val in enumerate(row):
                item = table.item(r, c)
                if item is None:
                    item = QTableWidgetItem()
                    table.setItem(r, c, item)
                item.setText("" if val is None else str(val))



    # =========  CTS ACCOMODATION TABLE =========

    def init_ct_high_tables(self):
        """
        Initializes 6 CT High tables and connects signals so numbering is continuous ("memory")
        across tables for each column H0..H3.
        """
        self.ct_tables = [
            (self.tableCTHigh1, self.i_CTH1_tag),
            (self.tableCTHigh2, self.i_CTH2_tag),
            (self.tableCTHigh3, self.i_CTH3_tag),
            #(self.tableCTHigh4, self.i_CTH4_tag),
            #(self.tableCTHigh5, self.i_CTH5_tag),
            #(self.tableCTHigh6, self.i_CTH6_tag),
        ]

        for table, tag_edit in self.ct_tables:
            self._setup_one_ct_table(table)

            # When user edits the first row (CT/PH), rebuild all
            table.itemChanged.connect(self._rebuild_all_ct_tables)

            # Faster than editingFinished: updates as user types tag
            tag_edit.textEdited.connect(self._rebuild_all_ct_tables)

        # Build once at start
        self._rebuild_all_ct_tables()

    def _setup_one_ct_table(self, t):
        """Setup headers, row count, editability: row 0 editable, rows below read-only."""
        t.setColumnCount(4)
        t.setHorizontalHeaderLabels(["H0", "H1", "H2", "H3"])
        t.verticalHeader().setVisible(True)

        max_ct_per_phase = 4  # <-- adjust if you want more rows
        t.setRowCount(1 + max_ct_per_phase)

        labels = ["CT / PH"] + [""] * (t.rowCount() - 1)
        t.setVerticalHeaderLabels(labels)

        vh = t.verticalHeader()
        vh.setSectionsClickable(False)
        vh.setHighlightSections(False)


        # Row 0 editable
        for c in range(4):
            it = t.item(0, c)
            if it is None:
                it = QTableWidgetItem("")
                t.setItem(0, c, it)
            it.setFlags(
                Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsEditable
            )

        # Rows 1... read-only
        for r in range(1, t.rowCount()):
            for c in range(4):
                it = t.item(r, c)
                if it is None:
                    it = QTableWidgetItem("")
                    t.setItem(r, c, it)
                it.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)

    def _rebuild_all_ct_tables(self, *_):
        """
        Rebuilds ALL 6 tables in order using a per-column memory accumulator.
        This guarantees consistent numbering even if user edits earlier tables.
        """
        used = [0, 0, 0, 0]  # memory per column H0..H3 (counts of CTs already assigned)

        # Block signals for all tables (avoid recursion due to setText)
        for table, _ in self.ct_tables:
            table.blockSignals(True)

        try:
            for table, tag_edit in self.ct_tables:
                tag = (tag_edit.text() or "").strip()

                # Read N (CT/PH) from row 0, each column
                n_list = []
                for col in range(4):
                    top_item = table.item(0, col)
                    txt = (top_item.text() if top_item else "").strip()

                    if txt == "":
                        n = 0
                    else:
                        try:
                            n = int(txt)
                        except ValueError:
                            n = 0
                            # Optional: clear invalid input
                            if top_item:
                                top_item.setText("")
                    if n < 0:
                        n = 0

                    n_list.append(n)

                # Fill each column using the memory offset
                for col in range(4):
                    self._fill_ct_table_column_with_offset(
                        table=table,
                        col=col,
                        n=n_list[col],
                        tag=tag,
                        start_k=used[col],
                    )
                    used[col] += n_list[col]

        finally:
            for table, _ in self.ct_tables:
                table.blockSignals(False)

    def _fill_ct_table_column_with_offset(self, table, col: int, n: int, tag: str, start_k: int):
        """
        Fills column 'col' below row 0 with 'n' tags:
          idx = col + 4*(start_k + k)
          text = f"{tag}-{idx}"
        """
        max_rows_out = table.rowCount() - 1
        n = min(n, max_rows_out)

        # Fill first n rows
        for k in range(n):
            r = 1 + k
            idx = col + 4 * (start_k + k)  # <-- memory applied here
            text = f"{tag}-{idx}" if tag else str(idx)
            table.item(r, col).setText(text)

        # Clear remaining rows
        for r in range(1 + n, table.rowCount()):
            table.item(r, col).setText("")

    # SUMMARY TABLE