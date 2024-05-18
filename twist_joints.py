import maya.cmds as cmds

def CopyJoint(inputJoint, group=None, name="copy"):
    cmds.select(clear=True)
    copyJoint = cmds.joint(n="{0}_{1}".format(group, name), position=(0, 0, 0))
    cmds.delete(cmds.parentConstraint(inputJoint, copyJoint, mo=False, weight=1))
    cmds.parent(copyJoint, inputJoint)
    cmds.makeIdentity(copyJoint, apply=True)
    return copyJoint


def forArmTwist(lowerArm=None, wrist=None, jointCount=3, aimVec=1):

    elbowTwistBaseJoint = CopyJoint(lowerArm, group=lowerArm, name="TwistBase")
    elbowTwistValueJoint = CopyJoint(elbowTwistBaseJoint, group=lowerArm, name="TwistValue")
    armLength = cmds.getAttr("{0}.ty".format(wrist))

    for i in range(1, jointCount + 1):
        twistJoints = CopyJoint(lowerArm, group=lowerArm, name="Twist{0}".format(i))
        cmds.setAttr("{0}.ty".format(twistJoints), armLength / jointCount * i)
        orCons = cmds.orientConstraint(elbowTwistBaseJoint, elbowTwistValueJoint, twistJoints, mo=False, weight=1)[0]
        cmds.setAttr("{0}.{1}W0".format(orCons, elbowTwistBaseJoint), 1 / jointCount * (jointCount - i))
        cmds.setAttr("{0}.{1}W1".format(orCons, elbowTwistValueJoint), 1 / jointCount * i)
        cmds.setAttr("{0}.interpType".format(orCons), 2)

    cmds.aimConstraint(wrist, elbowTwistValueJoint, aimVector=[0, aimVec, 0], upVector=[0, 0, 1],
                       worldUpType="objectrotation", worldUpObject=wrist, worldUpVector=[0, 0, 1])


def upperArmTwist(upperArm=None, lowerArm=None, jointCount=3, aimVec=1, upVec=-1):

    armLength = cmds.getAttr("{0}.ty".format(lowerArm))
    upperArmCounterTwist = CopyJoint(upperArm, group=upperArm, name="CounterTwist")
    upperArmTwistUpJoint = CopyJoint(upperArm, group=upperArm, name="Up")
    cmds.setAttr("{0}.tx".format(upperArmTwistUpJoint), -armLength / 3)
    clavicleJoint = cmds.listRelatives(upperArm, p=True)[0]
    cmds.parent(upperArmTwistUpJoint, clavicleJoint)

    upperArmTwistBaseJoint = CopyJoint(upperArmCounterTwist, group=upperArm, name="TwistBase")
    upperArmTwistValueJoint = CopyJoint(upperArmCounterTwist, group=upperArm, name="TwistValue")

    for i in range(0, jointCount):
        twistJoints = CopyJoint(upperArm, group=upperArm, name="Twist{0}".format(i + 1))
        cmds.setAttr("{0}.ty".format(twistJoints), armLength / jointCount * i)
        orCons = cmds.orientConstraint(upperArmTwistBaseJoint, upperArmTwistValueJoint, twistJoints, mo=False, weight=1)[0]
        if i == 0:
            cmds.setAttr("{0}.{1}W0".format(orCons, upperArmTwistBaseJoint), 0.9)
            cmds.setAttr("{0}.{1}W1".format(orCons, upperArmTwistValueJoint), 0.1)
        else:
            cmds.setAttr("{0}.{1}W0".format(orCons, upperArmTwistBaseJoint), 1 / jointCount * (jointCount - i))
            cmds.setAttr("{0}.{1}W1".format(orCons, upperArmTwistValueJoint), 1 / jointCount * i)

        cmds.setAttr("{0}.interpType".format(orCons), 2)

    cmds.aimConstraint(lowerArm, upperArmCounterTwist, aimVector=[0, aimVec, 0], upVector=[upVec, 0, 0],
                       worldUpType="object", worldUpObject=upperArmTwistUpJoint)
    cmds.aimConstraint(lowerArm, upperArmTwistValueJoint, aimVector=[0, aimVec, 0], upVector=[0, 0, 1],
                       worldUpType="objectrotation", worldUpObject=upperArm, worldUpVector=[0, 0, 1])

    return upperArmTwistUpJoint


def shoulderCounterFilp(upperArm, lowerArm, armUpJoint, rotationAxis="z"):
    clavicleJo = cmds.listRelatives(upperArm, parent=True)[0]

    jointDn = CopyJoint(upperArm, group=upperArm, name="Dn")
    lengh = cmds.getAttr("{0}.ty".format(upperArm)) / 2
    cmds.setAttr("{0}.ty".format(jointDn), lengh)

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

    cmds.setAttr("{0}.rz".format(upperArm), -90)
    tempPos = cmds.xform(posTempJoint, translation=True, ws=True, q=True)
    cmds.xform(armUpJoint, ws=True, translation=(tempPos[0], tempPos[1], tempPos[2]))
    for index, axis in enumerate("XYZ"):
        cmds.setDrivenKeyframe("{0}.translate{1}".format(armUpJoint, axis),
                               currentDriver="{0}.outputX".format(DotNode))

    cmds.setAttr("{0}.rz".format(upperArm), 90)
    tempPos = cmds.xform(posTempJoint, translation=True, ws=True, q=True)
    cmds.xform(armUpJoint, ws=True, translation=(tempPos[0], tempPos[1], tempPos[2]))
    for index, axis in enumerate("XYZ"):
        cmds.setDrivenKeyframe("{0}.translate{1}".format(armUpJoint, axis),
                               currentDriver="{0}.outputX".format(DotNode))

    cmds.setAttr("{0}.rz".format(upperArm), 0)
    cmds.delete(posTempJoint)


def autoCreate(upperArm, lowerArm, wrist, rotationAxis="z", jointCount=3):
    forArmTwist(lowerArm=lowerArm, wrist=wrist, jointCount=jointCount)
    createArmUpJoint = upperArmTwist(upperArm=upperArm, lowerArm=lowerArm, jointCount=jointCount)
    shoulderCounterFilp(upperArm=upperArm, lowerArm=lowerArm, armUpJoint=createArmUpJoint, rotationAxis=rotationAxis)


