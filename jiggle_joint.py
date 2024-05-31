import maya.OpenMaya as om
import maya.OpenMayaMPx as ompx
import math


class JiggleJoint(ompx.MPxNode):
    kPluginNodeId = om.MTypeId(0x00001234)

    aOutput = om.MObject()
    aGoal = om.MObject()
    aDamping = om.MObject()
    aStiffness = om.MObject()
    aTime = om.MObject()
    aParentInverse = om.MObject()
    aJiggleAmount = om.MObject()

    def __init__(self):
        ompx.MPxNode.__init__(self)
        self.initialized = False
        self.currentPos = om.MPoint()
        self.previousPos = om.MPoint()
        self.previousTime = om.MTime()

    def compute(self, plug, data):
        if plug != JiggleJoint.aOutput:
            return om.kUnknownParameter

        # get inputs
        damping = data.inputValue(self.aDamping).asFloat()
        stiffness = data.inputValue(self.aStiffness).asFloat()
        goal = om.MPoint(data.inputValue(self.aGoal).asFloatVector())
        currentTime = data.inputValue(self.aTime).asTime()
        parentInverse = data.inputValue(self.aParentInverse).asMatrix()
        jiggleAmount = data.inputValue(self.aJiggleAmount).asFloat()

        if not self.initialized:
            self.previousTime = currentTime
            self.currentPos = goal
            self.previousPos = goal
            self.initialized = True

        timeDifference = currentTime.value() - self.previousTime.value()
        if timeDifference > 1.0 or timeDifference < 0.0:
            self.initialized = False
            self.previousTime = currentTime
            data.setClean(plug)
            return

        velocity = (self.currentPos - self.previousPos) * (1.0 - damping)
        newPosition = self.currentPos + velocity
        goalForce = (goal - newPosition) * stiffness
        newPosition += goalForce

        # store the states for next computation
        self.previousPos = om.MPoint(self.currentPos)
        self.currentPos = om.MPoint(newPosition)
        self.previousTime = om.MTime(currentTime)

        newPosition = goal + ((newPosition - goal) * jiggleAmount)
        newPosition *= parentInverse

        hOutput = data.outputValue(JiggleJoint.aOutput)
        outVector = om.MFloatVector(newPosition.x, newPosition.y, newPosition.z)
        hOutput.setMFloatVector(outVector)
        hOutput.setClean()
        data.setClean(plug)


def creator():
    return ompx.asMPxPtr(JiggleJoint())


def initialize():
    nAttr = om.MFnNumericAttribute()
    uAttr = om.MFnUnitAttribute()
    mAttr = om.MFnMatrixAttribute()

    JiggleJoint.aOutput = nAttr.createPoint("output", "out")
    nAttr.setWritable(False)
    nAttr.setStorable(False)
    JiggleJoint.addAttribute(JiggleJoint.aOutput)

    JiggleJoint.aJiggleAmount = nAttr.create("jiggleAmount", "jiggleAmount", om.MFnNumericData.kFloat, 0.0)
    nAttr.setKeyable(True)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    JiggleJoint.addAttribute(JiggleJoint.aJiggleAmount)
    JiggleJoint.attributeAffects(JiggleJoint.aJiggleAmount, JiggleJoint.aOutput)

    JiggleJoint.aGoal = nAttr.createPoint("goal", "goal")
    JiggleJoint.addAttribute(JiggleJoint.aGoal)
    JiggleJoint.attributeAffects(JiggleJoint.aGoal, JiggleJoint.aOutput)

    JiggleJoint.aTime = uAttr.create("time", "time", om.MFnUnitAttribute.kTime, 0.0)
    JiggleJoint.addAttribute(JiggleJoint.aTime)
    JiggleJoint.attributeAffects(JiggleJoint.aTime, JiggleJoint.aOutput)

    JiggleJoint.aStiffness = nAttr.create("stiffness", "stiffness", om.MFnNumericData.kFloat, 1.0)
    nAttr.setKeyable(True)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    JiggleJoint.addAttribute(JiggleJoint.aStiffness)
    JiggleJoint.attributeAffects(JiggleJoint.aStiffness, JiggleJoint.aOutput)

    JiggleJoint.aDamping = nAttr.create("damping", "damping", om.MFnNumericData.kFloat, 1.0)
    nAttr.setKeyable(True)
    nAttr.setMin(0.0)
    nAttr.setMax(1.0)
    JiggleJoint.addAttribute(JiggleJoint.aDamping)
    JiggleJoint.attributeAffects(JiggleJoint.aDamping, JiggleJoint.aOutput)

    JiggleJoint.aParentInverse = mAttr.create("parentInverse", "parentInverse")
    JiggleJoint.addAttribute(JiggleJoint.aParentInverse)


def initializePlugin(obj):
    fnPlugin = ompx.MFnPlugin(obj, "Lyz", "1.0", "Any")
    fnPlugin.registerNode("jiggleJoint", JiggleJoint.kPluginNodeId, creator, initialize)


def uninitializePlugin(obj):
    fnPlugin = ompx.MFnPlugin(obj)
    fnPlugin.deregisterNode(JiggleJoint.kPluginNodeId)
