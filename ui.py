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
from . import muscle_group


def mayaMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mainWindowPtr), QWidget)


def createMuscleGroup(groupType, inputs):
    if groupType == "Trapezius":
        return muscle_group.TrapGroup(inputs[0], inputs[1], inputs[2], inputs[3])
    elif groupType == "Lats":
        return muscle_group.LatsGroup(*inputs)
    elif groupType == "Deltoid":
        return muscle_group.DeltoidGroup(*inputs)
    elif groupType == "Arm":
        return muscle_group.ArmMuscleGroup(*inputs)
    elif groupType == "Pectoralis":
        return muscle_group.PectoralisGroup(*inputs)


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


class LayoutWidget(QWidget):
    def __init__(self, groupType, inputs, parent=None):
        super(LayoutWidget, self).__init__(parent)
        mainLayout = QVBoxLayout()
        groupBox = QGroupBox(groupType)
        groupBoxLayout = QVBoxLayout(groupBox)
        mainLayout.addWidget(groupBox)
        self.setLayout(mainLayout)
        self.skeleton_group = createMuscleGroup(groupType, inputs)
        self.skeleton_group.add()

        # add right click event
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)

    def open_menu(self, position):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        build_action = menu.addAction("Build")
        delete_action = menu.addAction("Delete")
        mirror_action = menu.addAction("mirror")

        # 连接每个菜单项到对应的槽函数
        edit_action.triggered.connect(self.skeleton_group.edit)
        build_action.triggered.connect(self.skeleton_group.build)
        delete_action.triggered.connect(self.skeleton_group.delete)

        menu.exec_(self.mapToGlobal(position))

    def perform_action(self, action_name):
        print(f"{action_name} action triggered")


class MuscleCreateSubWindow(QDialog):
    def __init__(self, parent=None):
        super(MuscleCreateSubWindow, self).__init__(parent)
        self.setWindowTitle("Create Muscle Group")
        self.setGeometry(300, 300, 200, 150)

        self.createWidgets()
        self.createLayout()
        self.createConnections()

    def createWidgets(self):
        self.mainLabel = QLabel("Select Layout Type:")
        self.mainCmb = QComboBox()
        self.mainCmb.addItems(["Trapezius", "Lats", "Deltoid", "Arm", "Pectoralis"])
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.trapMuscleNameLe = QLineEdit()
        self.trapBack2JointLe = QLineEdit()
        self.trapClavicleJointLe = QLineEdit()
        self.trapAcromionJointLe = QLineEdit()

        self.LatsMuscleNameLe = QLineEdit()
        self.LatsBack1JointLe = QLineEdit()
        self.LatsTwist2JointLe = QLineEdit()
        self.LatsScapulaJointLe = QLineEdit()
        self.LatsTrapCJointLe = QLineEdit()

        self.DeltoidMuscleNameLe = QLineEdit()
        self.DeltoidClavicleJointLe = QLineEdit()
        self.DeltoidUpperArmJointLe = QLineEdit()
        self.DeltoidTwist1JointLe = QLineEdit()
        self.DeltoidTwist2JointLe = QLineEdit()
        self.DeltoidAcromionJointLe = QLineEdit()

        self.ArmMuscleNameLe = QLineEdit()
        self.ArmUppearmTwistJointLe = QLineEdit()
        self.ArmLowerarmTwistJointLe = QLineEdit()
        self.ArmTwistBaseJointLe = QLineEdit()
        self.ArmTwistValueJointLe = QLineEdit()
        self.ArmAcromionJointLe = QLineEdit()

        self.PectoralisMuscleNameLe = QLineEdit()
        self.PectoralisBack3JointLe = QLineEdit()
        self.PectoralisClavicleJointLe = QLineEdit()
        self.PectoralisUpperarmJointLe = QLineEdit()
        self.PectoralisTwist2JointLe = QLineEdit()

    def createLayout(self):
        self.trapWidget = QWidget()
        self.trapFormLayout = QFormLayout()
        self.trapFormLayout.addRow("Muscle Name:", self.trapMuscleNameLe)
        self.trapFormLayout.addRow("Back2 Joint:", self.trapBack2JointLe)
        self.trapFormLayout.addRow("Clavicle Joint:", self.trapClavicleJointLe)
        self.trapFormLayout.addRow("Acromion Joint:", self.trapAcromionJointLe)
        self.trapWidget.setLayout(self.trapFormLayout)

        self.LatsWidget = QWidget()
        self.LatsFormLayout = QFormLayout()
        self.LatsFormLayout.addRow("Muscle Name:", self.LatsMuscleNameLe)
        self.LatsFormLayout.addRow("Back1 Joint:", self.LatsBack1JointLe)
        self.LatsFormLayout.addRow("UpperArm Twist2 Joint:", self.LatsTwist2JointLe)
        self.LatsFormLayout.addRow("Scapula Joint:", self.LatsScapulaJointLe)
        self.LatsFormLayout.addRow("TrapC Joint:", self.LatsTrapCJointLe)
        self.LatsWidget.setLayout(self.LatsFormLayout)

        self.DeltoidWidget = QWidget()
        self.DeltoidFormLayout = QFormLayout()
        self.DeltoidFormLayout.addRow("Muscle Name:", self.DeltoidMuscleNameLe)
        self.DeltoidFormLayout.addRow("Clavicle Joint:", self.DeltoidClavicleJointLe)
        self.DeltoidFormLayout.addRow("UpperArm Joint:", self.DeltoidUpperArmJointLe)
        self.DeltoidFormLayout.addRow("UpperArm Twist1 Joint:", self.DeltoidTwist1JointLe)
        self.DeltoidFormLayout.addRow("UpperArm Twist2 Joint:", self.DeltoidTwist2JointLe)
        self.DeltoidFormLayout.addRow("Acromion Joint:", self.DeltoidAcromionJointLe)
        self.DeltoidWidget.setLayout(self.DeltoidFormLayout)

        self.ArmWidget = QWidget()
        self.ArmFormLayout = QFormLayout()
        self.ArmFormLayout.addRow("Muscle Name:", self.ArmMuscleNameLe)
        self.ArmFormLayout.addRow("UpperArm Twist1 Joint:", self.ArmUppearmTwistJointLe)
        self.ArmFormLayout.addRow("LowerArm Twist1 Joint:", self.ArmLowerarmTwistJointLe)
        self.ArmFormLayout.addRow("UpperArm TwistBase Joint:", self.ArmTwistBaseJointLe)
        self.ArmFormLayout.addRow("UpperArm TwistValue Joint:", self.ArmTwistValueJointLe)
        self.ArmFormLayout.addRow("Acromion Joint:", self.ArmAcromionJointLe)
        self.ArmWidget.setLayout(self.ArmFormLayout)

        self.PectoralisWidget = QWidget()
        self.PectoralisFormLayout = QFormLayout()
        self.PectoralisFormLayout.addRow("Muscle Name:", self.PectoralisMuscleNameLe)
        self.PectoralisFormLayout.addRow("Back3 Joint:", self.PectoralisBack3JointLe)
        self.PectoralisFormLayout.addRow("Clavicle Joint:", self.PectoralisClavicleJointLe)
        self.PectoralisFormLayout.addRow("UpperArm Joint:", self.PectoralisUpperarmJointLe)
        self.PectoralisFormLayout.addRow("UpperArm Twist2 Joint:", self.PectoralisTwist2JointLe)
        self.PectoralisWidget.setLayout(self.PectoralisFormLayout)

        self.stackedWidget = QStackedWidget()
        self.stackedWidget.addWidget(self.trapWidget)
        self.stackedWidget.addWidget(self.LatsWidget)
        self.stackedWidget.addWidget(self.DeltoidWidget)
        self.stackedWidget.addWidget(self.ArmWidget)
        self.stackedWidget.addWidget(self.PectoralisWidget)

        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.addWidget(self.mainLabel)
        self.mainLayout.addWidget(self.mainCmb)
        self.mainLayout.addWidget(self.stackedWidget)
        self.mainLayout.addWidget(self.buttons)

        self.setLayout(self.mainLayout)

    def createConnections(self):
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.mainCmb.currentIndexChanged.connect(self.stackedWidget.setCurrentIndex)

    def getInputText(self, formLayout):
        texts = []
        for i in range(formLayout.count()):
            # 获取每一行的Widget
            labelItem = formLayout.itemAt(i, QFormLayout.LabelRole)
            fieldItem = formLayout.itemAt(i, QFormLayout.FieldRole)

            if labelItem and fieldItem:
                labelWidget = labelItem.widget()
                fieldWidget = fieldItem.widget()

            formatted_text = fieldWidget.text()
            texts.append(formatted_text)

        return texts

    def getSelectedMuscleType(self):
        return self.mainCmb.currentText()

    def getSelectedMuscleInputs(self):
        currentWidget = self.stackedWidget.currentWidget()
        currentLayout = currentWidget.layout()
        inputTexts = self.getInputText(currentLayout)

        return inputTexts


class MuscleGroupWindow(QDialog):
    def __init__(self, parent=None):
        super(MuscleGroupWindow, self).__init__(parent)

        mainLayout = QVBoxLayout(self)

        self.listWidget = QListWidget()
        mainLayout.addWidget(self.listWidget)

        self.addLayoutBtn = QPushButton("Add Layout")
        self.addLayoutBtn.clicked.connect(self.openSubWindow)
        mainLayout.addWidget(self.addLayoutBtn)

        self.setLayout(mainLayout)

    def openSubWindow(self):
        self.subWindow = MuscleCreateSubWindow(self)
        self.subWindow.show()
        self.subWindow.accepted.connect(self.getSubWindowAccept)

    def getSubWindowAccept(self):
        selectedMuscleType = self.subWindow.getSelectedMuscleType()
        dataInputs = self.subWindow.getSelectedMuscleInputs()
        self.addLayoutItem(selectedMuscleType, dataInputs)

    def addLayoutItem(self, selectedMuscleType, dataInputs):
        listItemWidget = LayoutWidget(selectedMuscleType, dataInputs)
        listItem = QListWidgetItem(self.listWidget)
        listItem.setSizeHint(listItemWidget.sizeHint())
        self.listWidget.addItem(listItem)
        self.listWidget.setItemWidget(listItem, listItemWidget)


class MainWindow(QDialog):
    def __init__(self, parent=mayaMainWindow()):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("JBDMuscle")
        self.resize(QSize(500, 600))

        self.createWidgets()
        self.createLayout()

        self.initUI()

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

    def initUI(self):
        # 加载之前保存的状态或布局
        self.loadState()

    def closeEvent(self, event):
        # 隐藏窗口而不是关闭
        self.hide()
        event.ignore()

    def loadState(self):
        # 从文件或其他地方加载之前保存的状态
        pass

    def saveState(self):
        # 将当前状态保存到文件或其他地方
        pass




