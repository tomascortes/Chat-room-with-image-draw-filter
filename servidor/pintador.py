
def paintEvent(self, event):

        painter = QPainter(self)

        painter.setPen(QPen(Qt.green,  8, Qt.SolidLine))

        painter.setBrush(QBrush(Qt.red, Qt.SolidPattern))

        painter.drawEllipse(40, 40, 400, 400)
