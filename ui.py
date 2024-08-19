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
import maya.cmds as cm
from . import helper_joints
from . import muscle_group


def mayaMainWindow():
    mainWindowPtr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(mainWindowPtr), QWidget)


def createMuscleGroup(groupType, inputs):
    if groupType == "Trapezius":
        return muscle_group.TrapGroup(inputs[0], inputs[1], inputs[2], inputs[3])
    elif groupType == "Lats":
        return muscle_group.LatsGroup(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4])
    elif groupType == "Deltoid":
        return muscle_group.DeltoidGroup(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5])
    elif groupType == "Arm":
        return muscle_group.ArmMuscleGroup(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4], inputs[5])
    elif groupType == "Pectoralis":
        return muscle_group.PectoralisGroup(inputs[0], inputs[1], inputs[2], inputs[3], inputs[4])


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


class MuscleCreateWidget(QWidget):
    def __init__(self, listItem, listWidget, create=None, mirror=None, rebuild=None,
                 muscleUnit=None, groupType=None, inputs=None, parent=None):

        super(MuscleCreateWidget, self).__init__(parent)
        self.parentWidget = listWidget
        self.listItem = listItem

        if create:
            self.skeleton_group = createMuscleGroup(groupType, inputs)
            self.skeleton_group.add()
        if mirror:
            self.skeleton_group = muscleUnit.mirror()
        if rebuild:
            self.skeleton_group = muscleUnit

        mainLayout = QVBoxLayout()
        groupBox = QGroupBox(self.skeleton_group.muscleName)
        groupBoxLayout = QVBoxLayout(groupBox)
        mainLayout.addWidget(groupBox)
        self.setLayout(mainLayout)

        self.treeWidget = QTreeWidget()
        self.treeWidget.setFixedHeight(100)
        self.treeWidget.setHeaderLabels(["Muscle Units"])
        groupBoxLayout.addWidget(self.treeWidget)
        self.populateTreeWidget()

        # add right click event
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_menu)

        self.treeWidget.itemSelectionChanged.connect(self.onItemSelectionChanged)
        self.treeWidget.itemDoubleClicked.connect(self.onItemDoubleClicked)

    def populateTreeWidget(self):
        icon_path = QPixmap(":kinJoint.png")
        bone_icon = QIcon(icon_path)

        for unit in self.skeleton_group.muscleUnitGroup:
            muscleGroup = unit.muscleName
            muscleOrigin = unit.muscleOrigin
            muscleInsertion = unit.muscleInsertion
            muscleOffset = unit.muscleOffset
            Jomuscle = unit.JOmuscle

            muscleGroup = QTreeWidgetItem(self.treeWidget, [muscleGroup])

            origin_item = QTreeWidgetItem(muscleGroup, [muscleOrigin])
            origin_item.setData(0, Qt.UserRole, muscleOrigin)
            origin_item.setIcon(0, bone_icon)

            insertion_item = QTreeWidgetItem(muscleGroup, [muscleInsertion])
            insertion_item.setData(0, Qt.UserRole, muscleInsertion)
            insertion_item.setIcon(0, bone_icon)

            offset_item = QTreeWidgetItem(muscleGroup, [muscleOffset])
            offset_item.setData(0, Qt.UserRole, muscleOffset)
            offset_item.setIcon(0, bone_icon)

            jomuscle_item = QTreeWidgetItem(muscleGroup, [Jomuscle])
            jomuscle_item.setData(0, Qt.UserRole, Jomuscle)
            jomuscle_item.setIcon(0, bone_icon)

    def open_menu(self, position):
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        build_action = menu.addAction("Build")
        delete_action = menu.addAction("Delete")

        edit_action.triggered.connect(self.skeleton_group.edit)
        build_action.triggered.connect(self.skeleton_group.build)
        delete_action.triggered.connect(self.deleteItem)

        menu.exec_(self.mapToGlobal(position))

    def deleteItem(self):
        self.skeleton_group.delete()
        if self.parentWidget and self.listItem:
            row = self.parentWidget.row(self.listItem)
            self.parentWidget.takeItem(row)
        self.deleteLater()

    def onItemSelectionChanged(self):
        cm.select(clear=True)
        selected_items = self.treeWidget.selectedItems()
        if selected_items:
            selected_item = selected_items[0]
            joint = selected_item.data(0, Qt.UserRole)
            cm.select(joint)

    def onItemDoubleClicked(self, item):  # 添加处理双击事件的方法
        joint = item.data(0, Qt.UserRole)
        cm.select(joint)
        cm.GraphEditor()


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


class MuscleMirrorSubWindow(QDialog):
    def __init__(self, parent=None):
        super(MuscleMirrorSubWindow, self).__init__(parent)
        self.setWindowTitle("Mirror")
        self.setGeometry(300, 300, 200, 150)

        mainLayout = QVBoxLayout()

        self.muscleName = QLineEdit()
        self.axisCBX = QComboBox()
        self.axisCBX.addItems(["x", "y", "z"])
        self.sideCBX = QComboBox()
        self.sideCBX.addItems(["L", "R"])

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        self.formLayout = QFormLayout()
        self.formLayout.addRow("Name", self.muscleName)
        self.formLayout.addRow("Axis", self.axisCBX)
        self.formLayout.addRow("Side", self.sideCBX)
        mainLayout.addLayout(self.formLayout)
        mainLayout.addWidget(self.buttons)

        self.setLayout(mainLayout)

        self.createConnections()

    def createConnections(self):
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def getMirrorInputs(self):
        return([self.muscleName.text(), self.axisCBX.currentText(), self.sideCBX.currentText()])


class MuscleGroupWindow(QDialog):
    def __init__(self, parent=None):
        super(MuscleGroupWindow, self).__init__(parent)

        self.createWidgets()
        self.createLayout()
        self.createConnections()

    def createWidgets(self):
        self.listWidget = QListWidget()

        self.addMuscleBtn = QPushButton("Add Muscle Group")
        self.mirrorBtn = QPushButton("Mirror")

        self.fileLabel = QLabel("File Path:")
        self.filePathLe = QLineEdit()
        self.selectPathBtn = QPushButton()
        self.selectPathBtn.setIcon(QIcon(":fileOpen.png"))

        self.importFileBtn = QPushButton("Import")
        self.exportFileBtn = QPushButton("Export")

    def createLayout(self):
        self.buttonHLO = QHBoxLayout()
        self.buttonHLO.addWidget(self.addMuscleBtn)
        self.buttonHLO.addWidget(self.mirrorBtn)

        self.fileLayout = QHBoxLayout()
        self.fileLayout.addWidget(self.fileLabel)
        self.fileLayout.addWidget(self.filePathLe)
        self.fileLayout.addWidget(self.selectPathBtn)

        self.fileSaveLayout = QHBoxLayout()
        self.fileSaveLayout.addStretch()
        self.fileSaveLayout.addWidget(self.importFileBtn)
        self.fileSaveLayout.addWidget(self.exportFileBtn)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.listWidget)
        mainLayout.addLayout(self.buttonHLO)
        mainLayout.addLayout(self.fileLayout)
        mainLayout.addLayout(self.fileSaveLayout)
        self.setLayout(mainLayout)

    def createConnections(self):
        self.addMuscleBtn.clicked.connect(self.openSubWindow)
        self.mirrorBtn.clicked.connect(self.openMirrorWindow)
        self.selectPathBtn.clicked.connect(self.setFilePath)
        self.exportFileBtn.clicked.connect(self.openFilfExportWindow)
        self.importFileBtn.clicked.connect(self.openFileImportWindow)

    def setFilePath(self):
        filePath = self.filePathLe.text()
        if not filePath:
            filePath = cm.internalVar(userAppDir=True)

        filePath = QFileDialog.getExistingDirectory(self, "Select Directory", filePath)
        if filePath:
            self.filePathLe.setText(filePath)

    def openFilfExportWindow(self):
        filePath = self.filePathLe.text()
        if not filePath:
            filePath = cm.internalVar(userAppDir=True)

        muscleList = []
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File As", filePath, "JSON Files (*.json)")
        for i in range(self.listWidget.count()):
            listItem = self.listWidget.item(i)
            muscleWidget = self.listWidget.itemWidget(listItem)
            muscleList.append(muscleWidget.skeleton_group)

        muscle_group.exportMuscles(filePath, *muscleList)

    def openFileImportWindow(self):
        filePath = self.filePathLe.text()
        if not filePath:
            filePath = cm.internalVar(userAppDir=True)

        filePath, self.selectedFilter = QFileDialog.getOpenFileName(self, "Select File", filePath)
        muscleInstances = muscle_group.importMuscles(filePath)
        self.reloadMuscleWidgets(muscleInstances)

    def reloadMuscleWidgets(self, muscleInstances):
        for muscleUnit in muscleInstances:
            listItem = QListWidgetItem(self.listWidget)
            listItemWidget = MuscleCreateWidget(rebuild=True, muscleUnit=muscleUnit,
                                                listItem=listItem, listWidget=self.listWidget)
            listItem.setSizeHint(listItemWidget.sizeHint())

            self.listWidget.addItem(listItem)
            self.listWidget.setItemWidget(listItem, listItemWidget)

    def openSubWindow(self):
        self.subWindow = MuscleCreateSubWindow(self)
        self.subWindow.show()
        self.subWindow.accepted.connect(self.getSubWindowAccept)

    def openMirrorWindow(self):
        self.mirrorWindow = MuscleMirrorSubWindow(self)
        self.mirrorWindow.show()
        self.mirrorWindow.accepted.connect(self.getMirrorWindowAccept)

    def getMirrorWindowAccept(self):
        selectedItems = self.listWidget.selectedItems()
        if not selectedItems:
            return

        selectedItem = selectedItems[0]
        listItemWidget = self.listWidget.itemWidget(selectedItem)
        if not listItemWidget:
            return

        mirrorInputs = self.mirrorWindow.getMirrorInputs()
        self.addMirrorItem(listItemWidget.skeleton_group, mirrorInputs)

    def getSubWindowAccept(self):
        selectedMuscleType = self.subWindow.getSelectedMuscleType()
        dataInputs = self.subWindow.getSelectedMuscleInputs()
        self.addLayoutItem(selectedMuscleType, dataInputs)

    def addLayoutItem(self, selectedMuscleType, dataInputs):
        listItem = QListWidgetItem(self.listWidget)
        listItemWidget = MuscleCreateWidget(create=True, groupType=selectedMuscleType, inputs=dataInputs,
                                            listItem=listItem, listWidget=self.listWidget)
        listItem.setSizeHint(listItemWidget.sizeHint())

        self.listWidget.addItem(listItem)
        self.listWidget.setItemWidget(listItem, listItemWidget)

    def addMirrorItem(self, muscleUnit, dataInputs):
        listItem = QListWidgetItem(self.listWidget)
        listItemWidget = MuscleCreateWidget(mirror=True, muscleUnit=muscleUnit, inputs=dataInputs,
                                            listItem=listItem, listWidget=self.listWidget)
        listItem.setSizeHint(listItemWidget.sizeHint())

        self.listWidget.addItem(listItem)
        self.listWidget.setItemWidget(listItem, listItemWidget)


class CustomButton(QPushButton):
    def __init__(self, parent=None):
        super(CustomButton, self).__init__(parent)
        self.setText("")
        self.setStyleSheet("""
           QPushButton {
                border-radius: 25px;       /* 圆形按钮的半径 */
                padding: 0px;               /* 内边距 */
                color: white;               /* 字体颜色 */
                font-size: 16px;            /* 字体大小 */
                min-width: 50px;           /* 最小宽度 */
                min-height: 50px;          /* 最小高度 */
                max-width: 50px;           /* 最大宽度 */
                max-height: 50px;          /* 最大高度 */
                text-align: center;         /* 文字居中对齐 */
                line-height: 100px;         /* 文字行高 */
            }
            QPushButton:hover {
                background-color: #45a049; /* 悬停时背景颜色 */
            }
            QPushButton:pressed {
                background-color: #367c39; /* 按下时背景颜色 */
            }
        """)
        icon_path = ":/proximityWrap.png"  # Ensure the icon path is correct
        pixmap = QPixmap(icon_path)
        pixmap = pixmap.scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(120, 120))


class ImageBackgroundWidget(QWidget):
    def __init__(self, image_path, parent=None):
        super(ImageBackgroundWidget, self).__init__(parent)
        self.setFixedSize(372, 1025)
        self.setGeometry(100, 100, 372, 1025)
        self.image_path = image_path

    def set_image(self, image_path):
        """Update the background image."""
        self.image_path = image_path
        self.update()  # Request a repaint to apply the new image

    def paintEvent(self, event):
        """Override the paint event to draw the background image."""
        painter = QPainter(self)
        pixmap = QPixmap(self.image_path)

        # Scale the pixmap to fit the widget's size
        scaled_pixmap = pixmap.scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(self.rect(), scaled_pixmap)



class AnimationJointWindow(QWidget):
    def __init__(self, parent=None):
        super(AnimationJointWindow, self).__init__(parent)
        image_path = 'C:/Users/zenzl/Documents/maya/scripts/JBDMuscle/data/qwe.png'
        background_widget = ImageBackgroundWidget(image_path)

        # Create buttons
        aa = CustomButton()

        # Create a layout and add buttons to it
        layout = QVBoxLayout()
        layout.addWidget(aa)
        # Set the layout to the background widget
        background_widget.setLayout(layout)

        # Set the background widget as the main layout for the dialog
        main_layout = QVBoxLayout()
        main_layout.addWidget(background_widget)
        self.setLayout(main_layout)



class MainWindow(QDialog):
    def __init__(self, parent=mayaMainWindow()):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("JBDMuscle")
        self.resize(QSize(500, 600))

        self.createWidgets()
        self.createLayout()

    def createWidgets(self):
        self.tabWidget = QTabWidget()
        self.animationJointPage = AnimationJointWindow()
        self.helpJointPage = HelperJointWindow()
        self.muscleGroupPage = MuscleGroupWindow()
        self.tabWidget.addTab(self.animationJointPage, "Animation Joint")
        self.tabWidget.addTab(self.helpJointPage, "Helper Joints")
        self.tabWidget.addTab(self.muscleGroupPage, "Muscle Group")

    def createLayout(self):
        self.mainLayout = QVBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.addWidget(self.tabWidget)
        self.setLayout(self.mainLayout)





