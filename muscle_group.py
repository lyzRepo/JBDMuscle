import maya.cmds as cmds
import maya.api.OpenMaya as om
from . import muscle_units as mu


def moveJoints(startJoint, endJoint, moveObject, moveFactor=1.0):
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


def getMirrorPos(muscleGrp, mirrorAxis="x", size=3, side="L", prefix="R"):
    locPosList = []
    mirrorSize = list(range(size))
    for muscle, i in zip(muscleGrp.muscleUnitGroup, mirrorSize):
        tempMuscle = mu.mirror(muscleJointGrp=muscle,
                               newMuscleName="{0}_temp{1}".format(prefix, i),
                               muscleOrigin=muscle.originAttachObj.replace(side + "_", prefix + "_"),
                               muscleInsertion=muscle.insertionAttachObj.replace(side + "_", prefix + "_"),
                               mirrorAxis=mirrorAxis)

        originPos = cmds.xform(tempMuscle.originLoc, t=True, q=True)
        insertionPos = cmds.xform(tempMuscle.insertionLoc, t=True, q=True)
        centerPos = cmds.xform(tempMuscle.centerLoc, t=True, q=True)
        tempPosList = [originPos, insertionPos, centerPos]
        locPosList.append(tempPosList)
        tempMuscle.delete()
    return locPosList


def mirrorMuscleGroup(muscleGrp, groupClass, muscleName, mirrorAxis="x", side="L", prefix="R", **kwargs):
    if not isinstance(muscleGrp, groupClass):
        return
    if side == "R":
        prefix = "L"
    mirrorPosList = getMirrorPos(muscleGrp=muscleGrp, mirrorAxis=mirrorAxis,
                                 size=len(muscleGrp.muscleUnitGroup), side=side, prefix=prefix)
    mirrorInstance = groupClass(muscleName="{0}_{1}".format(prefix, muscleName), **kwargs)

    for muscle, pos in zip(mirrorInstance.muscleUnitGroup, mirrorPosList):
        cmds.xform(muscle.originLoc, translation=pos[0])
        cmds.xform(muscle.insertionLoc, translation=pos[1])
        cmds.xform(muscle.centerLoc, translation=pos[2])
    return mirrorInstance


class BipedMuscles(object):
    def __init__(self):
        self.muscleUnitGroup = []
        self.muscleCons = []

    def build(self):
        pass

    def delete(self):
        if self.muscleCons:
            for i in self.muscleCons:
                cmds.delete(i)
        for i in self.muscleUnitGroup:
            i.delete()

    def edit(self):
        if self.muscleCons:
            for i in self.muscleCons:
                cmds.delete(i)
        for i in self.muscleUnitGroup:
            i.edit()

    
class TrapeziusGroup(BipedMuscles):

    def __init__(self, muscleName, back2Joint, clavicleJoint, acromionJoint):
        super().__init__()
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
                                           moveFactor=[1/2.0, 5/6.0])
        self.trapeziusB = createMuscleUnit(muscleName=self.muscleName+"B",
                                           originJoint=self.back3Joint, originEndJoint=self.neckJoint,
                                           insertionJoint=self.acromionJoint, insertionEndJoint=self.scapulaJoint,
                                           moveFactor=[6/8.0, 1/4.0])
        self.trapeziusC = createMuscleUnit(muscleName=self.muscleName+"C",
                                           originJoint=self.back3Joint, originEndJoint=self.neckJoint,
                                           insertionJoint=self.acromionJoint, insertionEndJoint=self.scapulaJoint,
                                           moveFactor=[1/8.0, 3/4.0])
        self.muscleUnitGroup = [self.trapeziusA, self.trapeziusB, self.trapeziusC]

    def build(self):
        for trapPart in self.muscleUnitGroup:
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
        self.muscleCons = [self.trapAParentCons, self.trapCParentCons]


def trapeMirror(muscleGrp, muscleName, back2Joint, clavicleJoint, acromionJoint, mirrorAxis="x", side="L", prefix="R"):
    return mirrorMuscleGroup(muscleGrp=muscleGrp, groupClass=TrapeziusGroup, muscleName=muscleName,
                             mirrorAxis=mirrorAxis, side=side, prefix=prefix,
                             back2Joint=back2Joint, clavicleJoint=clavicleJoint, acromionJoint=acromionJoint)


class LatsGroup(BipedMuscles):
    def __init__(self, muscleName, back1Joint, armJoint, scapulaJoint, trapC):
        super().__init__()
        self.muscleName = muscleName
        self.back1Joint = back1Joint
        self.back2Joint = cmds.listRelatives(self.back1Joint, children=True)[0]
        self.back3Joint = cmds.listRelatives(self.back2Joint, children=True)[0]
        self.armJoint = armJoint
        self.shoulderJoint = cmds.listRelatives(self.armJoint, parent=True)[0]
        self.scapulaJoint = scapulaJoint
        self.scapulaTipJoint = cmds.listRelatives(self.scapulaJoint, children=True)[0]
        self.trapC = trapC

        self.latsA = createMuscleUnit(muscleName=self.muscleName+"A",
                                      originJoint=self.back2Joint, originEndJoint=self.back3Joint,
                                      insertionJoint=self.armJoint, insertionEndJoint=self.shoulderJoint,
                                      moveFactor=[1/2.0, 1/2.0])
        self.latsB = createMuscleUnit(muscleName=self.muscleName+"B",
                                      originJoint=self.back1Joint, originEndJoint=self.back2Joint,
                                      insertionJoint=self.armJoint, insertionEndJoint=self.shoulderJoint,
                                      moveFactor=[1/10.0, 1/2.0])
        self.latsC = createMuscleUnit(muscleName=self.muscleName+"C",
                                      originJoint=self.scapulaTipJoint, originEndJoint=self.scapulaJoint,
                                      insertionJoint=self.armJoint, insertionEndJoint=self.shoulderJoint,
                                      moveFactor=[1/10.0, 1/2.0])
        self.muscleUnitGroup = [self.latsA, self.latsB, self.latsC]

    def build(self):
        for latsPart in self.muscleUnitGroup:
            latsPart.update()

        self.latsBPointCos = cmds.pointConstraint(self.back3Joint, self.latsB.muscleOffset,
                                                  mo=True, weight=True, skip="y")
        self.latsAPointCos = cmds.pointConstraint(self.latsB.JOmuscle, self.trapC, self.latsA.muscleOffset,
                                                  mo=True, weight=True)
        self.muscleCons = [self.latsAPointCos, self.latsBPointCos]


def latsMirror(muscleGrp, muscleName, back1Joint, armJoint, scapulaJoint, trapC, mirrorAxis="x", side="L", prefix="R"):
    return mirrorMuscleGroup(muscleGrp=muscleGrp, groupClass=LatsGroup, muscleName=muscleName,
                             mirrorAxis=mirrorAxis, side=side, prefix=prefix,
                             back1Joint=back1Joint, armJoint=armJoint, scapulaJoint=scapulaJoint, trapC=trapC)


class DeltoidGroup(BipedMuscles):
    def __init__(self, muscleName, clavicleJoint, armJoint, twistJoint, shoulderJoint, acromionJoint, sacpulaJoint):
        super().__init__()
        self.muscleName = muscleName
        self.clavicleJoint = clavicleJoint
        self.armJoint = armJoint
        self.twistJoint = twistJoint
        self.acrominonJoint = acromionJoint
        self.sacpulaJoint = sacpulaJoint
        self.shoulderJoint = shoulderJoint

        self.deltoidA = createMuscleUnit(muscleName=self.muscleName+"A",
                                         originJoint=self.clavicleJoint, originEndJoint=self.armJoint,
                                         insertionJoint=self.twistJoint, insertionEndJoint=self.armJoint,
                                         moveFactor=[5/6.0, 0.0])
        self.deltoidB = createMuscleUnit(muscleName=self.muscleName+"B",
                                         originJoint=self.acrominonJoint, originEndJoint=self.acrominonJoint,
                                         insertionJoint=self.twistJoint, insertionEndJoint=self.armJoint,
                                         moveFactor=[1.0, 0.0])
        self.deltoidC = createMuscleUnit(muscleName=self.muscleName+"C",
                                         originJoint=self.sacpulaJoint, originEndJoint=self.acrominonJoint,
                                         insertionJoint=self.twistJoint, insertionEndJoint=self.armJoint,
                                         moveFactor=[5/6.0, 0.0])
        self.muscleUnitGroup = [self.deltoidA, self.deltoidB, self.deltoidC]

    def build(self):
        for deltoidPart in self.muscleUnitGroup:
            deltoidPart.update()
            cmds.delete(deltoidPart.mainAimConstraint)
            deltoidPart.mainAimConstraint = cmds.aimConstraint(deltoidPart.muscleInsertion,
                                                               deltoidPart.muscleBase, mo=True,
                                                               aimVector=[0, 1, 0], upVector=[1, 0, 0],
                                                               worldUpType="objectrotation",
                                                               worldUpObject=self.shoulderJoint,
                                                               worldUpVector=[1, 0, 0])
        self.deltoidPointCons = cmds.pointConstraint(self.deltoidA.JOmuscle, self.deltoidC.JOmuscle,
                                                     self.deltoidB.muscleOffset, mo=True, weight=1)

        self.muscleCons = [self.deltoidPointCons]


def deltoidMirror(muscleGrp, muscleName, clavicleJoint, armJoint, twistJoint, shoulderJoint, acromionJoint, sacpulaJoint,
                  mirrorAxis="x", side="L", prefix="R"):
    return mirrorMuscleGroup(muscleGrp=muscleGrp, groupClass=DeltoidGroup, muscleName=muscleName,
                             mirrorAxis=mirrorAxis, side=side, prefix=prefix,
                             clavicleJoint=clavicleJoint, armJoint=armJoint, twistJoint=twistJoint,
                             shoulderJoint=shoulderJoint, acromionJoint=acromionJoint, sacpulaJoint=sacpulaJoint)

