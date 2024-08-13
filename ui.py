try:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
except ImportError:
    from PySide6.QtGui import *
    from PySide6.QtCore import *
    from PySide6.QtWidgets import *
    from shiboken6 import wrapInstance

import maya.OpenMayaUI as omui
from . import helper_joints


def mayaMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mainWindowPtr), QWidget)


class CollapsibleHeader(QWidget):

    COLLAPSED_PIXMAP = QPixmap(":teRightArrow.png")
    EXPENDED_PIXMAP = QPixmap(":teDownArrow.png")
    COLOR = QPushButton().palette().color(QPalette.Button)
    clicked = Signal()

    def __init__(self, text, parent=None):
        super(CollapsibleHeader, self).__init__(parent)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, self.COLOR)
        self.setPalette(palette)

        self.iconLabel = QLabel()
        self.iconLabel.setFixedWidth(self.COLLAPSED_PIXMAP.width())

        self.textLabel = QLabel()
        self.textLabel.setAttribute(Qt.WA_TransparentForMouseEvents)

        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(4, 4, 4, 4)
        self.mainLayout.addWidget(self.iconLabel)
        self.mainLayout.addWidget(self.textLabel)

        self.setText(text)
        self.setExpended(False)

    def setText(self, text):
        self.textLabel.setText("<b>{0}</b>".format(text))

    def isExpanded(self):
        return self._expanded

    def setExpended(self, expanded):
        self._expanded = expanded
        if(self._expanded):
            self.iconLabel.setPixmap(self.EXPENDED_PIXMAP)
        else:
            self.iconLabel.setPixmap(self.COLLAPSED_PIXMAP)

    def mouseReleaseEvent(self, event):
        self.clicked.emit()


class CollapsibleWidget(QWidget):
    def __init__(self, text, parent=None):
        super(CollapsibleWidget, self).__init__(parent)

        self.headerWdg = CollapsibleHeader(text)
        self.headerWdg.clicked.connect(self.headerClicked)

        self.bodyWdg = QWidget()
        self.bodyLayout = QVBoxLayout(self.bodyWdg)
        self.bodyLayout.setContentsMargins(0, 0, 0, 0)
        self.bodyLayout.setSpacing(3)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.headerWdg)
        self.mainLayout.addWidget(self.bodyWdg)

        self.setExpanded(False)

    def addWidget(self, widget):
        self.bodyLayout.addWidget(widget)

    def setExpanded(self, expanded):
        self.headerWdg.setExpended(expanded)
        self.bodyWdg.setVisible(expanded)

    def addLayout(self, layout):
        self.bodyLayout.addLayout(layout)

    def headerClicked(self):
        self.setExpanded(not self.headerWdg.isExpanded())


class ForArmTwistTab(QWidget):
    def __init__(self):
        super(ForArmTwistTab, self).__init__()
        self.createWidgets()
        self.createLayout()
        self.createConnections()

    def createWidgets(self):
        self.forArmLowerArmLe = QLineEdit()
        self.forArmWristLe = QLineEdit()
        self.forArmWristTag = QLabel("Wrist Joint:")

        self.validator = QDoubleValidator()
        self.validator.setRange(-1.0, 1.0)
        self.validator.setDecimals(3)

        self.AimVecX = QLineEdit()
        self.AimVecX.setFixedWidth(70)
        self.AimVecX.setText("0.000")
        self.AimVecX.setValidator(self.validator)

        self.AimVecY = QLineEdit()
        self.AimVecY.setFixedWidth(70)
        self.AimVecY.setText("1.000")
        self.AimVecY.setValidator(self.validator)

        self.AimVecZ = QLineEdit()
        self.AimVecZ.setFixedWidth(70)
        self.AimVecZ.setText("0.000")
        self.AimVecZ.setValidator(self.validator)

        self.upVecX = QLineEdit()
        self.upVecX.setFixedWidth(70)
        self.upVecX.setText("0.000")
        self.upVecX.setValidator(self.validator)

        self.upVecY = QLineEdit()
        self.upVecY.setFixedWidth(70)
        self.upVecY.setText("0.000")
        self.upVecY.setValidator(self.validator)

        self.upVecZ = QLineEdit()
        self.upVecZ.setFixedWidth(70)
        self.upVecZ.setText("1.000")
        self.upVecZ.setValidator(self.validator)

        self.forArmTwistIndexLe = QSpinBox()

        self.apply = QPushButton("Apply")

    def createLayout(self):
        self.JointHbox = QHBoxLayout()
        self.JointHbox.addWidget(self.forArmLowerArmLe)
        self.JointHbox.addWidget(self.forArmWristTag)
        self.JointHbox.addWidget(self.forArmWristLe)

        self.AimVecHbox = QHBoxLayout()
        self.AimVecHbox.setSpacing(2)
        self.AimVecHbox.addWidget(self.AimVecX)
        self.AimVecHbox.addWidget(self.AimVecY)
        self.AimVecHbox.addWidget(self.AimVecZ)

        self.UpVectorHbox = QHBoxLayout()
        self.UpVectorHbox.setSpacing(2)
        self.UpVectorHbox.addWidget(self.upVecX)
        self.UpVectorHbox.addWidget(self.upVecY)
        self.UpVectorHbox.addWidget(self.upVecZ)

        self.applyHbox = QHBoxLayout()
        self.applyHbox.addStretch()
        self.applyHbox.addWidget(self.apply)

        self.froArmFormLayout = QFormLayout()
        self.froArmFormLayout.addRow("Lower Arm Joint:", self.JointHbox)
        self.froArmFormLayout.addRow("Joint Axis:", self.AimVecHbox)
        self.froArmFormLayout.addRow("Up Axis:", self.UpVectorHbox)
        self.froArmFormLayout.addRow("Twist Joint Number:", self.forArmTwistIndexLe)
        self.froArmFormLayout.addRow("", self.applyHbox)

        self.GroupBox = QGroupBox()
        self.GroupBox.setLayout(self.froArmFormLayout)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.GroupBox)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.mainLayout)

    def createConnections(self):
        pass


class MainWindow(QDialog):
    def __init__(self, parent=mayaMainWindow()):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("JBDMuscle")
        self.resize(QSize(380, 470))

        self.createWidgets()
        self.createLayout()

    def createWidgets(self):
        self.forarmCollapWdg = CollapsibleWidget("Forarm Twist")
        self.forarmWin = ForArmTwistTab()
        self.forarmCollapWdg.addWidget(self.forarmWin)

    def createLayout(self):
        self.bodyWdg = QWidget()

        self.bodyLayout = QVBoxLayout(self.bodyWdg)
        self.bodyLayout.setContentsMargins(0, 0, 0, 0)
        self.bodyLayout.setSpacing(3)
        self.bodyLayout.setAlignment(Qt.AlignTop)
        self.bodyLayout.addWidget(self.forarmCollapWdg)

        self.bodyScrollArea = QScrollArea()
        self.bodyScrollArea.setWidgetResizable(False)
        self.bodyScrollArea.setWidget(self.bodyWdg)

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.bodyWdg)











