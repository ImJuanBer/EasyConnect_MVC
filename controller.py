from Models.templates_model import TemplateModel
from Models.contacts_model import ContactsModel
from Models.ct_model import CTModel
from Models.tb_maker_model import TBModel
from pyautocad import Autocad
import win32com.client
import time
import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMessageBox, QLabel
from PyQt6 import QtCore


def regeneration(doc):
    try:
        # 0 = acActiveViewport, 1 = acAllViewports
        doc.Regen(1)
    except Exception:
        # Fallback si el método falla en tu versión:
        try:
            doc.SendCommand("REGEN\n")
        except Exception:
            pass


class Controller:
    def __init__(self, view):
        # ------------------------------------------------------------------------
        # ------------------------------------------------------------------------
        self.view = view  # View is MainApp and self.View has access to all MainApp features
        self.templatesModel = TemplateModel()
        self.contactsModel = ContactsModel()
        self.ctModel = CTModel()
        self.tbModel = TBModel()
        self.init_ACAD()
        self.view.actionOpen_ACAD.triggered.connect(self.open_ACAD_master_file)

        self.view.run_button.clicked.connect(self.runAll)

        # Regen ACAD sheet
        regeneration(self.doc)

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

    def init_ACAD(self):
        try:
            # Instance to use PyAutocad
            self.pyacad = Autocad()
            self.acad = win32com.client.Dispatch("AutoCAD.Application")
            self.acadModel = self.acad.ActiveDocument.ModelSpace
            self.doc = self.acad.ActiveDocument

        except:

            self.pop_up("Autocad is not opened!")

    def open_ACAD_master_file(self):

        acad_file_path = "main_scaled_acad.dwg"
        current_dir = os.path.dirname(os.path.abspath(__file__))
        autocad_file_path = os.path.join(current_dir, acad_file_path)
        print(autocad_file_path)

        if not os.path.exists(autocad_file_path):
            self.pop_up(f"AutoCAD file not found: {autocad_file_path}")
            return

        # Create an AutoCAD instance
        self.acad = win32com.client.Dispatch("AutoCAD.Application")
        self.acad.Visible = True
        self.acad.Documents.Open(autocad_file_path)
        time.sleep(2)  # Needed to avoid cross proccessing

        # Open the Master Autocad File
        max_retries = 5  # Adjust the number of retries as needed
        for retry in range(max_retries):
            try:
                self.doc = self.acad.ActiveDocument
                break  # Break the loop if successful
            except AttributeError:
                time.sleep(1.5)  # Wait before retrying

        self.pop_up("Autocad was succesfully opened!")

        if self.doc is None:
            self.pop_up(f"Failed to open AutoCAD document after {max_retries} retries.")
            return False

    def runAll(self):
        data = self.view.get_data()  # ← get the dictionary from view

        drawing_selector = data["drawing_selector"]
        phases = data["phases"]

        print(drawing_selector)
        print(phases)
