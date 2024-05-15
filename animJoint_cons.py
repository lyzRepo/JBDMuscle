import maya.cmds as cmds
from .muscle_units import createJnt

def undo(fun):

    def undo_fun(*args, **kwargs):
        #open undo record
        cmds.undoInfo(openChunk=1)
        #save current selected object
        long_name = cmds.ls(sl=1, l=1)
        #call input function
        fun(*args, **kwargs)
        #keep selection
        cmds.select(cmds.ls(long_name))
        #close undo record
        cmds.undoInfo(closeChunk=1)
    return undo_fun

class AnimationJoint(object):

    def __init__(self, jointName, jointSize=1, jointScale=1):

        self.jointName = jointName
        self.jointSize = jointSize
        self.jointScale = jointScale

        self.allJoints = []

        self.create(jointName, jointSize, jointScale)

    @undo
    def create(self, jointName, jointSize, jointScale=1.0):

        self.spineJointGrp = []
        self.pelvic = createJnt("{0}_pelvic".format(jointName),
                                position=[0, (10*jointSize), 0], radius=jointScale)
        self.back1 = createJnt("{0}_back1".format(jointName),
                               position=[0, (11 * jointSize), 0], radius=jointScale)
        self.back2 = createJnt("{0}_back2".format(jointName),
                               position=[0, (12 * jointSize), 0], radius=jointScale)
        self.back3 = createJnt("{0}_back2".format(jointName),
                               position=[0, (13 * jointSize), 0], radius=jointScale)
        self.neck = createJnt("{0}_neck".format(jointName),
                              position=[0, (14.5 * jointSize), 0], radius=jointScale)
        self.head = createJnt("{0}_head".format(jointName),
                              position=[0, (15.5 * jointSize), (0.2*jointSize)], radius=jointScale)
        self.headEnd = createJnt("{0}_headEnd".format(jointName),
                                 position=[0, (16.5 * jointSize), (0.2*jointSize)], radius=jointScale)
        self.spineJointGrp.extend([self.pelvic, self.back1, self.back2, self.back3, self.neck, self.head, self.headEnd])
        [cmds.parent(self.spineJointGrp[i + 1], joint) for i, joint in enumerate(self.spineJointGrp[:-1])]

        self.legJointGrp = []
        self.hip = createJnt("{0}_L_hip".format(jointName),
                             position=[(1*jointSize), (10 * jointSize), 0], radius=jointScale)
        self.knee = createJnt("{0}_L_knee".format(jointName),
                              position=[(1*jointSize), (5 * jointSize), (0.2*jointSize)], radius=jointScale)
        self.ankle = createJnt("{0}_L_ankle".format(jointName),
                               position=[(1*jointSize), (1 * jointSize), 0], radius=jointScale)
        self.ball = createJnt("{0}_L_ball".format(jointName),
                              position=[(1*jointSize), 0, (1*jointSize)], radius=jointScale)
        self.toe = createJnt("{0}_L_toe".format(jointName),
                             position=[(1*jointSize), 0, (2*jointSize)], radius=jointScale)
        self.legJointGrp.extend([self.hip,  self.knee, self.ankle, self.ball, self.toe])
        [cmds.parent(self.legJointGrp[i + 1], joint) for i, joint in enumerate(self.legJointGrp[:-1])]

        self.armJointGrp = []
        self.clavicle = createJnt("{0}_L_clavicle".format(jointName),
                                  position=[(0.5*jointSize), (14 * jointSize), (0.5*jointSize)], radius=jointScale)
        self.shoulder = createJnt("{0}_L_shoulder".format(jointName),
                                  position=[(2*jointSize), (14 * jointSize), 0], radius=jointScale)
        self.elbow = createJnt("{0}_L_elbow".format(jointName),
                               position=[(4.5*jointSize), (14 * jointSize), -(0.2*jointSize)], radius=jointScale)
        self.wrist = createJnt("{0}_L_wrist".format(jointName),
                               position=[(7.2*jointSize), (14 * jointSize), 0], radius=jointScale)
        self.armJointGrp.extend([self.clavicle, self.shoulder, self.elbow, self.wrist])
        [cmds.parent(self.armJointGrp[i + 1], joint) for i, joint in enumerate(self.armJointGrp[:-1])]

        self.thumbJointGrp = []
        self.thumbMeta = createJnt("{0}_L_thumbMeta".format(jointName),
                                   position=[(7.6*jointSize), (13.9 * jointSize), (0.5 * jointSize)], radius=jointScale)
        self.thumb1 = createJnt("{0}_L_thumb1".format(jointName),
                                position=[(8*jointSize), (13.8 * jointSize), (0.6 * jointSize)], radius=jointScale)
        self.thumb2 = createJnt("{0}_L_thumb2".format(jointName),
                                position=[(8.3*jointSize), (13.8 * jointSize), (0.6 * jointSize)], radius=jointScale)
        self.thumb3 = createJnt("{0}_L_thumb3".format(jointName),
                                position=[(8.6*jointSize), (13.8 * jointSize), (0.6 * jointSize)], radius=jointScale)
        self.thumbJointGrp.extend([self.thumbMeta, self.thumb1, self.thumb2, self.thumb3])
        [cmds.parent(self.thumbJointGrp[i + 1], joint) for i, joint in enumerate(self.thumbJointGrp[:-1])]

        self.indexJointGrp = []
        self.indexMeta = createJnt("{0}_L_indexMeta".format(jointName),
                                   position=[(7.5*jointSize), (14 * jointSize), (0.2 * jointSize)], radius=jointScale)
        self.index1 = createJnt("{0}_L_index1".format(jointName),
                                position=[(8.3*jointSize), (14 * jointSize), (0.3 * jointSize)], radius=jointScale)
        self.index2 = createJnt("{0}_L_index2".format(jointName),
                                position=[(8.7*jointSize), (14 * jointSize), (0.3 * jointSize)], radius=jointScale)
        self.index3 = createJnt("{0}_L_index3".format(jointName),
                                position=[(9.0*jointSize), (14 * jointSize), (0.3 * jointSize)], radius=jointScale)
        self.indexEnd = createJnt("{0}_L_indexEnd".format(jointName),
                                  position=[(9.3*jointSize), (14 * jointSize), (0.3 * jointSize)], radius=jointScale)
        self.indexJointGrp.extend([self.indexMeta, self.index1, self.index2, self.index3, self.indexEnd])
        [cmds.parent(self.indexJointGrp[i + 1], joint) for i, joint in enumerate(self.indexJointGrp[:-1])]

        self.middleJointGrp = []
        self.middleMeta = createJnt("{0}_L_middleMeta".format(jointName),
                                    position=[(7.5*jointSize), (14 * jointSize), 0], radius=jointScale)
        self.middle1 = createJnt("{0}_L_middle1".format(jointName),
                                 position=[(8.3*jointSize), (14 * jointSize), 0], radius=jointScale)
        self.middle2 = createJnt("{0}_L_middle2".format(jointName),
                                 position=[(8.7*jointSize), (14 * jointSize), 0], radius=jointScale)
        self.middle3 = createJnt("{0}_L_middle3".format(jointName),
                                 position=[(9.0*jointSize), (14 * jointSize), 0], radius=jointScale)
        self.middleEnd = createJnt("{0}_L_middleEnd".format(jointName),
                                   position=[(9.3*jointSize), (14 * jointSize), 0], radius=jointScale)
        self.middleJointGrp.extend([self.middleMeta, self.middle1, self.middle2, self.middle3, self.middleEnd])
        [cmds.parent(self.middleJointGrp[i + 1], joint) for i, joint in enumerate(self.middleJointGrp[:-1])]

        self.ringJointGrp = []
        self.ringMeta = createJnt("{0}_L_ringMeta".format(jointName),
                                  position=[(7.5*jointSize), (14 * jointSize), -(0.2 * jointSize)], radius=jointScale)
        self.ring1 = createJnt("{0}_L_ring1".format(jointName),
                               position=[(8.3*jointSize), (14 * jointSize), -(0.3 * jointSize)], radius=jointScale)
        self.ring2 = createJnt("{0}_L_ring2".format(jointName),
                               position=[(8.7*jointSize), (14 * jointSize), -(0.3 * jointSize)], radius=jointScale)
        self.ring3 = createJnt("{0}_L_ring3".format(jointName),
                               position=[(9.0*jointSize), (14 * jointSize), -(0.3 * jointSize)], radius=jointScale)
        self.ringEnd = createJnt("{0}_L_ringEnd".format(jointName),
                                 position=[(9.3*jointSize), (14 * jointSize), -(0.3 * jointSize)], radius=jointScale)
        self.ringJointGrp.extend([self.ringMeta, self.ring1, self.ring2, self.ring3, self.ringEnd])
        [cmds.parent(self.ringJointGrp[i + 1], joint) for i, joint in enumerate(self.ringJointGrp[:-1])]

        self.pinkyJointGrp = []
        self.pinkyMeta = createJnt("{0}_L_pinkyMeta".format(jointName),
                                   position=[(7.5*jointSize), (14 * jointSize), -(0.4 * jointSize)], radius=jointScale)
        self.pinky1 = createJnt("{0}_L_pinky1".format(jointName),
                                position=[(8.1*jointSize), (14 * jointSize), -(0.5 * jointSize)], radius=jointScale)
        self.pinky2 = createJnt("{0}_L_pinky2".format(jointName),
                                position=[(8.4*jointSize), (14 * jointSize), -(0.5 * jointSize)], radius=jointScale)
        self.pinky3 = createJnt("{0}_L_pinky3".format(jointName),
                                position=[(8.7*jointSize), (14 * jointSize), -(0.5 * jointSize)], radius=jointScale)
        self.pinkyEnd = createJnt("{0}_L_pinkyEnd".format(jointName),
                                  position=[(9.0*jointSize), (14 * jointSize), -(0.5 * jointSize)], radius=jointScale)
        self.pinkyJointGrp.extend([self.pinkyMeta, self.pinky1, self.pinky2, self.pinky3, self.pinkyEnd])
        [cmds.parent(self.pinkyJointGrp[i + 1], joint) for i, joint in enumerate(self.pinkyJointGrp[:-1])]

        cmds.parent(self.armJointGrp[0], self.spineJointGrp[3])
        cmds.parent(self.legJointGrp[0], self.spineJointGrp[0])
        cmds.parent(self.thumbJointGrp[0], self.armJointGrp[-1])
        cmds.parent(self.indexJointGrp[0], self.armJointGrp[-1])
        cmds.parent(self.middleJointGrp[0], self.armJointGrp[-1])
        cmds.parent(self.ringJointGrp[0], self.armJointGrp[-1])
        cmds.parent(self.pinkyJointGrp[0], self.armJointGrp[-1])

        self.allJoints = cmds.listRelatives(self.spineJointGrp[0], c=True, ad=True)
        self.visLocalAxis(self.allJoints)

    @undo
    def visLocalAxis(self, jointList=None, dis=1):
        if not jointList:
            jointList = cmds.listRelatives(cmds.ls(sl=True), c=True, ad=True)
        if jointList:
            for i in jointList:
                cmds.setAttr("{0}.displayLocalAxis".format(i), dis)

    @undo
    def rebulid(self, primaryAxis="y", secondaryAxis="x"):
        pass




def visPoleVector(jointName, jointList=None):

    jointName = jointName
    if not jointList:
        jointList = cmds.ls(sl=1, fl=1)

    if not cmds.objExists("SkVisualizer"):
        cmds.createNode("transform", name="SkVisualizer")

    if not cmds.objExists("SkPoleVectors"):
        cmds.createNode("transform", name="SkPoleVectors", parent="SkVisualizer")
        cmds.setAttr("SkPoleVectors.inheritsTransform", 0)

    if not cmds.objExists("MPolerVis"):
        cmds.setAttr(cmds.shadingNode("lambert", asShader=True, name="MPolerVis") + ".color", 1, 0, 0,
                     type="double3")

    vpvGeo = cmds.polyCreateFacet(name="VPV_{0}".format(jointName), ch=0, tx=1, s=1,
                                  p=[(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)])[0]
    cmds.parent(vpvGeo, "SkPoleVectors")

    lambert_sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="MPolerVisSG")
    cmds.connectAttr("MPolerVis" + ".outColor", lambert_sg + ".surfaceShader", force=True)
    cmds.sets(vpvGeo, e=True, forceElement=lambert_sg)

    cmds.setAttr("{0}.overrideEnabled".format(vpvGeo), 1)
    cmds.setAttr("{0}.overrideDisplayType".format(vpvGeo), 2)

    parentLoc = cmds.spaceLocator(name="{0}_ParentLoc".format(jointName))[0]
    cmds.parent(parentLoc, vpvGeo)
    cmds.setAttr("{0}.v".format(parentLoc), 0)

    childLoc = cmds.duplicate(parentLoc, name="{0}_childLoc".format(jointName))[0]
    midLoc = cmds.duplicate(parentLoc, name="{0}_midLoc".format(jointName))[0]
    midFloatLoc = cmds.duplicate(parentLoc, name="{0}_midFloatLoc".format(jointName))[0]
    poleVecLoc = cmds.duplicate(parentLoc, name="{0}_poleVecLoc".format(jointName))[0]
    cmds.parent(poleVecLoc, midFloatLoc)

    IkDis = cmds.createNode("distanceBetween", name="{0}_IKDist".format(jointName))
    IkDisA = cmds.createNode("distanceBetween", name="{0}_IKDistA".format(jointName))
    IkDisB = cmds.createNode("distanceBetween", name="{0}_IKDistB".format(jointName))
    IkDisC = cmds.createNode("distanceBetween", name="{0}_IKDistC".format(jointName))

    cmds.connectAttr("{0}.worldMatrix[0]".format(parentLoc), "{0}.inMatrix1".format(IkDis))
    cmds.connectAttr("{0}.worldMatrix[0]".format(childLoc), "{0}.inMatrix2".format(IkDis))
    cmds.connectAttr("{0}.worldMatrix[0]".format(parentLoc), "{0}.inMatrix1".format(IkDisA))
    cmds.connectAttr("{0}.worldMatrix[0]".format(childLoc), "{0}.inMatrix1".format(IkDisB))
    cmds.connectAttr("{0}.worldMatrix[0]".format(midLoc), "{0}.inMatrix2".format(IkDisA))
    cmds.connectAttr("{0}.worldMatrix[0]".format(midLoc), "{0}.inMatrix2".format(IkDisB))
    cmds.connectAttr("{0}.worldMatrix[0]".format(midLoc), "{0}.inMatrix1".format(IkDisC))
    cmds.connectAttr("{0}.worldMatrix[0]".format(midFloatLoc), "{0}.inMatrix2".format(IkDisC))

    IkPMA = cmds.createNode("plusMinusAverage", name="{0}_PMA".format(jointName))
    cmds.connectAttr("{0}.distance".format(IkDis), "{0}.input1D[0]".format(IkPMA), force=True)
    cmds.connectAttr("{0}.distance".format(IkDisC), "{0}.input1D[1]".format(IkPMA), force=True)

    IkMTD = cmds.createNode("multiplyDivide", name="{0}_MTD".format(jointName))
    cmds.connectAttr("{0}.output1D".format(IkPMA), "{0}.input1X".format(IkMTD), force=True)
    cmds.setAttr("{0}.input2X".format(IkMTD), 0.5)
    cmds.connectAttr("{0}.outputX".format(IkMTD), "{0}.tx".format(poleVecLoc))

    cmds.pointConstraint(jointList[0], parentLoc)
    cmds.pointConstraint(jointList[2], childLoc)
    cmds.pointConstraint(jointList[1], midLoc)
    midFloatPOC = cmds.pointConstraint(jointList[0], jointList[2], midFloatLoc)[0]

    cmds.connectAttr("{0}.distance".format(IkDisB), "{0}.{1}W0".format(midFloatPOC, jointList[0]))
    cmds.connectAttr("{0}.distance".format(IkDisA), "{0}.{1}W1".format(midFloatPOC, jointList[2]))
    cmds.aimConstraint(jointList[1], midFloatLoc, weight=1, aimVector=(1, 0, 0), upVector=(0, 0, 1),
                       worldUpType="objectrotation", worldUpObject=jointList[0], offset=(0, 0, 0))

    vpvGeo_shape = cmds.listRelatives(vpvGeo, s=True)[0]
    cmds.connectAttr("{0}.worldPosition[0]".format(parentLoc), "{0}.controlPoints[0]".format(vpvGeo_shape))
    cmds.connectAttr("{0}.worldPosition[0]".format(poleVecLoc), "{0}.controlPoints[1]".format(vpvGeo_shape))
    cmds.connectAttr("{0}.worldPosition[0]".format(childLoc), "{0}.controlPoints[2]".format(vpvGeo_shape))
    cmds.connectAttr("{0}.worldPosition[0]".format(midLoc), "{0}.controlPoints[3]".format(vpvGeo_shape))

def hidePoleVector(jointName):
    if cmds.objExists("VPV_{0}".format(jointName)):
        cmds.delete("VPV_{0}".format(jointName))








