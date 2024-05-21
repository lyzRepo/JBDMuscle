import maya.cmds as cmds
import maya.api.OpenMaya as om
import math


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

    def __init__(self, muscleName, muscleLength, compressionFactor, stretchFactor,
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
                           worldUpType="scene", offset=[0, 0, 0], weight=1)
        cmds.aimConstraint(self.insertionLoc, self.originLoc,
                           aimVector=[0, -1, 0], upVector=[1, 0, 0],
                           worldUpType="scene", offset=[0, 0, 0], weight=1)

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

        for ptConstraintsTmp in self.ptConstraintsTmp:
            if cmds.objExists(ptConstraintsTmp):
                cmds.delete(ptConstraintsTmp)

        for loc in [self.originLoc, self.insertionLoc, self.centerLoc]:
            if cmds.objExists(loc):
                cmds.delete(loc)

        cmds.setAttr("{0}.overrideEnabled".format(self.muscleOrigin), 0)
        cmds.setAttr("{0}.overrideDisplayType".format(self.muscleOrigin), 0)
        cmds.setAttr("{0}.overrideEnabled".format(self.muscleInsertion), 0)
        cmds.setAttr("{0}.overrideDisplayType".format(self.muscleInsertion), 0)

        cmds.delete(self.mainAimConstraint)

        self.mainPointConstraint = cmds.pointConstraint(self.muscleBase, self.muscleTip, self.muscleDriver,
                                                        mo=True, weight=1)

        cmds.delete(cmds.aimConstraint(self.muscleInsertion, self.muscleOrigin,
                                       aimVector=[0, 1, 0], upVector=[1, 0, 0],
                                       worldUpType="scene", offset=[0, 0, 0], weight=1))

        self.mainAimConstraint = cmds.aimConstraint(self.muscleInsertion, self.muscleBase,
                                                    aimVector=[0, 1, 0], upVector=[1, 0, 0],
                                                    worldUpType="objectrotation", worldUpObject=self.muscleOrigin,
                                                    worldUpVector=[1, 0, 0])

        animCurveNodes = cmds.ls(cmds.listConnections(self.JOmuscle, s=True, d=False),
                                 type=("animCurveUU", "animCurveUL"))
        cmds.delete(animCurveNodes)
        self.addSDK()

    def addSDK(self, stretchOffset=None, compressionOffset=None):
        xzSquashScale = math.sqrt(1.0 / self.compressionFactor)
        xzStretchScale = math.sqrt(1.0 / self.stretchFactor)

        if stretchOffset is None:
            stretchOffset = [0.0, 0.0, 0.0]
        if compressionOffset is None:
            compressionOffset = [0.0, 0.0, 0.0]

        restLength = cmds.getAttr("{0}.translateY".format(self.muscleTip))

        for index, axis in enumerate("XYZ"):

            cmds.setAttr("{0}.scale{1}".format(self.JOmuscle, axis), 1.0)
            cmds.setAttr("{0}.translate{1}".format(self.JOmuscle, axis), 0.0)
            cmds.setDrivenKeyframe("{0}.scale{1}".format(self.JOmuscle, axis),
                                   currentDriver="{0}.translateY".format(self.muscleTip))
            cmds.setDrivenKeyframe("{0}.translate{1}".format(self.JOmuscle, axis),
                                   currentDriver="{0}.translateY".format(self.muscleTip))

            cmds.setAttr("{0}.translateY".format(self.muscleTip), restLength * self.stretchFactor)
            if axis == "Y":
                cmds.setAttr("{0}.scale{1}".format(self.JOmuscle, axis), self.stretchFactor)
            else:
                cmds.setAttr("{0}.scale{1}".format(self.JOmuscle, axis), xzStretchScale)
                cmds.setAttr("{0}.translate{1}".format(self.JOmuscle, axis), stretchOffset[index])

            cmds.setDrivenKeyframe("{0}.scale{1}".format(self.JOmuscle, axis),
                                   currentDriver="{0}.translateY".format(self.muscleTip))
            cmds.setDrivenKeyframe("{0}.translate{1}".format(self.JOmuscle, axis),
                                   currentDriver="{0}.translateY".format(self.muscleTip))

            cmds.setAttr("{0}.translateY".format(self.muscleTip), restLength * self.compressionFactor)
            if axis == "Y":
                cmds.setAttr("{0}.scale{1}".format(self.JOmuscle, axis), self.compressionFactor)
            else:
                cmds.setAttr("{0}.scale{1}".format(self.JOmuscle, axis), xzSquashScale)
                cmds.setAttr("{0}.translate{1}".format(self.JOmuscle, axis), compressionOffset[index])

            cmds.setDrivenKeyframe("{0}.scale{1}".format(self.JOmuscle, axis),
                                   currentDriver="{0}.translateY".format(self.muscleTip))
            cmds.setDrivenKeyframe("{0}.translate{1}".format(self.JOmuscle, axis),
                                   currentDriver="{0}.translateY".format(self.muscleTip))

            cmds.setAttr("{0}.translateY".format(self.muscleTip), restLength)

    def delete(self):
        self.update()
        if cmds.objExists(self.muscleOrigin):
            cmds.delete(self.muscleOrigin)
        if cmds.objExists(self.muscleInsertion):
            cmds.delete(self.muscleInsertion)
        for node in self.muscleNodes:
            if cmds.objExists(node):
                cmds.delete(node)

    @classmethod
    def createFromAttachObj(cls, muscleName, originAttachObj, insertionAttachObj,
                            compressionFactor=1.0, stretchFactor=1.0,
                            stretchOffset=None, compressionOffset=None):

        originPos = om.MVector(cmds.xform(originAttachObj, translation=True, ws=True, query=True))
        insertionPos = om.MVector(cmds.xform(insertionAttachObj, translation=True, ws=True, query=True))

        muscleLength = om.MVector(insertionPos - originPos).length()
        muscleJointGrp = cls(muscleName, muscleLength, compressionFactor, stretchFactor,
                             stretchOffset=stretchOffset, compressionOffset=compressionOffset)

        muscleJointGrp.originAttachObj = originAttachObj
        muscleJointGrp.insertionAttachObj = insertionAttachObj

        cmds.delete(cmds.pointConstraint(originAttachObj, muscleJointGrp.originLoc, weight=1, mo=False))
        cmds.delete(cmds.pointConstraint(insertionAttachObj, muscleJointGrp.insertionLoc, weight=1, mo=False))
        cmds.parent(muscleJointGrp.muscleOrigin, originAttachObj)
        cmds.parent(muscleJointGrp.originLoc, originAttachObj)
        cmds.parent(muscleJointGrp.muscleInsertion, insertionAttachObj)
        cmds.parent(muscleJointGrp.insertionLoc, insertionAttachObj)
        return muscleJointGrp


def mirror(muscleJointGrp, newMuscleName, muscleOrigin, muscleInsertion, mirrorAxis="x"):
    if not isinstance(muscleJointGrp, MuscleJoint):
        return
    originPos = om.MVector(cmds.xform(muscleJointGrp.muscleOrigin, translation=True, ws=True, query=True))
    insertionPos = om.MVector(cmds.xform(muscleJointGrp.muscleInsertion, translation=True, ws=True, query=True))
    centerPos = om.MVector(cmds.xform(muscleJointGrp.muscleDriver, translation=True, ws=True, query=True))

    if mirrorAxis == "x":
        mirrorOriginPos = om.MVector(-originPos.x, originPos.y, originPos.z)
        mirrorInsertionPos = om.MVector(-insertionPos.x, insertionPos.y, insertionPos.z)
        mirrorCenterPos = om.MVector(-centerPos.x, centerPos.y, centerPos.z)
    elif mirrorAxis == "y":
        mirrorOriginPos = om.MVector(originPos.x, -originPos.y, originPos.z)
        mirrorInsertionPos = om.MVector(insertionPos.x, -insertionPos.y, insertionPos.z)
        mirrorCenterPos = om.MVector(centerPos.x, -centerPos.y, centerPos.z)
    elif mirrorAxis == "z":
        mirrorOriginPos = om.MVector(originPos.x, originPos.y, -originPos.z)
        mirrorInsertionPos = om.MVector(insertionPos.x, insertionPos.y, -insertionPos.z)
        mirrorCenterPos = om.MVector(centerPos.x, centerPos.y, -centerPos.z)
    else:
        raise RuntimeError("Invalid axis, should be in 'xyz'")

    muscleLength = om.MVector(insertionPos - originPos).length()

    mirrorMuscleGrp = MuscleJoint(newMuscleName, muscleLength,
                                  muscleJointGrp.compressionFactor, muscleJointGrp.stretchFactor,
                                  muscleJointGrp.stretchOffset, muscleJointGrp.compressionOffset)
    cmds.xform(mirrorMuscleGrp.originLoc, t=mirrorOriginPos, worldSpace=True)
    cmds.xform(mirrorMuscleGrp.insertionLoc, t=mirrorInsertionPos, worldSpace=True)
    cmds.xform(mirrorMuscleGrp.centerLoc, t=mirrorCenterPos, worldSpace=True)

    cmds.parent(mirrorMuscleGrp.muscleOrigin, muscleOrigin)
    cmds.parent(mirrorMuscleGrp.originLoc, muscleOrigin)
    cmds.parent(mirrorMuscleGrp.muscleInsertion, muscleInsertion)
    cmds.parent(mirrorMuscleGrp.insertionLoc, muscleInsertion)

    return mirrorMuscleGrp
