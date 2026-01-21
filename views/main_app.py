import os
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit, QComboBox, QTableWidget, QTableWidgetItem
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

    def set_data(self, data: dict) -> None:
        """Actualiza el UI con keys presentes en 'data'."""

        if "drawing_selector" in data:
            self._set_combobox_by_text(self.drawing_selector_box, data["drawing_selector"])

        if "phases" in data:
            self._set_combobox_by_text(self.phases_box, data["phases"])

        # Ejemplo line edit:
        # if "customer" in data:
        #     self.le_customer.setText(str(data["customer"]))

        # Ejemplo tabla:
        # if "ct_table_1" in data:
        #     self._set_table(self.CT_TABLE_1, data["ct_table_1"])

    # ==========================
    # HELPERS
    # ==========================

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



