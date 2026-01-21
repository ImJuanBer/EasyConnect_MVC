import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QLabel
from PyQt5 import QtCore
from pyautocad import Autocad
import pythoncom
import win32com.client
import re
import time


class TemplateModel:

    @staticmethod
    def APoint(x, y, z=0):
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y, z))

    @staticmethod
    def aDouble(xyz):
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, xyz)

    @staticmethod
    def aDispatch(vObject):
        return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, vObject)

    def __init__(self):

        self.pyacad = Autocad()

    @staticmethod
    def pop_up(error):
        message_box2 = QMessageBox()
        current_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/") + "/"

        # Set the window icon using a relative path
        relative_icon_path = "Images/mess.png"  # Replace this with the relative path of your icon image
        window_icon_path = os.path.join(current_dir, relative_icon_path)

        # Set the message box properties
        window_icon = QIcon(window_icon_path)
        message_box2.setWindowIcon(window_icon)
        message_box2.setWindowTitle("INFORMATIVE MESSAGE")
        text_widget = message_box2.findChild(QLabel)
        if text_widget:
            text_widget.setAlignment(QtCore.Qt.AlignCenter)  # Center-align the text
        message_box2.setText(error)
        message_box2.exec_()

    @staticmethod
    def pop_up_yes_no(confirmation):
        message_box = QMessageBox()
        current_dir = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/") + "/"

        # Set the window icon using a relative path
        relative_icon_path = "Images/warning.png"  # Replace this with the relative path of your icon image
        window_icon_path = os.path.join(current_dir, relative_icon_path)

        # Set the message box properties
        window_icon = QIcon(window_icon_path)
        message_box.setWindowIcon(window_icon)
        message_box.setWindowTitle("Confirmation")
        message_box.setIcon(QMessageBox.Question)
        message_box.setText(confirmation)
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.No)

        # Show the message box and wait for the user response
        response = message_box.exec_()

        # Process the user response
        if response == QMessageBox.Yes:
            return True
        else:
            return False



    def create_templates(self, acadModel, y_base=0, espaciado_horizontal_entre_templates=90,
                         block_name="MY_TEMPLATE_SMALL"):

        templates_config = {
            "03-N22453-AC": {
                "DESIGNER_NAME": "Juan Gomez",
                "PO_NUMBER": "235992",
                "Q_NO": "Q22453",
                "ULTIMATE_LOC": "IDAHO POWER",
                "TITLE": "CURRENT TRANSFORMERS",
                "SO_NO": "N22453",
                "CUSTOMER": "IDAHO POWER",
                "DRAWING_NO": "",
                "R": "0"

            },
            "03-N22453-CT": {
                "DESIGNER_NAME": "Juan Gomez",
                "PO_NUMBER": "235992",
                "Q_NO": "Q22453",
                "ULTIMATE_LOC": "IDAHO POWER",
                "TITLE": "CURRENT TRANSFORMERS",
                "SO_NO": "N22453",
                "CUSTOMER": "IDAHO POWER",
                "DRAWING_NO": "",
                "R": "0",
            },

            "03-N22453-WIR1": {
                "DESIGNER_NAME": "Juan Gomez",
                "PO_NUMBER": "235992",
                "Q_NO": "Q22453",
                "ULTIMATE_LOC": "IDAHO POWER",
                "TITLE": "WIRING DIAGRAM 1",
                "SO_NO": "N22453",
                "CUSTOMER": "IDAHO POWER",
                "DRAWING_NO": "",
                "R": "0",
            },
        }

        # Recorremos cada grupo

        for group, (key, config) in enumerate(templates_config.items()):
            x_pos = group * espaciado_horizontal_entre_templates  # template horizontal

            block = acadModel.InsertBlock(self.APoint(x_pos, y_base), block_name, 1, 1, 1, 0)
            block.XScaleFactor = 1
            block.YScaleFactor = 1
            block.ZScaleFactor = 1

            # Actualizar atributos, saltando TITLE
            for template_attributes in block.GetAttributes():
                attribute = template_attributes.TagString.strip().upper()

                # Busca el valor por TAG (acepta mayúsculas o Title-case)
                val = (config.get(attribute) or config.get(attribute.title()) or "")
                template_attributes.TextString = str(val)
                template_attributes.Update()

                if template_attributes.TagString.strip().upper() == "DRAWING_NO":
                    template_attributes.TextString = f"{key}"
                if template_attributes.TagString.strip().upper() == "ID":
                    template_attributes.TextString = f"{key}"



