import maya.cmds as cmds
import maya.api.OpenMaya as om


def createJnt(jointName, parent=None, radius=1.0, **kwargs):
    cmds.select(clear=True)
    jnt = cmds.joint(name=jointName, **kwargs)
    cmds.setAttr("{0}.radius".format(jnt), radius)
    if parent:
        cmds.parent(jnt, parent)
        cmds.setAttr("{0}.t".format(jnt), 0, 0, 0)
        cmds.setAttr("{0}.r".format(jnt), 0, 0, 0)
        cmds.setAttr("{0}.jo".format(jnt), 0, 0, 0)
    return jnt


class MuscleJoint(object):
    def __init__(self, muscleName, muscleLength,
                       compressionFactor, stretchFactor,
                       stretchOffset=None, compressionOffset=None):
        self.muscleName = muscleName
        self.compressionFactor = compressionFactor
        self.stretchFactor = stretchFactor
        self.stretchOffset = stretchOffset
        self.compressionOffset = compressionOffset
        self.allJoints = []
        self.originAttachObj = None
        self.insertionAttachObj = None

        self.create(muscleName, muscleLength, stretchOffset=stretchOffset, compressionOffset=compressionOffset)
        self.edit()

    def create(self, muscleName, muscleLength, stretchOffset=None, compressionOffset=None):

        self.muscleOrigin = createJnt("{0}_muscleOrigin".format(muscleName))

        self.muscleInsertion = createJnt("{0}_muscleInsertion".format(muscleName))

        cmds.setAttr("{0}.tx".format(self.muscleInsertion), muscleLength)
        cmds.delete(cmds.aimConstraint(self.muscleInsertion, self.muscleOrigin,
                                       aimVector=[0, 1, 0], upVector=[1, 0, 0],
                                       worldUpType="scene", offset=[0, 0, 0], weight=1))

        self.muscleBase = createJnt("{0}_muscleBase".format(muscleName), radius=0.5)
        cmds.pointConstraint(self.muscleOrigin, self.muscleBase, mo=False, weight=1)

        self.mainAimConstraint = cmds.aimConstraint(self.muscleInsertion, self.muscleBase,
                                                    aimVector=[0, 1, 0], upVector=[1, 0, 0],
                                                    worldUpType="objectrotation", worldUpObject=self.muscleOrigin,
                                                    worldUpVector=[1, 0, 0])

        self.muscleTip = createJnt("{0}_muscleTip".format(muscleName), radius=0.5, parent=self.muscleBase)
        cmds.pointConstraint(self.muscleInsertion, self.muscleTip, mo=False, weight=1)

        self.muscleDriver = createJnt("{0}_muscleDriver".format(muscleName), radius=0.5, parent=self.muscleBase)
        self.mainPointConstraint = cmds.pointConstraint(self.muscleBase, self.muscleTip, self.muscleDriver,
                                                        mo=False, weight=1)

        cmds.parent(self.muscleBase, self.muscleOrigin)

        self.muscleOffset = createJnt("{0}_muscleOffset".format(muscleName), radius=0.75, parent=self.muscleDriver)
        self.JOmuscle = createJnt("{0}_JOmuscle".format(muscleName), radius=1.0, parent=self.muscleOffset)
        cmds.setAttr("{0}.segmentScaleCompensate".format(self.JOmuscle), 0)

        self.allJoints.extend([self.muscleOrigin, self.muscleInsertion, self.muscleBase, self.muscleTip,
                               self.muscleDriver, self.muscleOffset, self.JOmuscle])

        self.muscleNodes = []

        self.addSDK()



    def edit(self):

        def createSpaceLocator(scaleValue, **kwargs):
            loc = cmds.spaceLocator(**kwargs)[0]
            for axis in "XYZ":
                cmds.setAttr("{0}.localScale{1}".format(loc, axis), scaleValue)
            return loc

        cmds.setAttr("{0}.overrideEnabled".format(self.muscleOrigin), 1)
        cmds.setAttr("{0}.overrideDisplayType".format(self.muscleOrigin), 1)
        cmds.setAttr("{0}.overrideEnabled".format(self.muscleInsertion), 1)
        cmds.setAttr("{0}.overrideDisplayType".format(self.muscleInsertion), 1)

        self.ptConstraintsTmp = []
        self.originLoc = createSpaceLocator(0.25, name="{0}_muscleOrigin_loc".format(self.muscleName))
        if self.originAttachObj:
            cmds.parent(self.originLoc, self.originAttachObj)
        cmds.delete(cmds.pointConstraint(self.muscleOrigin, self.originLoc, mo=False, w=True))
        self.ptConstraintsTmp.append(cmds.pointConstraint(self.originLoc, self.muscleOrigin, mo=False, w=True)[0])

        self.insertionLoc = createSpaceLocator(0.25, name="{0}_muscleInsertion_loc".format(self.muscleName))
        if self.insertionAttachObj:
            cmds.parent(self.insertionLoc, self.insertionAttachObj)

        cmds.aimConstraint(self.insertionLoc, self.originLoc,
                           aimVector=[0, 1, 0], upVector=[1, 0, 0],
                           worldUpType="scene", offset = [0, 0, 0], weight=1)
        cmds.aimConstraint(self.insertionLoc, self.originLoc,
                           aimVector=[0, -1, 0], upVector=[1, 0, 0],
                           worldUpType="scene", offset = [0, 0, 0], weight=1)

        cmds.delete(cmds.pointConstraint(self.muscleInsertion, self.insertionLoc, mo=False, w=True))
        self.ptConstraintsTmp.append(cmds.pointConstraint(self.insertionLoc, self.muscleInsertion, mo=False, w=True)[0])

        driverGrp = cmds.group(name="{0}_muscleCenter_grp".format(self.muscleName), empty=True)

        self.centerLoc = createSpaceLocator(0.25, name="{0}_muscleCenter_loc".format(self.muscleName))
        cmds.parent(self.centerLoc, driverGrp)
        cmds.delete(cmds.pointConstraint(self.muscleDriver, driverGrp, mo=False, w=True))
        cmds.parent(driverGrp, self.originLoc)
        cmds.pointConstraint(self.originLoc, self.insertionLoc, driverGrp, mo=True, w=True)
        cmds.setAttr("{0}.r".format(driverGrp), 0, 0, 0)
        cmds.delete(self.mainPointConstraint)
        self.ptConstraintsTmp.append(cmds.pointConstraint(self.centerLoc, self.muscleDriver, mo=False, w=True)[0])

    def update(self):
        pass

    def addSDK(self, stretchOffset=None, compressionOffset=None):
        pass

























