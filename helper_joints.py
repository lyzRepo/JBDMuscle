import maya.cmds as cmds


def generateScapulaLocs(shoulderJo, back3Jo, neckJo, side="L"):
    shoulderPos = cmds.xform(shoulderJo, translation=True, ws=True, q=True)

    acromionLoc = cmds.spaceLocator(name="{0}_AcromionLoc".format(side))[0]
    cmds.xform(acromionLoc, t=shoulderPos, ws=True)

    scapulaLoc = cmds.spaceLocator(name="{0}_scapulaLoc".format(side))[0]
    cmds.delete(cmds.pointConstraint(back3Jo, neckJo, acromionLoc, scapulaLoc, mo=False, w=True))

    tipLoc = cmds.spaceLocator(name="{0}_tipLoc".format(side))[0]
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
