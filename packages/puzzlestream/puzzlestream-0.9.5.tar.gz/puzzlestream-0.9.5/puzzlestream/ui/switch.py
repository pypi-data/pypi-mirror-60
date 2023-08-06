from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class PSSlideSwitchPrivate(QObject):

    def __init__(self, q: QObject):
        super().__init__()

        self._position = 0
        self._sliderShape = QRectF()
        self._gradient = QLinearGradient()
        self._gradient.setSpread(QGradient.PadSpread)
        self._qPointer = q

        self.animation = QPropertyAnimation(self)
        self.animation.setTargetObject(self)
        self.animation.setPropertyName(b"position")
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutExpo)

    @pyqtProperty(float)
    def position(self) -> QPoint:
        return self._position

    @position.setter
    def position(self, value: QPoint):
        self._position = value
        self._qPointer.repaint()

    def drawSlider(self, painter: QPainter):
        margin = 3
        r = self._qPointer.rect().adjusted(0, 0, -1, -1)
        dx = (r.width() - self._sliderShape.width()) * self._position
        sliderRect = self._sliderShape.translated(dx, 0)
        painter.setPen(Qt.NoPen)

        # basic settings
        shadow = self._qPointer.palette().color(QPalette.Dark)
        light = self._qPointer.palette().color(QPalette.Light)
        button = self._qPointer.palette().color(QPalette.Button)

        # draw background
        # draw outer background
        self._gradient.setColorAt(0, shadow.darker(130))
        self._gradient.setColorAt(1, light.darker(130))
        self._gradient.setStart(0, r.height())
        self._gradient.setFinalStop(0, 0)
        painter.setBrush(self._gradient)
        painter.drawRoundedRect(r, 15, 15)

        # draw background
        # draw inner background
        self._gradient.setColorAt(0, shadow.darker(140))
        self._gradient.setColorAt(1, light.darker(160))
        self._gradient.setStart(0, 0)
        self._gradient.setFinalStop(0, r.height())
        painter.setBrush(self._gradient)
        painter.drawRoundedRect(r.adjusted(
            margin, margin, -margin, -margin), 15, 15)

        # draw slider
        self._gradient.setColorAt(0, button.darker(130))
        self._gradient.setColorAt(1, button)

        # draw outer slider
        self._gradient.setStart(0, r.height())
        self._gradient.setFinalStop(0, 0)
        painter.setBrush(self._gradient)
        painter.drawRoundedRect(sliderRect.adjusted(
            margin, margin, -margin, -margin), 10, 15)

        # draw inner slider
        self._gradient.setStart(0, 0)
        self._gradient.setFinalStop(0, r.height())
        painter.setBrush(self._gradient)
        painter.drawRoundedRect(sliderRect.adjusted(
            2.5 * margin, 2.5 * margin, -2.5 * margin, - 2.5 * margin), 5, 15)

        # draw text
        if self.animation.state() == QPropertyAnimation.Running:
            return  # don't draw any text while animation is running

        font = self._qPointer.font()
        self._gradient.setColorAt(0, light)
        self._gradient.setColorAt(1, shadow)
        self._gradient.setStart(0, r.height() / 2.0 + font.pointSizeF())
        self._gradient.setFinalStop(0, r.height() / 2.0 - font.pointSizeF())
        painter.setFont(font)
        painter.setPen(QPen(QBrush(self._gradient), 0))

    def updateSliderRect(self, size: QSize):
        self._sliderShape.setWidth(size.width() / 2.0)
        self._sliderShape.setHeight(size.height() - 1.0)

    @pyqtSlot(bool, name='animate')
    def animate(self, checked: bool):
        self.animation.setDirection(
            QPropertyAnimation.Forward if checked else
            QPropertyAnimation.Backward)
        self.animation.start()


class PSSlideSwitch(QAbstractButton):
    def __init__(self, parent: QObject = None):
        super().__init__(parent)
        self.setCheckable(True)

        self.d_ptr = PSSlideSwitchPrivate(self)
        self.clicked.connect(self.d_ptr.animate)
        self.d_ptr.animation.finished.connect(self.update)

    def sizeHint(self):
        return QSize(48, 28)

    def hitButton(self, point: QPoint):
        return self.rect().contains(point)

    def paintEvent(self, event: QEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        self.d_ptr.drawSlider(painter)

    def resizeEvent(self, event: QEvent):
        self.d_ptr.updateSliderRect(event.size())
        self.repaint()
