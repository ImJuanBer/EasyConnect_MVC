import os
from PyQt6.QtGui import QFontDatabase, QFont
from PyQt6.QtWidgets import QMainWindow, QLabel, QLineEdit
from UI_Main import Ui_AutocadAutomation  # Import the auto_gener
from controller import Controller

def highlight_text(line_edit):
    line_edit.selectAll()

def add_click_event_to_line_edits(widget):
    for child in widget.findChildren(QLineEdit):
        child.mousePressEvent = lambda event, le=child: highlight_text(le)

class MainApp(QMainWindow, Ui_AutocadAutomation):

    def __init__(self):
        super().__init__()

        ################################################################################################################
        # Get the font from file path
        self.animation = None
        self.good_qline = None

        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Set the window icon using a relative path
        relative_icon_path = "Fonts\JetBrainsMono-Bold.ttf"  # Replace this with the relative path of your icon image
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
        ################################################################################################################
        ################################################################################################################
        # Setup the UI

        # Center and resize the window to avoid covering the taskbar

        self.setupUi(self)

        ################################################################################################################
        # Set the font for every single Label
        for label in self.findChildren(QLabel):  # Find all QLabel widgets in the UI
            label.setFont(custom_font)



        self.controller = Controller(self)



