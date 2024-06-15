import maya.cmds as cmds
import maya.api.OpenMaya as om


def duplicateJoint(inputJoint, group=None, name="copy"):
    """
    copy joint, match joint pos and parent to original joint
    :param inputJoint: original joint
    :param group: name prefix
    :param name: joint name
    :return: joint name as str
    """
    # create joint
    cmds.select(clear=True)
    copyJoint = cmds.joint(name="{0}_{1}".format(group, name), position=(0, 0, 0))
    # match transformation
    cmds.matchTransform(copyJoint, inputJoint)
    cmds.parent(copyJoint, inputJoint)
    # freeze rotation to jointOrient
    cmds.makeIdentity(copyJoint, apply=True)
    return copyJoint


def getLength(startJoint, endJoint):
    elbowPos = om.MVector(cmds.xform(startJoint, translation=True, ws=True, q=True))
    wristPos = om.MVector(cmds.xform(endJoint, translation=True, ws=True, q=True))
    armLength = (elbowPos - wristPos).length()
    return armLength


def forArmTwist(lowerArm=None, wrist=None, jointCount=3, aimVec=None, upVector=None):
    """
    :param lowerArm: elbow joint
    :param wrist: wrist joint
    :param jointCount: twist joint count
    :param aimVec: joint orient main axis
    :param upVector: wrist side axis direction
    """
    # default aim axis "y", up axis "z"
    if aimVec is None:
        aimVec = [0, 1, 0]
    if upVector is None:
        upVector = [0, 0, 1]
    # duplicate two joints and get length
    elbowTwistBaseJoint = duplicateJoint(lowerArm, group=lowerArm, name="TwistBase")
    elbowTwistValueJoint = duplicateJoint(elbowTwistBaseJoint, group=lowerArm, name="TwistValue")
    armLength = getLength(lowerArm, wrist)

    for i in range(1, jointCount + 1):
        # copy joint and set offset value
        twistJoints = duplicateJoint(lowerArm, group=lowerArm, name="Twist{0}".format(i))
        offset = armLength / jointCount * i
        # transfer offset to aim vector and move
        jointPos = [element * offset for element in aimVec]
        cmds.xform(twistJoints, translation=jointPos)
        # set orientConstraint and weight percent
        orCons = cmds.orientConstraint(elbowTwistBaseJoint, elbowTwistValueJoint, twistJoints, mo=False, weight=1)[0]
        cmds.setAttr("{0}.{1}W0".format(orCons, elbowTwistBaseJoint), 1 / jointCount * (jointCount - i))
        cmds.setAttr("{0}.{1}W1".format(orCons, elbowTwistValueJoint), 1 / jointCount * i)
        # change constraint interp type to shortest
        cmds.setAttr("{0}.interpType".format(orCons), 2)
    # aimConstraint twistValueJoint by wrist to get wrist twist value
    cmds.aimConstraint(wrist, elbowTwistValueJoint, aimVector=aimVec, upVector=upVector,
                       worldUpType="objectrotation", worldUpObject=wrist, worldUpVector=upVector)


def upperArmTwist(upperArm=None, lowerArm=None, jointCount=3, aimVec=None, upVector=None, jointUpVector=None):
    """
    :param upperArm: shoulder joint
    :param lowerArm: elbow joint
    :param jointCount: twist joint count
    :param aimVec: joint main axis
    :param jointUpVector: up joint offset axis
    :param upVector:
    """
    # default aim axis "y", up axis "z"
    if aimVec is None:
        aimVec = [0, 1, 0]
    if upVector is None:
        upVector = [0, 0, 1]
    if jointUpVector is None:
        jointUpVector = [-1, 0, 0]

    upperArmCounterTwist = duplicateJoint(upperArm, group=upperArm, name="CounterTwist")
    upperArmTwistUpJoint = duplicateJoint(upperArm, group=upperArm, name="Up")
    armLength = getLength(upperArm, lowerArm)
    upJointPos = [element * armLength/3 for element in jointUpVector]
    cmds.xform(upperArmTwistUpJoint, translation=upJointPos)
    clavicleJoint = cmds.listRelatives(upperArm, parent=True)[0]
    cmds.parent(upperArmTwistUpJoint, clavicleJoint)

    upperArmTwistBaseJoint = duplicateJoint(upperArmCounterTwist, group=upperArm, name="TwistBase")
    upperArmTwistValueJoint = duplicateJoint(upperArmCounterTwist, group=upperArm, name="TwistValue")

    for i in range(0, jointCount):
        twistJoints = duplicateJoint(upperArm, group=upperArm, name="Twist{0}".format(i + 1))
        offset = armLength / jointCount * i
        jointPos = [element * offset for element in aimVec]
        cmds.xform(twistJoints, translation=jointPos)

        orCons = cmds.orientConstraint(upperArmTwistBaseJoint, upperArmTwistValueJoint, twistJoints, mo=False, weight=1)[0]
        if i == 0:
            cmds.setAttr("{0}.{1}W0".format(orCons, upperArmTwistBaseJoint), 0.9)
            cmds.setAttr("{0}.{1}W1".format(orCons, upperArmTwistValueJoint), 0.1)
        else:
            cmds.setAttr("{0}.{1}W0".format(orCons, upperArmTwistBaseJoint), 1 / jointCount * (jointCount-i))
            cmds.setAttr("{0}.{1}W1".format(orCons, upperArmTwistValueJoint), 1 / jointCount * i)

        cmds.setAttr("{0}.interpType".format(orCons), 2)

    cmds.aimConstraint(lowerArm, upperArmCounterTwist, aimVector=aimVec, upVector=jointUpVector,
                       worldUpType="object", worldUpObject=upperArmTwistUpJoint)
    cmds.aimConstraint(lowerArm, upperArmTwistValueJoint, aimVector=aimVec, upVector=upVector,
                       worldUpType="objectrotation", worldUpObject=upperArm, worldUpVector=upVector)

    return upperArmTwistUpJoint


def shoulderCounterFilp(upperArm, lowerArm, armUpJoint, jointAxis, rotationAxis="z"):
    # default aim axis "y", up axis "z"
    if jointAxis is None:
        jointAxis = [0, 1, 0]

    clavicleJo = cmds.listRelatives(upperArm, parent=True)[0]

    jointDn = duplicateJoint(upperArm, group=upperArm, name="Dn")
    armLength = getLength(upperArm, lowerArm)
    dnJointPos = [element * armLength/3 for element in jointAxis]
    cmds.xform(jointDn, translation=dnJointPos)

    cmds.setAttr("{0}.r{1}".format(upperArm, rotationAxis), -90)
    cmds.parent(jointDn, clavicleJo)
    cmds.setAttr("{0}.r{1}".format(upperArm, rotationAxis), 0)

    MTMNode = cmds.createNode("multMatrix", name="{0}_MTM".format(upperArm))
    cmds.connectAttr("{0}.worldMatrix[0]".format(jointDn), "{0}.matrixIn[0]".format(MTMNode))
    cmds.connectAttr("{0}.worldInverseMatrix[0]".format(upperArm), "{0}.matrixIn[1]".format(MTMNode))

    DCPMNode = cmds.createNode("decomposeMatrix", name="{0}_DCPM".format(upperArm))
    cmds.connectAttr("{0}.matrixSum".format(MTMNode), "{0}.inputMatrix".format(DCPMNode))

    DotNode = cmds.createNode("vectorProduct", name="{0}_Dot".format(upperArm))
    cmds.connectAttr("{0}.outputTranslate".format(DCPMNode), "{0}.input1".format(DotNode))
    cmds.connectAttr("{0}.translate".format(lowerArm), "{0}.input2".format(DotNode))
    cmds.setAttr("{0}.normalizeOutput".format(DotNode), 1)

    posTempJoint = cmds.duplicate(armUpJoint, name="posTempJoint")[0]
    cmds.parent(posTempJoint, upperArm)

    for index, axis in enumerate("XYZ"):
        cmds.setDrivenKeyframe("{0}.translate{1}".format(armUpJoint, axis),
                               currentDriver="{0}.outputX".format(DotNode))

    cmds.setAttr("{0}.r{1}".format(upperArm, rotationAxis), -90)
    tempPos = cmds.xform(posTempJoint, translation=True, ws=True, q=True)
    cmds.xform(armUpJoint, ws=True, translation=(tempPos[0], tempPos[1], tempPos[2]))
    for index, axis in enumerate("XYZ"):
        cmds.setDrivenKeyframe("{0}.translate{1}".format(armUpJoint, axis),
                               currentDriver="{0}.outputX".format(DotNode))

    cmds.setAttr("{0}.r{1}".format(upperArm, rotationAxis), 90)
    tempPos = cmds.xform(posTempJoint, translation=True, ws=True, q=True)
    cmds.xform(armUpJoint, ws=True, translation=(tempPos[0], tempPos[1], tempPos[2]))
    for index, axis in enumerate("XYZ"):
        cmds.setDrivenKeyframe("{0}.translate{1}".format(armUpJoint, axis),
                               currentDriver="{0}.outputX".format(DotNode))

    cmds.setAttr("{0}.r{1}".format(upperArm, rotationAxis), 0)
    cmds.delete(posTempJoint)


def autoCreate(upperArm, lowerArm, wrist, rotationAxis="z", jointCount=3):
    forArmTwist(lowerArm=lowerArm, wrist=wrist, jointCount=jointCount)
    createArmUpJoint = upperArmTwist(upperArm=upperArm, lowerArm=lowerArm, jointCount=jointCount)
    shoulderCounterFilp(upperArm=upperArm, lowerArm=lowerArm, armUpJoint=createArmUpJoint,
                        rotationAxis=rotationAxis, jointAxis=[0, 1, 0])


def generateScapulaLocs(shoulderJo, back3Jo, neckJo, side="L"):
    shoulderPos = cmds.xform(shoulderJo, translation=True, ws=True, q=True)

    acromionLoc = cmds.spaceLocator(name="{0}_acromionLoc".format(side))[0]
    cmds.xform(acromionLoc, t=shoulderPos, ws=True)

    scapulaLoc = cmds.spaceLocator(name="{0}_scapulaLoc".format(side))[0]
    cmds.delete(cmds.pointConstraint(back3Jo, neckJo, acromionLoc, scapulaLoc, mo=False, w=True))

    tipLoc = cmds.spaceLocator(name="{0}_scapulaTipLoc".format(side))[0]
    cmds.delete(cmds.pointConstraint(acromionLoc, scapulaLoc, tipLoc, mo=False, w=True))
    cmds.delete(cmds.pointConstraint(back3Jo, tipLoc, skip=("x", "z"), mo=False, w=True))


def createScapulaJoints(clavicle, neckJoint, backJoint, oj="yzx", sao="zup", upVec=1):
    loctors = cmds.ls(sl=True)
    locList = [loc.split("Loc")[0] for loc in loctors]
    posList = [cmds.xform(locPos, t=True, ws=True, q=True) for locPos in loctors]

    cmds.select(cl=True)
    boneLis = [cmds.joint(n=loc, p=pos) for loc, pos in zip(locList, posList)]

    for joint in boneLis:
        cmds.joint(joint, e=True, oj=oj, sao=sao, ch=True, zso=True)

    cmds.parent(boneLis[0], clavicle)
    print(boneLis[0])

    cmds.aimConstraint(neckJoint, boneLis[0], aimVector=[0, 1, 0], upVector=[upVec, 0, 0],
                       worldUpType="objectrotation", worldUpVector=[0, 1, 0], worldUpObject=backJoint, mo=True,
                       weight=True)