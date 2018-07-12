import sys
import maya.api.OpenMaya as om
import maya.cmds as cmds
import random
import copy
from functools import partial

##########################################################
# Plug-in
##########################################################
class GUI():

    def __init__(self, CTL_TREE,allStartingWeights,allNeutralWeights,
                 allCurrentGenWeights, strongestShapes, minMaxWeights, allSymmetryNames,OTHER_FACE_IDS):

        self.ctlTree = CTL_TREE
        self.allStartingWeights = allStartingWeights
        self.allCurrentGenWeights = allCurrentGenWeights
        self.allCurrentWeights = allCurrentGenWeights
        self.allNeutralWeights = allNeutralWeights
        self.allMinMaxWeights = minMaxWeights
        self.strongestShapes = strongestShapes
        self.generationSelection = []
        self.nextGeneration = []
        self.allSymmetryNames = allSymmetryNames
        self.buttonList = []
        self.newShapes = {}
        self.startingCurves = {}
        self.currentGenCurves = {}
        self.OTHER_FACE_IDS = OTHER_FACE_IDS
        self.originalStrongest = strongestShapes

        self.linearBlendshape(allStartingWeights)

        import maya.cmds as cmds
        selectionUI = 'altUI'

        if cmds.window(selectionUI, exists=True):
            cmds.deleteUI(selectionUI)

        cmds.window(selectionUI, width=1000, height=200)
        form = cmds.formLayout()
        tabs = cmds.tabLayout(innerMarginWidth=10, innerMarginHeight=10, mcw=400, width=750, height=100)
        cmds.formLayout(form, edit=True,
                        attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)))

        child2 = cmds.gridLayout(numberOfColumns=4, cellWidthHeight=(300, 32))
        cmds.text("ELITE:", font="boldLabelFont", al="center")
        cmds.text("SAMPLE 1:", font="boldLabelFont", al="center")
        cmds.text("SAMPLE 2:", font="boldLabelFont", al="center")
        cmds.text("SAMPLE 3:", font="boldLabelFont", al="center")

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="Set Elite:  ")
        controlGroup = cmds.optionMenu("controlGroup")
        for key in range(1, 4):
            cmds.menuItem(label="SAMPLE " + str(key))
        cmds.button(label='    Set    ')
        cmds.setParent('..')

        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'right', 0)])
        cmds.text("                                ")
        cmds.checkBox(editable=True, label="  Select")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'right', 0)])
        cmds.text("                                ")
        cmds.checkBox(editable=True, label="  Select")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'right', 0)])
        cmds.text("                                ")
        cmds.checkBox(editable=True, label="  Select")
        cmds.setParent('..')

        cmds.text(label='')
        cmds.separator()
        cmds.separator()
        cmds.separator()

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Reset to Last Elite')
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Sample Current Gen')
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Add Selected to Gene Pool')
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Breed Next Gen')
        cmds.text(label="                 ")
        cmds.setParent('..')

        cmds.setParent('..')

        child1 = cmds.gridLayout(numberOfColumns=4, cellWidthHeight=(300, 32))
        cmds.text("ELITE:", font="boldLabelFont", al="center")
        cmds.text("Choose Curve to Act on:", font="boldLabelFont", al="center")
        controlGroup = cmds.optionMenu("controlGroup")
        for key in range(1, 4):
            cmds.menuItem(label="SAMPLE " + str(key))
        cmds.text("OPTIONS:", font="boldLabelFont", al="center")

        cmds.text(label='')
        cmds.separator()
        cmds.separator()
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'right', 0)])
        cmds.text("                                ")
        cmds.checkBox(editable=True, label="  Symmetry")
        cmds.setParent('..')

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="Set Elite:  ")
        controlGroup = cmds.optionMenu("controlGroup")
        for key in range(1, 4):
            cmds.menuItem(label="SAMPLE " + str(key))
        cmds.button(label='    Set    ')
        cmds.setParent('..')
        cmds.text("New Curves:", font="boldLabelFont", al="center")
        cmds.text("Modify Curves:", font="boldLabelFont", al="center")
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'right', 0)])
        cmds.text("                                ")
        cmds.checkBox(editable=True, label="  Localise sampling")
        cmds.setParent('..')

        cmds.text(label="                 ")
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 Number of New Keys:")
        cmds.intField(minValue=1, maxValue=4, value=2, editable=True)
        cmds.text(label="                ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Sample Curve Amplitude')
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)], w=100)

        cmds.text(label='                S.D: ')
        cmds.floatSliderGrp(field=True, minValue=0.0, maxValue=5.0, fieldMinValue=0.0,
                            fieldMaxValue=5.0, value=1.0, cw=[(1, 50), (2, 120)])
        cmds.text(label='                   ')
        cmds.setParent('..')

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Reset to Last Elite')
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Sample')
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Sample Curve Phase')
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.text(label="                 ")

        cmds.setParent('..')

        cmds.tabLayout(tabs, edit=True, tabLabel=((child2, '\t\t\t\t\t\t\t\t\tEvolution\t\t\t\t\t\t\t\t\t'),
                                                  (child1, '\t\t\t\t\t\t\tAdvanced Control\t\t\t\t\t\t\t')))

        cmds.showWindow()

    def linearBlendshape(self, blendshapeTargetTree):

        for faceGroup, ctlDict in blendshapeTargetTree.iteritems():

            for ctlName, ctlVal in ctlDict.iteritems():

                cmds.setKeyframe(ctlName, t=(250, 250), v=ctlVal)
                cmds.setKeyframe(ctlName, t=(200, 200), v=ctlVal)


        for faceGroup, ctlDict in blendshapeTargetTree.iteritems():

            for ctlName, ctlVal in ctlDict.iteritems():

                nSId = ctlName.find(':')
                if nSId != -1:
                    print "in"
                    out1 = ctlName[:nSId] + str(1) + ctlName[nSId:]
                    out2 = ctlName[:nSId] + str(2) + ctlName[nSId:]
                    out3 = ctlName[:nSId] + str(3) + ctlName[nSId:]
                    print out1

                else:
                    out1 = (self.OTHER_FACE_IDS + ctlName) % 1
                    out2 = (self.OTHER_FACE_IDS + ctlName) % 2
                    out3 = (self.OTHER_FACE_IDS + ctlName) % 3
                    print out1

                cmds.copyKey(ctlName, time=(1, 250), option="keys")  # or keys?
                cmds.pasteKey(out1, time=(1, 250), option="replace")
                cmds.pasteKey(out2, time=(1, 250), option="replace")
                cmds.pasteKey(out3, time=(1, 250), option="replace")

    def sampleNonLinear(self, numKeys, *args):

        self.linearBlendshape(self.allStartingWeights)

        blendshapeTargetTree = self.allStartingWeights
        blendshapeSourceTree = self.allNeutralWeights

        for sampleFace in range(1,4):

            for keyId in range(numKeys):

                if keyId == 0:
                    randTime = random.uniform(1,200)
                    randScale = random.uniform(0, 1)
                else:
                    randTime = random.uniform(1, randTime)
                    randScale = random.uniform(0, randScale)

                for faceGroup, ctlDict in blendshapeTargetTree.iteritems():

                    for ctlName, ctlVal in ctlDict.iteritems():

                        neutralVal = blendshapeSourceTree[faceGroup][ctlName]
                        sampleVal = neutralVal + ( randScale * (ctlVal - neutralVal) )

                        nSId = ctlName.find(':')
                        if nSId != -1:
                            outTransform = ctlName[:nSId] + str(sampleFace) + ctlName[nSId:]
                        else:
                            outTransform = self.OTHER_FACE_IDS % sampleFace
                            outTransform = outTransform + ctlName

                        cmds.setKeyframe(outTransform, t=(randTime,randTime), v=sampleVal)