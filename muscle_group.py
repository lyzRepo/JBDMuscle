import maya.cmds as cmds
import maya.api.OpenMaya as om
from . import muscle_units as mu


def moveJoints(startJoint, endJoint, moveObject, moveFactor=(1, 1)):
    numerator, denominator = moveFactor
    moveFactor = numerator / denominator

    startVector = om.MVector(cmds.xform(startJoint, translation=True, ws=True, q=True))
    endVector = om.MVector(cmds.xform(endJoint, translation=True, ws=True, q=True))
    finalPos = (endVector - startVector) * moveFactor + startVector
    cmds.xform(moveObject, translation=finalPos, ws=True)


def createMuscleUnit(muscleName, originJoint, originEndJoint, insertionJoint, insertionEndJoint, moveFactor):
    muscleUnit = mu.MuscleJoint.createFromAttachObj(muscleName=muscleName, originAttachObj=originJoint,
                                                    insertionAttachObj=insertionJoint,
                                                    compressionFactor=0.5, stretchFactor=1.5)
    moveJoints(startJoint=originJoint, endJoint=originEndJoint,
               moveObject=muscleUnit.originLoc, moveFactor=moveFactor[0])
    moveJoints(startJoint=insertionJoint, endJoint=insertionEndJoint,
               moveObject=muscleUnit.insertionLoc, moveFactor=moveFactor[1])
    return muscleUnit


class TrapeziusGroup(object):

    def __init__(self, muscleName, back2Joint, clavicleJoint, acromionJoint):
        self.muscleName = muscleName
        self.back2Joint = back2Joint
        self.back3Joint = cmds.listRelatives(self.back2Joint, children=True)[0]
        self.neckJoint = cmds.listRelatives(self.back3Joint, children=True)[0]
        self.headJoint = cmds.listRelatives(self.neckJoint, children=True)[0]
        self.clavicleJoint = clavicleJoint
        self.shoulderJoint = cmds.listRelatives(self.clavicleJoint, children=True)[0]
        self.acromionJoint = acromionJoint
        self.scapulaJoint = cmds.listRelatives(self.acromionJoint, children=True)[0]

        self.trapeziusA = createMuscleUnit(muscleName=self.muscleName+"A",
                                           originJoint=self.neckJoint, originEndJoint=self.headJoint,
                                           insertionJoint=self.clavicleJoint, insertionEndJoint=self.shoulderJoint,
                                           moveFactor=[(1, 2), (5, 6)])
        self.trapeziusB = createMuscleUnit(muscleName=self.muscleName+"B",
                                           originJoint=self.back3Joint, originEndJoint=self.neckJoint,
                                           insertionJoint=self.acromionJoint, insertionEndJoint=self.scapulaJoint,
                                           moveFactor=[(6, 8), (1, 4)])
        self.trapeziusC = createMuscleUnit(muscleName=self.muscleName+"C",
                                           originJoint=self.back3Joint, originEndJoint=self.neckJoint,
                                           insertionJoint=self.acromionJoint, insertionEndJoint=self.scapulaJoint,
                                           moveFactor=[(1, 8), (3, 4)])
        self.trapeziusGroup = [self.trapeziusA, self.trapeziusB, self.trapeziusC]

    def trapeziusBuild(self):
        for trapPart in self.trapeziusGroup:
            trapPart.update()

        originalAimCons = cmds.listRelatives(self.trapeziusA.muscleBase, type="aimConstraint")[0]
        if originalAimCons:
            cmds.delete(originalAimCons)

        self.trapAParentCons = cmds.parentConstraint(self.neckJoint, self.headJoint, self.trapeziusA.muscleOrigin,
                                                     mo=True, weight=True)

        self.trapAAimCons = cmds.aimConstraint(self.trapeziusA.muscleInsertion, self.trapeziusA.muscleBase,
                                               aimVector=[0, 1, 0], upVector=[1, 0, 0],
                                               worldUpType="objectrotation",
                                               worldUpObject=self.back3Joint, worldUpVector=[0, 1, 0], mo=True)
        self.trapeziusA.mainAimConstraint = self.trapAAimCons

        self.trapCParentCons = cmds.parentConstraint(self.back2Joint, self.back3Joint, self.trapeziusC.muscleOrigin,
                                                     mo=True, weight=True)
        self.trapConstraints = [self.trapAParentCons, self.trapCParentCons]

    def trapeziusEdit(self):
        if self.trapConstraints:
            for i in self.trapConstraints:
                cmds.delete(i)
        for trapPart in self.trapeziusGroup:
            trapPart.edit()

    def trapeziusDelete(self):
        if self.trapConstraints:
            for i in self.trapConstraints:
                cmds.delete(i)
        for i in self.trapeziusGroup:
            i.delete()


def trapeziusMirror(muscleGrp, back2Joint, clavicleJoint, acromionJoint, mirrorAxis="x", side="L", prefix="R"):
    if not isinstance(muscleGrp, TrapeziusGroup):
        return
    if side == "R":
        prefix = "L"

    locPosList = []
    for muscle, i in zip(muscleGrp.trapeziusGroup, "ABC"):
        tempMuscle = mu.mirror(muscleJointGrp=muscle,
                               newMuscleName="{0}_trapezius{1}".format(prefix, i),
                               muscleOrigin=muscle.originAttachObj,
                               muscleInsertion=muscle.insertionAttachObj.replace(side + "_", prefix + "_"),
                               mirrorAxis=mirrorAxis)

        originPos = cmds.xform(tempMuscle.originLoc, t=True, q=True)
        insertionPos = cmds.xform(tempMuscle.insertionLoc, t=True, q=True)
        centerPos = cmds.xform(tempMuscle.centerLoc, t=True, q=True)
        tempPosList = [originPos, insertionPos, centerPos]
        locPosList.append(tempPosList)
        tempMuscle.delete()

    mirrorInstance = TrapeziusGroup(muscleName="{0}_trapezius".format(prefix), back2Joint=back2Joint,
                                    clavicleJoint=clavicleJoint, acromionJoint=acromionJoint)
    for muscle, pos in zip(mirrorInstance.trapeziusGroup, locPosList):
        cmds.xform(muscle.originLoc, translation=pos[0])
        cmds.xform(muscle.insertionLoc, translation=pos[1])
        cmds.xform(muscle.centerLoc, translation=pos[2])
    return mirrorInstance



