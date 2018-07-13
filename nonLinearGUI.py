import sys
import maya.api.OpenMaya as om
import maya.cmds as cmds
import random
from sets import Set
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
        self.strongestShapesTree = {}
        self.generationSelection = []
        self.nextGeneration = []
        self.allSymmetryNames = allSymmetryNames
        self.buttonList = []
        self.newShapes = {}
        self.startingCurves = {}
        self.currentGenCurves = {}
        self.OTHER_FACE_IDS = OTHER_FACE_IDS
        self.originalStrongest = strongestShapes
        self.symGroups = {}
        self.lastElite = self.saveFaceCurves()

        print "strongestShapes"
        print strongestShapes

        newShapes = self.flattenDictToVals(self.strongestShapes)
        targetShapes = self.flattenDictToChildren(self.strongestShapes)
        strongestShapesTree = self.cropTreeToStrongestShapes()
        # strongestShapesNeutrals = self.getStrongestNeutralVals(self.strongestShapes)

        # self.strongestShapesNeutrals = strongestShapesNeutrals

        print "newShapes:"
        print newShapes
        print "targetShapes"
        print targetShapes
        print "strongestShapesTree"
        print strongestShapesTree
        # print "strongestShapesNeutrals"
        # print strongestShapesNeutrals

        self.strongestShapesTree = strongestShapesTree

        flattenedSyms = self.flattenDictToChildren(self.allSymmetryNames)

        newShapesSym = self.correctSymmetryNames(newShapes, flattenedSyms)


        self.linearBlendshape(self.strongestShapesTree)
        self.sampleNonLinear(2)

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
        cmds.text(label = "")
        cmds.text("Choose Group to Act on:", font="boldLabelFont", al="center")
        controlGroupSourceGroup = cmds.optionMenu("controlGroupSourceGroup")
        cmds.menuItem(label='All')
        for key1 in strongestShapesTree.keys():
            cmds.menuItem(label=key1)
        cmds.text(label="")

        cmds.text("ELITE:", font="boldLabelFont", al="center")
        cmds.text("Choose Curve to Act on:", font="boldLabelFont", al="center")
        controlGroupSource = cmds.optionMenu("controlGroupSource")
        cmds.menuItem(label='All')
        for key1 in newShapesSym:
            cmds.menuItem(label=key1)
        cmds.text("OPTIONS:", font="boldLabelFont", al="center")

        cmds.text(label='')
        cmds.separator()
        cmds.separator()
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'right', 0)])
        cmds.text("                                ")
        cmds.checkBox(editable=True, label="  Symmetry", value=True)
        cmds.setParent('..')

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="Set Elite:  ")
        controlGroup = cmds.optionMenu("controlGroup")
        for key in range(1, 4):
            cmds.menuItem(label="SAMPLE " + str(key))
        cmds.button(label='    Set    ', command=partial(self.setFaceAsElite))
        cmds.setParent('..')
        cmds.text("New Curves:", font="boldLabelFont", al="center")
        cmds.text("Modify Curves:", font="boldLabelFont", al="center")
        cmds.rowLayout(numberOfColumns=2, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'right', 0)])
        cmds.text("                                ")
        cmds.checkBox("localiseFlag",editable=True, label="  Localise sampling")
        cmds.setParent('..')

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Reset Samples to Elite', command=partial(self.copyEliteToSamples,self.strongestShapesTree))
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 Number of New Keys:")
        cmds.intField("numKeys",minValue=1, maxValue=4, value=2, editable=True)
        cmds.text(label="                ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Sample Curve Amplitude', command=partial(self.sampleAmpPhase , "Amp"))
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)], w=100)

        cmds.text(label='                S.D: ')
        cmds.floatSliderGrp("sdVal", field=True, minValue=0.0, maxValue=1.0, fieldMinValue=0.0,
                            fieldMaxValue=1.0, value=0.3, cw=[(1, 50), (2, 120)])
        cmds.text(label='                   ')
        cmds.setParent('..')

        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Reset to Last Elite', command=partial(self.resetToLastElite))
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Sample', command=partial(self.sampleNonLinear,-1))
        cmds.text(label="                 ")
        cmds.setParent('..')
        cmds.rowLayout(numberOfColumns=3, adjustableColumn=2, columnAlign=(1, 'right'),
                       columnAttach=[(1, 'left', 0), (2, 'both', 0), (3, 'right', 0)])
        cmds.text(label="                 ")
        cmds.button(label='Sample Curve Phase', command=partial(self.sampleAmpPhase , "Phase"))
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

        self.copyEliteToSamples(self.strongestShapesTree)

    def copyEliteToSamples(self, blendshapeTargetTree, *args):

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

        if numKeys < 0:
            numKeys = cmds.intField("numKeys", value=True, query=True)
            localiseFlag = cmds.checkBox("localiseFlag", value=True, query=True)
            selectedGroup = cmds.optionMenu("controlGroupSourceGroup", value=True, query=True)
            selectedCurve = cmds.optionMenu("controlGroupSource", value=True, query=True)

        else:
            selectedGroup = 'All'
            selectedCurve = 'All'

        # if localiseFlag:
        #     self.copyEliteToSamples(self.allStartingWeights)
        # else:

        blendshapeTargetTree = self.strongestShapesTree
        blendshapeSourceTree = self.allNeutralWeights

        for sampleFace in range(1,4):

            ranSampTime = sorted ( random.sample(range(2, 199), numKeys) , reverse=True)
            ranSampValTemp = [random.random() for _ in range(numKeys)]
            print ranSampValTemp
            ranSampVal = sorted(ranSampValTemp,reverse=True)
            print ranSampVal
            print ranSampTime

            for faceGroup, ctlDict in blendshapeTargetTree.iteritems():

                if  selectedGroup == faceGroup:
                    print "Selected Group True"
                    ranSampTime = sorted(random.sample(range(2, 199), numKeys) , reverse=True)
                    ranSampValTemp = [random.random() for _ in range(numKeys)]
                    ranSampVal = sorted(ranSampValTemp,reverse=True)

                if selectedGroup == faceGroup or selectedGroup == 'All':
                    for ctlName, ctlVal in ctlDict.iteritems():

                        if selectedCurve != 'All':
                            if self.symGroups[selectedCurve][0] == ctlName:
                                print "Selected Curve True"
                                ranSampTime2 = sorted(random.sample(range(2,199), numKeys) , reverse=True)
                                ranSampValTemp2= [random.random() for _ in range(numKeys)]
                                ranSampVal2 = sorted(ranSampValTemp2,reverse=True)

                                self.individualCurveSample(ctlName, faceGroup, ranSampTime2, ranSampVal2, ctlVal,
                                                           sampleFace)
                                self.individualCurveSample(self.symGroups[selectedCurve][1], faceGroup, ranSampTime2, ranSampVal2, ctlVal,
                                                           sampleFace)
                        else:
                            self.individualCurveSample(ctlName, faceGroup, ranSampTime, ranSampVal, ctlVal, sampleFace)



    def individualCurveSample(self, curveName, faceGroup, ranSampTime, ranSampVal, ctlVal, sampleFace):

        nSId = curveName.find(':')
        if nSId != -1:
            outTransform = curveName[:nSId] + str(sampleFace) + curveName[nSId:]
        else:
            outTransform = self.OTHER_FACE_IDS % sampleFace
            outTransform = outTransform + curveName

        cmds.cutKey(outTransform, time=(2, 199), option="keys")


        for keyId,ranKey in enumerate(ranSampVal):

            randTime = ranSampTime[keyId]

            neutralVal = self.allNeutralWeights[faceGroup][curveName]
            sampleVal = neutralVal + (ranKey * (ctlVal - neutralVal))



            cmds.setKeyframe(outTransform, t=(randTime, randTime), v=sampleVal)

    def sampleAmpPhase(self, ampOrPhase, *args):


        localiseFlag = cmds.checkBox("localiseFlag", value=True, query=True)
        selectedGroup = cmds.optionMenu("controlGroupSourceGroup", value=True, query=True)
        selectedCurve = cmds.optionMenu("controlGroupSource", value=True, query=True)
        sdVal = cmds.floatSliderGrp("sdVal", value=True, query=True)


        blendshapeTargetTree = self.strongestShapesTree
        blendshapeSourceTree = self.allNeutralWeights

        for sampleFace in range(1,4):

            if localiseFlag:
                ranShiftAmp = [random.uniform(1 - sdVal,1 + sdVal) for _ in range(6)]
                ranShiftPhase = [random.uniform(1 - sdVal,1 + sdVal) for _ in range(6)]
            else:
                ranShiftAmp = random.uniform(-0.3,0.3)
                ranShiftPhase = random.uniform(-20, 20)

            for faceGroup, ctlDict in blendshapeTargetTree.iteritems():

                if  selectedGroup == faceGroup:
                    print "Selected Group True"
                    if localiseFlag:
                        ranShiftAmp = [random.uniform(1 - sdVal, 1 + sdVal) for _ in range(6)]
                        ranShiftPhase = [random.uniform(1 - sdVal, 1 + sdVal) for _ in range(6)]
                    else:
                        ranShiftAmp = random.uniform(-0.3, 0.3)
                        ranShiftPhase = random.uniform(-20, 20)

                if selectedGroup == faceGroup or selectedGroup == 'All':
                    for ctlName, ctlVal in ctlDict.iteritems():

                        if selectedCurve != 'All':
                            if self.symGroups[selectedCurve][0] == ctlName:
                                print "Selected Curve True"
                                if localiseFlag:
                                    ranShiftAmp2 = [random.uniform(1 - sdVal, 1 + sdVal) for _ in range(6)]
                                    ranShiftPhase2 = [random.uniform(1 - sdVal, 1 + sdVal) for _ in range(6)]
                                else:
                                    ranShiftAmp2 = random.uniform(-0.3, 0.3)
                                    ranShiftPhase2 = random.uniform(-20, 20)

                                self.individualCurveAmpPhaseSample(ctlName, faceGroup, ranShiftPhase2, ranShiftAmp2, ctlVal,
                                                           sampleFace, localiseFlag, ampOrPhase)
                                self.individualCurveAmpPhaseSample(self.symGroups[selectedCurve][1], faceGroup, ranShiftPhase2, ranShiftAmp2, ctlVal,
                                                           sampleFace, localiseFlag, ampOrPhase)
                        else:
                            self.individualCurveAmpPhaseSample(ctlName, faceGroup, ranShiftPhase, ranShiftAmp, ctlVal,
                                                               sampleFace, localiseFlag, ampOrPhase)

    def individualCurveAmpPhaseSample(self, curveName, faceGroup, ranSampTime, ranSampVal,
                                      ctlVal, sampleFace, localiseFlag, ampOrPhase):

        nSId = curveName.find(':')
        if nSId != -1:
            outTransform = curveName[:nSId] + str(sampleFace) + curveName[nSId:]
        else:
            outTransform = self.OTHER_FACE_IDS % sampleFace
            outTransform = outTransform + curveName

        # cmds.cutKey(outTransform, time=(2, 199), option="keys")

        if not localiseFlag:
            if ampOrPhase == "Amp":
                cmds.keyframe(outTransform, time=(2,199), relative=True, valueChange= ranSampVal)
            if ampOrPhase == "Phase":
                cmds.keyframe(outTransform, time=(2,199), relative=True, timeChange= ranSampTime)

        else:

            keys = cmds.keyframe(outTransform, time = (2,199), valueChange=True, query=True)
            times = cmds.keyframe(outTransform, time=(2, 199), timeChange=True, query=True)
            print keys
            print times

            cmds.cutKey(outTransform, time=(2, 199), option="keys")

            for keyId, keyVal in enumerate(keys):

                if ampOrPhase == "Amp":
                    randTime = times[keyId]
                    randVal = ranSampVal[keyId] * keyVal


                if ampOrPhase == "Phase":
                    randTime = ranSampTime[keyId] * times[keyId]
                    randVal = keyVal

                    if randTime < 3:
                        randTime = 3

                    if randTime > 198:
                        randTime = 198

                cmds.setKeyframe(outTransform, t=(randTime, randTime), v=randVal)



    def flattenDictToVals(self, dicto):

        returnList = []
        for vals in dicto.values():
            print vals
            if vals:
                for nodes in vals:
                    returnList.append(nodes[0])

        return returnList

    def flattenDictToChildren(self, dicto):

        returnDict = {}
        for vals in dicto.values():
            if vals:
                print "vals:"
                print vals
                returnDict.update(vals)

        return returnDict

    # def getStrongestNeutralVals(self, strongestShapes):
    #
    #     neutralTree = self.allNeutralWeights
    #     returnDict = {}
    #     for keys, vals in strongestShapes.iteritems():
    #         for keys2, vals2 in vals.iteritems():
    #             returnDict[keys][keys2] = neutralTree[keys][keys2]
    #
    #     return returnDict

    def cropTreeToStrongestShapes(self):

        startingTree = self.allStartingWeights
        strongestShapes = self.strongestShapes
        returnDict = {}
        for keys, vals in strongestShapes.iteritems():
            if vals:
                returnDict[keys] = {}
                for keys2 in vals:
                    print keys
                    print keys2
                    print keys2[0]
                    print startingTree[keys][keys2[0]]
                    returnDict[keys][keys2[0]] = startingTree[keys][keys2[0]]

        return returnDict

    def correctSymmetryNames(self, flattened, flattenedSyms):

        returnList = []
        returnDict = {}

        print "flattened , flattenedSymn"
        print flattened
        print flattenedSyms
        print "end"
        for vid,vals in enumerate(flattened):
            print vals
            symVal = flattenedSyms[vals]
            if (symVal in flattened) and (vals != symVal):
                flattened.pop(vid)
                setVal = Set(vals.split('_'))
                print setVal
                setSymVal = Set(symVal.split('_'))
                print setSymVal
                seq = '_'.join(setVal & setSymVal)
                print "seq:"
                print seq
                returnList.append(seq)
                returnDict[seq] = (vals,symVal)
            else:
                returnList.append(vals)
                returnDict[vals] = (vals,vals)

        self.symGroups = returnDict
        return returnList

    def setFaceAsElite(self, *args):

        self.lastElite = self.saveFaceCurves()

        eliteChoice = cmds.optionMenu("controlGroup", value=True, query=True)
        eliteNum = int(eliteChoice[-1])

        shapeTree = self.strongestShapesTree

        for faceGroup, ctlDict in shapeTree.iteritems():

            for ctlName, ctlVal in ctlDict.iteritems():

                nSId = ctlName.find(':')
                if nSId != -1:
                    print "in"
                    out1 = ctlName[:nSId] + str(eliteNum) + ctlName[nSId:]

                else:
                    out1 = (self.OTHER_FACE_IDS + ctlName) % eliteNum

                cmds.cutKey(ctlName, time=(2, 199), option="keys")
                cmds.copyKey(out1, time=(1, 250), option="keys")  # or keys?
                cmds.pasteKey(ctlName, time=(1, 250), option="replace")

    def saveFaceCurves(self):

        shapeTree = self.strongestShapesTree

        outDict = {}
        for faceGroup, ctlDict in shapeTree.iteritems():
            outGroup = {}
            for ctlName, ctlVal in ctlDict.iteritems():
                keys = cmds.keyframe(ctlName, time=(1, 250), valueChange=True, query=True)
                times = cmds.keyframe(ctlName, time=(1, 250), timeChange=True, query=True)

                outGroup[ctlName] = (keys, times)
            outDict[faceGroup] = outGroup

        return outDict

    def resetToLastElite(self, *args):

        lastElite = self.lastElite

        outDict = {}
        for faceGroup, ctlDict in lastElite.iteritems():
            for ctlName, ctlVal in ctlDict.iteritems():
                cmds.cutKey(ctlName, time=(2, 199), option="keys")
                for keyId, keys in enumerate(ctlVal[0]):
                    times = ctlVal[1][keyId]

                    cmds.setKeyframe(ctlName, t=(times, times), v=keys)






