from PyQt5.QtWidgets import QApplication
from cliente import Cliente
import sys


if __name__ == "__main__":
    app = QApplication([])
    cliente = Cliente()
    sys.exit(app.exec_())
