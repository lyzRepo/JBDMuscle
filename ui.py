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


class LayoutWidget(QWidget):
    def __init__(self, layout, title=None, parent=None):
        super(LayoutWidget, self).__init__(parent)

        main_layout = QVBoxLayout(self)

        # add group box for input layout
        groupBox = QGroupBox(title)
        groupBoxLayout = QVBoxLayout(groupBox)
        groupBoxLayout.addLayout(layout)
        groupBox.setLayout(groupBoxLayout)

        # add group box to main layout
        main_layout.addWidget(groupBox)
        self.setLayout(main_layout)

        # add right click event
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)

    def open_menu(self, position):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        build_action = menu.addAction("Build")
        delete_action = menu.addAction("Delete")

        # 连接每个菜单项到对应的槽函数
        edit_action.triggered.connect(lambda: self.perform_action("Edit"))
        build_action.triggered.connect(lambda: self.perform_action("Build"))
        delete_action.triggered.connect(lambda: self.perform_action("Delete"))

        menu.exec_(self.mapToGlobal(position))

    def perform_action(self, action_name):
        print(f"{action_name} action triggered")


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


class UpperArmTwistTab(QWidget):
    def __init__(self):
        super(UpperArmTwistTab, self).__init__()

        self.createWidgets()
        self.createLayout()
        self.createConnections()

    def createWidgets(self):
        self.upperArmLe = QLineEdit()
        self.upperArmLe.setFixedWidth(120)
        self.lowerArmLe = QLineEdit()
        self.lowerArmLe.setFixedWidth(120)

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

        self.jntUpAxisX = QLineEdit()
        self.jntUpAxisX.setFixedWidth(70)
        self.jntUpAxisX.setText("0.000")
        self.jntUpAxisX.setValidator(self.validator)

        self.jntUpAxisY = QLineEdit()
        self.jntUpAxisY.setFixedWidth(70)
        self.jntUpAxisY.setText("0.000")
        self.jntUpAxisY.setValidator(self.validator)

        self.jntUpAxisZ = QLineEdit()
        self.jntUpAxisZ.setFixedWidth(70)
        self.jntUpAxisZ.setText("1.000")
        self.jntUpAxisZ.setValidator(self.validator)

        self.upperArmTwistIndexLe = QSpinBox()

        self.apply = QPushButton("Apply")

    def createLayout(self):
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

        self.jntUpAxisHbox = QHBoxLayout()
        self.jntUpAxisHbox.setSpacing(2)
        self.jntUpAxisHbox.addWidget(self.jntUpAxisX)
        self.jntUpAxisHbox.addWidget(self.jntUpAxisY)
        self.jntUpAxisHbox.addWidget(self.jntUpAxisZ)

        self.applyHbox = QHBoxLayout()
        self.applyHbox.addStretch()
        self.applyHbox.addWidget(self.apply)

        self.upArmFormLayout = QFormLayout()
        self.upArmFormLayout.addRow("Upper Arm Joint:", self.upperArmLe)
        self.upArmFormLayout.addRow("Lower Arm Joint:", self.lowerArmLe)
        self.upArmFormLayout.addRow("Joint Axis:", self.AimVecHbox)
        self.upArmFormLayout.addRow("Up Axis:", self.UpVectorHbox)
        self.upArmFormLayout.addRow("Joint Up Axis:", self.jntUpAxisHbox)
        self.upArmFormLayout.addRow("Twist Joint Number:", self.upperArmTwistIndexLe)
        self.upArmFormLayout.addRow("", self.applyHbox)

        self.GroupBox = QGroupBox()
        self.GroupBox.setLayout(self.upArmFormLayout)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.GroupBox)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.mainLayout)

    def createConnections(self):
        pass


class ShoulderCounterFilpTab(QWidget):
    def __init__(self):
        super(ShoulderCounterFilpTab, self).__init__()

        self.createWidgets()
        self.createLayout()
        self.createConnections()

    def createWidgets(self):
        self.upperArmLe = QLineEdit()
        self.lowerArmLe = QLineEdit()
        self.armUpjointLe = QLineEdit()
        self.lowerArmTag = QLabel("Lower Arm Joint:")
        self.armUpjointTag = QLabel("Arm Up Joint:")

        self.validator = QDoubleValidator()
        self.validator.setRange(-1.0, 1.0)
        self.validator.setDecimals(3)

        self.jointAxisX = QLineEdit()
        self.jointAxisX.setFixedWidth(70)
        self.jointAxisX.setText("0.000")
        self.jointAxisX.setValidator(self.validator)

        self.jointAxisY = QLineEdit()
        self.jointAxisY.setFixedWidth(70)
        self.jointAxisY.setText("1.000")
        self.jointAxisY.setValidator(self.validator)

        self.jointAxisZ = QLineEdit()
        self.jointAxisZ.setFixedWidth(70)
        self.jointAxisZ.setText("0.000")
        self.jointAxisZ.setValidator(self.validator)

        self.rotateAxisCmb = QComboBox()
        self.rotateAxisCmb.addItems(["x", "y", "z"])

        self.apply = QPushButton("Apply")

    def createLayout(self):
        self.JointHbox = QHBoxLayout()
        self.JointHbox.addWidget(self.upperArmLe)
        self.JointHbox.addWidget(self.lowerArmTag)
        self.JointHbox.addWidget(self.lowerArmLe)

        self.jointAxisHbox = QHBoxLayout()
        self.jointAxisHbox.setSpacing(2)
        self.jointAxisHbox.addWidget(self.jointAxisX)
        self.jointAxisHbox.addWidget(self.jointAxisY)
        self.jointAxisHbox.addWidget(self.jointAxisZ)

        self.applyHbox = QHBoxLayout()
        self.applyHbox.addStretch()
        self.applyHbox.addWidget(self.apply)

        self.shoulderCounterFilpLayout = QFormLayout()
        self.shoulderCounterFilpLayout.addRow("Upper Arm Joint:", self.JointHbox)
        self.shoulderCounterFilpLayout.addRow("Arm Up Joint:", self.armUpjointLe)
        self.shoulderCounterFilpLayout.addRow("Joint Axis:", self.jointAxisHbox)
        self.shoulderCounterFilpLayout.addRow("Joint rotation Axis:", self.rotateAxisCmb)
        self.shoulderCounterFilpLayout.addRow("", self.applyHbox)

        self.GroupBox = QGroupBox()
        self.GroupBox.setLayout(self.shoulderCounterFilpLayout)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(self.GroupBox)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.setLayout(self.mainLayout)

    def createConnections(self):
        pass


class HelperJointWindow(QDialog):
    def __init__(self, parent=None):
        super(HelperJointWindow, self).__init__(parent)

        self.createWidgets()
        self.createLayout()

    def createWidgets(self):
        self.forarmCollapWdg = CollapsibleWidget("Forarm Twist")
        self.forarmWin = ForArmTwistTab()
        self.forarmCollapWdg.addWidget(self.forarmWin)

        self.upperArmCollapWdg = CollapsibleWidget("Upper Arm Twist")
        self.upperArmWin = UpperArmTwistTab()
        self.upperArmCollapWdg.addWidget(self.upperArmWin)

        self.shouldCounterFilpCollapWdg = CollapsibleWidget("Shoulder Counter Filp")
        self.shouldCounterFilpWin = ShoulderCounterFilpTab()
        self.shouldCounterFilpCollapWdg.addWidget(self.shouldCounterFilpWin)

    def createLayout(self):
        self.bodyWdg = QWidget()

        self.bodyLayout = QVBoxLayout(self.bodyWdg)
        self.bodyLayout.setContentsMargins(0, 0, 0, 0)
        self.bodyLayout.setSpacing(5)
        self.bodyLayout.setAlignment(Qt.AlignTop)
        self.bodyLayout.addWidget(self.forarmCollapWdg)
        self.bodyLayout.addWidget(self.upperArmCollapWdg)
        self.bodyLayout.addWidget(self.shouldCounterFilpCollapWdg)

        self.bodyScrollArea = QScrollArea()
        self.bodyScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.bodyScrollArea.setFrameShape(QFrame.NoFrame)
        self.bodyScrollArea.setWidgetResizable(True)
        self.bodyScrollArea.setWidget(self.bodyWdg)

        mainLayout = QVBoxLayout(self)
        mainLayout.addWidget(self.bodyScrollArea)


class MuscleGroupWindow(QDialog):
    def __init__(self, parent=None):
        super(MuscleGroupWindow, self).__init__(parent)

        mainLayout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        mainLayout.addWidget(self.list_widget)

        # 创建布局
        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(QPushButton("Button 1"))
        horizontal_layout.addWidget(QPushButton("Button 2"))

        grid_layout = QVBoxLayout()
        grid_layout.addWidget(QPushButton("Button 1"))
        grid_layout.addWidget(QPushButton("Button 2"))
        grid_layout.addWidget(QPushButton("Button 3"))

        # 添加带有 GroupBox 的布局到 QListWidget
        self.addLayoutItem(horizontal_layout, "Horizontal Layout Group")
        self.addLayoutItem(grid_layout, "Grid Layout Group")

        self.setLayout(mainLayout)

    def addLayoutItem(self, layout, title):
        list_item_widget = LayoutWidget(layout, title)
        list_item = QListWidgetItem(self.list_widget)
        list_item.setSizeHint(list_item_widget.sizeHint())
        self.list_widget.addItem(list_item)
        self.list_widget.setItemWidget(list_item, list_item_widget)

class MainWindow(QDialog):
    def __init__(self, parent=mayaMainWindow()):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("JBDMuscle")
        self.resize(QSize(500, 600))

        self.createWidgets()
        self.createLayout()

    def createWidgets(self):
        self.tabWidget = QTabWidget()

        self.helpJointPage = HelperJointWindow()
        self.muscleGroupPage = MuscleGroupWindow()
        self.tabWidget.addTab(self.helpJointPage, "Helper Joints")
        self.tabWidget.addTab(self.muscleGroupPage, "Muscle Group")

    def createLayout(self):
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.tabWidget)
        self.setLayout(self.mainLayout)




