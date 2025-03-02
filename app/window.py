from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import QPointF

FRAMES_STYLE = """
background-color: #222222;
border-radius: 50px;
"""

class App(QtWidgets.QApplication):
    def __init__(self):
        super().__init__([])

        # Создание главного окна
        self.window = QtWidgets.QMainWindow()
        self.window.setStyleSheet("background-color: #2C2C2C;")
        self.window.setWindowTitle("Моё приложение")
        self.window.setFixedSize(1600, 900)

        # Центральный виджет
        central_widget = QtWidgets.QWidget()
        self.window.setCentralWidget(central_widget)

        # Основной layout
        self.window_layout = QtWidgets.QHBoxLayout(central_widget)
        self.window_layout.setContentsMargins(30, 120, 30, 120) # left, top, right, bottom
        self.window_layout.setSpacing(40)

        # Виджет расписания
        self.schedule = QtWidgets.QFrame()
        self.schedule.setStyleSheet(FRAMES_STYLE)
        self.schedule.setFixedWidth(290)
        self.schedule.setGraphicsEffect(self._create_shadow())
        self.window_layout.addWidget(self.schedule)

        # Виджет домашних заданий
        self.homework = QtWidgets.QFrame()
        self.homework.setStyleSheet(FRAMES_STYLE)
        self.homework.setFixedWidth(880)
        self.window_layout.addWidget(self.homework)

        # Виджет оценок
        self.grades = QtWidgets.QFrame()
        self.grades.setStyleSheet(FRAMES_STYLE)
        self.grades.setFixedWidth(290)
        self.window_layout.addWidget(self.grades)

        self.window.show()

    @staticmethod
    def _create_shadow() -> QtWidgets.QGraphicsDropShadowEffect:
        shadow = QtWidgets.QGraphicsDropShadowEffect(
                offset=QPointF(-3,5), blurRadius=15, color=QtGui.QColor(34, 34, 34, 150)
        )
        return shadow


if __name__ == '__main__':
    app = App()
    app.exec()