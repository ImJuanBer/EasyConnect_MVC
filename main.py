import sys
from PyQt6.QtWidgets import QApplication
from views.main_app import MainApp
from controller import Controller


def exception_hook(exctype, value, traceback):
    traceback_formatted = traceback.format_exception(exctype, value, traceback)
    traceback_string = "".join(traceback_formatted)
    print(traceback_string, file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":

    sys._excepthook = sys.excepthook
    sys.excepthook = exception_hook
    app = QApplication(sys.argv)
    view = MainApp()
    controller = Controller(view)
    view.show()
    sys.exit(app.exec())
