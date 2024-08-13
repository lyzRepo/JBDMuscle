import maya.cmds as cmds
import json
import os.path
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

    for key, value in kwargs.items():
        if isinstance(value, str):
            kwargs[key] = value.replace(side + "_", prefix + "_")

    mirrorPosList = getMirrorPos(muscleGrp=muscleGrp, mirrorAxis=mirrorAxis,
                                 size=len(muscleGrp.muscleUnitGroup), side=side, prefix=prefix)
    mirrorInstance = groupClass(muscleName, **kwargs)

    mirrorInstance.add()
    for muscle, pos in zip(mirrorInstance.muscleUnitGroup, mirrorPosList):
        cmds.xform(muscle.originLoc, translation=pos[0])
        cmds.xform(muscle.insertionLoc, translation=pos[1])
        cmds.xform(muscle.centerLoc, translation=pos[2])
    mirrorInstance.build()
    return mirrorInstance


def exportMuscles(fileName, *args):
    filePath = os.path.abspath(__file__ + "/../data/{0}.json".format(fileName))

    muscleData = {}
    for group in args:
        muscleData.update(group.serialize())

    with open(filePath, "w") as fp:
        json.dump(muscleData, fp, ensure_ascii=False, indent=4, separators=(",", ":"))


def importMuscles(fileName):
    filePath = os.path.abspath(__file__ + "/../data/{0}.json".format(fileName))
    muscleInstancesGrp = []

    with open(filePath) as fp:
        muscleData = json.load(fp)

    for muscleGroup, attributes in muscleData.items():
        muscleClass = attributes.get("Tag")
        classInputs = attributes.get("inputs")
        dataPos = []
        for key, value in attributes.items():
            if isinstance(value, list):
                dataPos.append(value)
        groupedPos = [dataPos[i:i+3] for i in range(0, len(dataPos), 3)]

        # 动态获取类并创建实例
        if muscleClass in globals():
            muscle_class = globals()[muscleClass]
            newInstance = muscle_class(muscleGroup, **classInputs)
            newInstance.add()
            for muscle, pos in zip(newInstance.muscleUnitGroup, groupedPos):
                cmds.xform(muscle.originLoc, worldSpace=True, translation=pos[0])
                cmds.xform(muscle.insertionLoc, worldSpace=True, translation=pos[1])
                cmds.xform(muscle.centerLoc, worldSpace=True, translation=pos[2])
            newInstance.build()
            muscleInstancesGrp.append(newInstance)
    return muscleInstancesGrp


def addJiggleJoint():
    pass


class BipedMuscles(object):
    def __init__(self, muscleName, tag):
        self.muscleName = muscleName
        self.tag = tag
        self.muscleUnitGroup = []
        self.mirrorJoints = []
        self.muscleCons = []
        self.muscleData = {}

    def __str__(self):
        return self.muscleName

    def add(self):
        pass

    def build(self):
        for muscleUnit in self.muscleUnitGroup:
            muscleUnit.update()

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

    def mirror(self):
        pass

    def jiggleGroup(self):
        for i in self.muscleUnitGroup:
            i.jiggle()

    def serialize(self):
        self.muscleData = {}
        self.muscleData[self.muscleName] = {}
        for muscle in self.muscleUnitGroup:
            muscleOriginPos = cmds.xform(muscle.muscleOrigin, translation=True, query=True, worldSpace=True)
            muscleInsertionPos = cmds.xform(muscle.muscleInsertion, translation=True, query=True, worldSpace=True)
            muscleCenterPos = cmds.xform(muscle.JOmuscle, translation=True, query=True, worldSpace=True)
            self.muscleData[self.muscleName].update({muscle.muscleOrigin: muscleOriginPos})
            self.muscleData[self.muscleName].update({muscle.muscleInsertion: muscleInsertionPos})
            self.muscleData[self.muscleName].update({muscle.JOmuscle: muscleCenterPos})
        self.muscleData[self.muscleName].update({"Tag": self.tag})


class TrapGroup(BipedMuscles):

    def __init__(self, muscleName, back2Joint, clavicleJoint, acromionJoint):
        super().__init__(muscleName, "TrapGroup")
        self.back2Joint = back2Joint
        self.back3Joint = cmds.listRelatives(self.back2Joint, children=True)[0]
        self.neckJoint = cmds.listRelatives(self.back3Joint, children=True)[0]
        self.headJoint = cmds.listRelatives(self.neckJoint, children=True)[0]
        self.clavicleJoint = clavicleJoint
        self.shoulderJoint = cmds.listRelatives(self.clavicleJoint, children=True)[0]
        self.acromionJoint = acromionJoint
        self.scapulaJoint = cmds.listRelatives(self.acromionJoint, children=True)[0]

    def add(self):
        self.trapeziusA = createMuscleUnit(muscleName=self.muscleName + "A",
                                           originJoint=self.neckJoint, originEndJoint=self.headJoint,
                                           insertionJoint=self.clavicleJoint, insertionEndJoint=self.shoulderJoint,
                                           moveFactor=[1 / 2.0, 5 / 6.0])
        self.trapeziusB = createMuscleUnit(muscleName=self.muscleName + "B",
                                           originJoint=self.back3Joint, originEndJoint=self.neckJoint,
                                           insertionJoint=self.acromionJoint, insertionEndJoint=self.scapulaJoint,
                                           moveFactor=[6 / 8.0, 1 / 4.0])
        self.trapeziusC = createMuscleUnit(muscleName=self.muscleName + "C",
                                           originJoint=self.back3Joint, originEndJoint=self.neckJoint,
                                           insertionJoint=self.acromionJoint, insertionEndJoint=self.scapulaJoint,
                                           moveFactor=[1 / 8.0, 3 / 4.0])
        self.muscleUnitGroup = [self.trapeziusA, self.trapeziusB, self.trapeziusC]

    def build(self):
        super().build()
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

    def mirror(self, mirrorAxis="x", side="L", prefix="R"):
        if side == "R":
            prefix = "L"
        return mirrorMuscleGroup(muscleGrp=self, groupClass=TrapGroup, mirrorAxis=mirrorAxis,
                                 side=side, prefix=prefix,
                                 muscleName=self.muscleName.replace(side + "_", prefix + "_"),
                                 back2Joint=self.back2Joint, clavicleJoint=self.clavicleJoint,
                                 acromionJoint=self.acromionJoint)

    def serialize(self):
        muscleData = super().serialize()
        self.muscleData[self.muscleName].update({"inputs": {"back2Joint": self.back2Joint,
                                                            "clavicleJoint": self.clavicleJoint,
                                                            "acromionJoint": self.acromionJoint
                                                            }})
        return self.muscleData


class LatsGroup(BipedMuscles):
    def __init__(self, muscleName, back1Joint, twist2Joint, scapulaJoint, trapCJoint):
        super().__init__(muscleName, "LatsGroup")
        self.back1Joint = back1Joint
        self.back2Joint = cmds.listRelatives(self.back1Joint, children=True)[0]
        self.back3Joint = cmds.listRelatives(self.back2Joint, children=True)[0]
        self.twist2Joint = twist2Joint
        self.shoulderJoint = cmds.listRelatives(self.twist2Joint, parent=True)[0]
        self.scapulaJoint = scapulaJoint
        self.scapulaTipJoint = cmds.listRelatives(self.scapulaJoint, children=True)[0]
        self.trapCJoint = trapCJoint

    def add(self):
        self.latsA = createMuscleUnit(muscleName=self.muscleName + "A",
                                      originJoint=self.back2Joint, originEndJoint=self.back3Joint,
                                      insertionJoint=self.twist2Joint, insertionEndJoint=self.shoulderJoint,
                                      moveFactor=[1 / 2.0, 1 / 2.0])
        self.latsB = createMuscleUnit(muscleName=self.muscleName + "B",
                                      originJoint=self.back1Joint, originEndJoint=self.back2Joint,
                                      insertionJoint=self.twist2Joint, insertionEndJoint=self.shoulderJoint,
                                      moveFactor=[1 / 10.0, 1 / 2.0])
        self.latsC = createMuscleUnit(muscleName=self.muscleName + "C",
                                      originJoint=self.scapulaTipJoint, originEndJoint=self.scapulaJoint,
                                      insertionJoint=self.twist2Joint, insertionEndJoint=self.shoulderJoint,
                                      moveFactor=[1 / 10.0, 1 / 2.0])
        self.muscleUnitGroup = [self.latsA, self.latsB, self.latsC]

    def build(self):
        super().build()

        self.latsBPointCos = cmds.pointConstraint(self.back3Joint, self.latsB.muscleOffset,
                                                  mo=True, weight=True, skip="y")
        self.latsAPointCos = cmds.pointConstraint(self.latsB.JOmuscle, self.trapCJoint, self.latsA.muscleOffset,
                                                  mo=True, weight=True)
        self.muscleCons = [self.latsAPointCos, self.latsBPointCos]

    def mirror(self, mirrorAxis="x", side="L", prefix="R"):
        if side == "R":
            prefix = "L"
        return mirrorMuscleGroup(muscleGrp=self, groupClass=LatsGroup, mirrorAxis=mirrorAxis,
                                 side=side, prefix=prefix,
                                 muscleName=self.muscleName.replace(side + "_", prefix + "_"),
                                 back1Joint=self.back1Joint, twist2Joint=self.twist2Joint,
                                 scapulaJoint=self.scapulaJoint, trapCJoint=self.trapCJoint)

    def serialize(self):
        muscleData = super().serialize()
        self.muscleData[self.muscleName].update({"inputs": {"back1Joint": self.back1Joint,
                                                            "twist2Joint": self.twist2Joint,
                                                            "scapulaJoint": self.scapulaJoint,
                                                            "trapCJoint": self.trapCJoint
                                                            }})
        return self.muscleData


class DeltoidGroup(BipedMuscles):
    def __init__(self, muscleName, clavicleJoint, upperArmJoint, twist1Joint, twist2Joint, acromionJoint):
        super().__init__(muscleName, "DeltoidGroup")
        self.clavicleJoint = clavicleJoint
        self.upperArmJoint = upperArmJoint
        self.twist1Joint = twist1Joint
        self.twist2Joint = twist2Joint
        self.acromionJoint = acromionJoint
        self.sacpulaJoint = cmds.listRelatives(self.acromionJoint, children=True)[0]

    def add(self):
        self.deltoidA = createMuscleUnit(muscleName=self.muscleName + "A",
                                         originJoint=self.clavicleJoint, originEndJoint=self.upperArmJoint,
                                         insertionJoint=self.twist2Joint, insertionEndJoint=self.upperArmJoint,
                                         moveFactor=[5 / 6.0, 0.0])
        self.deltoidB = createMuscleUnit(muscleName=self.muscleName + "B",
                                         originJoint=self.acromionJoint, originEndJoint=self.acromionJoint,
                                         insertionJoint=self.twist2Joint, insertionEndJoint=self.upperArmJoint,
                                         moveFactor=[1.0, 0.0])
        self.deltoidC = createMuscleUnit(muscleName=self.muscleName + "C",
                                         originJoint=self.sacpulaJoint, originEndJoint=self.acromionJoint,
                                         insertionJoint=self.twist2Joint, insertionEndJoint=self.upperArmJoint,
                                         moveFactor=[5 / 6.0, 0.0])
        self.muscleUnitGroup = [self.deltoidA, self.deltoidB, self.deltoidC]

    def build(self):
        for deltoidPart in self.muscleUnitGroup:
            deltoidPart.update()
            cmds.delete(deltoidPart.mainAimConstraint)
            deltoidPart.mainAimConstraint = cmds.aimConstraint(deltoidPart.muscleInsertion,
                                                               deltoidPart.muscleBase, mo=True,
                                                               aimVector=[0, 1, 0], upVector=[1, 0, 0],
                                                               worldUpType="objectrotation",
                                                               worldUpObject=self.twist1Joint,
                                                               worldUpVector=[1, 0, 0])
        self.deltoidBPointCons = cmds.pointConstraint(self.deltoidA.JOmuscle, self.deltoidC.JOmuscle,
                                                      self.deltoidB.muscleOffset, mo=True, weight=1)
        self.deltoidCPointCons = cmds.pointConstraint(self.upperArmJoint, self.deltoidC.JOmuscle,
                                                      mo=True, weight=1, skip=['x', 'y'])

        self.muscleCons = [self.deltoidBPointCons, self.deltoidCPointCons]

    def mirror(self, mirrorAxis="x", side="L", prefix="R"):
        if side == "R":
            prefix = "L"
        return mirrorMuscleGroup(muscleGrp=self, groupClass=DeltoidGroup, mirrorAxis=mirrorAxis,
                                 side=side, prefix=prefix,
                                 muscleName=self.muscleName.replace(side + "_", prefix + "_"),
                                 clavicleJoint=self.clavicleJoint, upperArmJoint=self.upperArmJoint,
                                 twist1Joint=self.twist1Joint, twist2Joint=self.twist2Joint,
                                 acromionJoint=self.acromionJoint)

    def serialize(self):
        muscleData = super().serialize()
        self.muscleData[self.muscleName].update({"inputs": {"clavicleJoint": self.clavicleJoint,
                                                            "upperArmJoint": self.upperArmJoint,
                                                            "twist1Joint": self.twist1Joint,
                                                            "twist2Joint": self.twist2Joint,
                                                            "acromionJoint": self.acromionJoint
                                                            }})
        return self.muscleData


class ArmMuscleGroup(BipedMuscles):
    def __init__(self, muscleName, upArmTwsitJoint, lowArmTwsitJoint, twistBaseJoint, twistValueJoint, acromionJoint):
        super().__init__(muscleName, "ArmMuscleGroup")
        self.upArmTwsitJoint = upArmTwsitJoint
        self.upperArmJoint = cmds.listRelatives(self.upArmTwsitJoint, parent=True)[0]
        self.lowArmTwsitJoint = lowArmTwsitJoint
        self.lowArmJoint = cmds.listRelatives(self.lowArmTwsitJoint, parent=True)[0]
        self.acromionJoint = acromionJoint
        self.sacpulaJoint = cmds.listRelatives(self.acromionJoint, children=True)[0]
        self.twistBaseJoint = twistBaseJoint
        self.twistValueJoint = twistValueJoint

    def add(self):
        self.armMuscleA = createMuscleUnit(muscleName=self.muscleName + "A",
                                           originJoint=self.upArmTwsitJoint, originEndJoint=self.upperArmJoint,
                                           insertionJoint=self.lowArmTwsitJoint,
                                           insertionEndJoint=self.lowArmTwsitJoint,
                                           moveFactor=[0.5, 0.0])
        self.armMuscleB = createMuscleUnit(muscleName=self.muscleName + "B",
                                           originJoint=self.sacpulaJoint, originEndJoint=self.acromionJoint,
                                           insertionJoint=self.lowArmJoint, insertionEndJoint=self.lowArmTwsitJoint,
                                           moveFactor=[4 / 6.0, 0.2])
        self.muscleUnitGroup = [self.armMuscleA, self.armMuscleB]

    def build(self):
        super().build()

        self.armMuscleBPointCons = cmds.orientConstraint(self.twistBaseJoint, self.twistValueJoint,
                                                         self.armMuscleB.muscleOrigin, mo=True, weight=0.5)
        self.armMuscleAParnetCons = cmds.parentConstraint(self.upperArmJoint, self.armMuscleA.muscleOffset,
                                                          mo=True, weight=True, skipTranslate=['x', 'y'],
                                                          skipRotate=['x', 'y', 'z'])
        self.armMuscleBParentCons = cmds.parentConstraint(self.upperArmJoint, self.armMuscleB.muscleOffset,
                                                          mo=True, weight=True, skipTranslate=['x', 'y'],
                                                          skipRotate=['x', 'y', 'z'])
        self.muscleCons = [self.armMuscleBPointCons, self.armMuscleAParnetCons, self.armMuscleBParentCons]

    def mirror(self, mirrorAxis="x", side="L", prefix="R"):
        if side == "R":
            prefix = "L"
        return mirrorMuscleGroup(muscleGrp=self, groupClass=ArmMuscleGroup, mirrorAxis=mirrorAxis,
                                 side=side, prefix=prefix,
                                 muscleName=self.muscleName.replace(side + "_", prefix + "_"),
                                 upArmTwsitJoint=self.upArmTwsitJoint, lowArmTwsitJoint=self.lowArmTwsitJoint,
                                 twistBaseJoint=self.twistBaseJoint, twistValueJoint=self.twistValueJoint,
                                 acromionJoint=self.acromionJoint)

    def serialize(self):
        muscleData = super().serialize()
        self.muscleData[self.muscleName].update({"inputs": {"upArmTwsitJoint": self.upArmTwsitJoint,
                                                            "lowArmTwsitJoint": self.lowArmTwsitJoint,
                                                            "twistBaseJoint": self.twistBaseJoint,
                                                            "twistValueJoint": self.twistValueJoint,
                                                            "acromionJoint": self.acromionJoint
                                                            }})
        return self.muscleData


class PectoralisGroup(BipedMuscles):

    def __init__(self, muscleName, back3Joint, clavicleJoint, upperarmJoint, twist2Joint):
        super().__init__(muscleName, "PectoralisGroup")
        self.back3Joint = back3Joint
        self.clavicleJoint = clavicleJoint
        self.upperarmJoint = upperarmJoint
        self.twist2Joint = twist2Joint

    def add(self):
        self.pectoralisA = createMuscleUnit(muscleName=self.muscleName + "A",
                                            originJoint=self.back3Joint, originEndJoint=self.back3Joint,
                                            insertionJoint=self.twist2Joint, insertionEndJoint=self.upperarmJoint,
                                            moveFactor=[1.0, 1 / 2.0])
        self.pectoralisB = createMuscleUnit(muscleName=self.muscleName + "B",
                                            originJoint=self.clavicleJoint, originEndJoint=self.upperarmJoint,
                                            insertionJoint=self.twist2Joint, insertionEndJoint=self.upperarmJoint,
                                            moveFactor=[1/4.0, 1 / 2.0])
        self.muscleUnitGroup = [self.pectoralisA, self.pectoralisB]

    def build(self):
        super().build()
        self.muscleCons = []

    def mirror(self, mirrorAxis="x", side="L", prefix="R"):
        if side == "R":
            prefix = "L"
        return mirrorMuscleGroup(muscleGrp=self, groupClass=PectoralisGroup, mirrorAxis=mirrorAxis,
                                 side=side, prefix=prefix,
                                 muscleName=self.muscleName.replace(side + "_", prefix + "_"),
                                 back3Joint=self.back3Joint, clavicleJoint=self.clavicleJoint,
                                 upperarmJoint=self.upperarmJoint, twist2Joint=self.twist2Joint)

    def serialize(self):
        muscleData = super().serialize()
        self.muscleData[self.muscleName].update({"inputs": {"back3Joint": self.back3Joint,
                                                            "clavicleJoint": self.clavicleJoint,
                                                            "upperarmJoint": self.upperarmJoint,
                                                            "twist2Joint": self.twist2Joint
                                                            }})
        return self.muscleData
