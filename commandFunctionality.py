import sys
import maya.api.OpenMaya as om
import maya.cmds as cmds
import random
import copy
from functools import partial

class CTLnode():

    def __init__(self,longname, translateName, weightDict, weightMinMax,shortGroupName):
        ''' Constructor. '''
        self.DAGpath = longname
        self.name = longname[longname.rfind('|') + 1:]
        self.translateName = self.name + '.' + translateName

        self.weight = weightDict
        self.startingWeight = weightDict
        self.groupName = shortGroupName
        self.weightMinMax = weightMinMax

    def __str__(self):
        return "Group: %s CTL: %s, Val: %s" % (self.groupName, self.name, self.weight)

    @staticmethod
    def createCTLNodePerTranslate(longname,shortGroupName):

        tempMinXYZ = cmds.getAttr(longname + '.minTransLimit')
        tempMaxXYZ = cmds.getAttr(longname + '.maxTransLimit')
        tempWeight = cmds.getAttr(longname + '.translate')

        translateCTLs = []
        try:
            cmds.setAttr(longname + '.translateX', tempWeight[0][0])
            weightDict = tempWeight[0][0]
            weightMinMax = (tempMinXYZ[0][0], tempMaxXYZ[0][0])
            translateCTLs.append(CTLnode(longname, 'translateX', weightDict, weightMinMax,shortGroupName))
        except:
            pass
        try:
            cmds.setAttr(longname + '.translateY', tempWeight[0][1])
            weightDict = tempWeight[0][1]
            weightMinMax = (tempMinXYZ[0][1], tempMaxXYZ[0][1])
            translateCTLs.append(CTLnode(longname, 'translateY', weightDict, weightMinMax,shortGroupName))
        except:
            pass

        return translateCTLs

    def getWeight(self):

        weight = cmds.getAttr(self.translateName)

        return weight

    def setWeight(self, newWeight):

        cmds.setAttr(self.translateName, newWeight)
        self.weight = newWeight


class GUI():

    def __init__(self, CTL_TREE,allStartingWeights,allNeutralWeights,
                 allCurrentGenWeights, strongestShapes, minMaxWeights, allSymmetryNames):

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


        winID = 'rigUI'

        if cmds.window(winID, exists=True):
            cmds.deleteUI(winID)
        cmds.window(winID, width = 100, height = 100)

        cmds.columnLayout("columnLayout")

        controlGroup = cmds.optionMenu("controlGroup",label='Control Group')
        cmds.menuItem(label='All')
        for key in self.ctlTree:
            cmds.menuItem(label=key)

        cmds.text(label="Symmetry On:")
        symFlag = cmds.checkBox("symFlag",label='symFlag', align='right', editable=True)

        # Add controls into this Layout
        cmds.text(label="Mutate Rate Lower:")
        numShapes = cmds.intField("numShapes", minValue=1, maxValue=10, value=3, editable=True,
                                      parent="columnLayout")
        cmds.text(label="Mutate Rate Upper:")
        mRateUpper = cmds.floatField("mRateUpper", minValue=0.0, maxValue=1.0, value=0.25, editable=True,
                                      parent="columnLayout")
        cmds.text(label="Constrain to Active Shapes:")
        constrainFlag = cmds.checkBox(label='constrainFlag', align='right', editable=True)
        cmds.text(label="Sample around Current Weight:")
        sampleFlag = cmds.checkBox(label='sampleWeight', align='right', editable=True, value=True)
        cmds.button(label='Random Sample from Current',
                    command=partial(self.randomMizeCTLs,numShapes,mRateUpper,constrainFlag,sampleFlag, controlGroup, symFlag))
        cmds.button(label='Reset To Gen', command=partial(self.updateRig, 'currentGen'))
        cmds.button(label='Reset To Starting', command=partial(self.updateRig, 'starting'))
        cmds.button(label='Reset To Neutral', command=partial(self.updateRig, 'neutral'))
        cmds.button(label='Set Current as Next Gen', command=partial(self.setCurrentGen))
        cmds.button(label='Add to selection', command=partial(self.addCurrentToSelection))
        cmds.text(label="Elite from Selection:")
        eliteId = cmds.intField("eliteId", minValue=1, maxValue=10, value=1, editable=True,
                                parent="columnLayout")
        cmds.button(label='Spawn Next Gen from Selection',
                    command=partial(self.spawnNextGen,eliteId,numShapes,mRateUpper,constrainFlag,sampleFlag,controlGroup, symFlag) )
        cmds.button(label='Next', command=partial(self.displayNext))
        cmds.button(label='Set Keyframe', command=partial(self.setKeyframes))


        # Display the window
        cmds.showWindow()

    def randomMizeCTLs(self, numShapes, mRateUpper, cFlag, sFlag, cGroup, syFlag, *args):
        print "Randomise"

        #print "Random func In: %s" % self.allCurrentGenWeights
        self.updateRig('currentGen')
        #print "Random func In2: %s" % self.allCurrentGenWeights

        numSampleShapes = cmds.intField(numShapes, query=True, value=True)
        upperLim = cmds.floatField(mRateUpper, query=True, value=True)
        constrainFlag = cmds.checkBox(cFlag, query=True, value=True)
        sampleFlag = cmds.checkBox(sFlag, query=True, value=True)
        controlGroup = cmds.optionMenu(cGroup, query=True, value=True)
        symFlag = cmds.checkBox(syFlag, query=True, value=True)

        print controlGroup

        randomCTLTree = self.randomCTLweights(self.allCurrentGenWeights,
                                              numSampleShapes, upperLim, constrainFlag,
                                              sampleFlag, controlGroup, symFlag)
        self.allCurrentWeights = randomCTLTree
        self.updateRig('current')

        # if constrainFlag:
        #     for key, value in self.strongestShapes.iteritems():
        #         if not value:
        #             continue
        #         randKeys = random.sample(list(value), min(numSampleShapes,len(value)))
        #         print randKeys
        #         for sortedTupleKey in randKeys:
        #             currentNode = self.ctlTree[key][sortedTupleKey[0]]
        #             currentWeight = currentNode.getWeight()
        #             randWeight = random.gauss(currentWeight,upperLim)
        #             print currentNode
        #             self.ctlTree[key][sortedTupleKey[0]].setWeight(randWeight)
        #             print currentNode
        #
        #
        # else:
        #     for key, value in self.ctlTree.iteritems():
        #         print "CTL GROUP: %s" % key
        #         randKeys = random.sample(list(value),min(numSampleShapes,len(value)))
        #         print randKeys
        #         for ctlNode in randKeys:
        #             #print ctlNode
        #             currentNode = self.ctlTree[key][ctlNode]
        #             currentWeight = currentNode.getWeight()
        #             randWeight = random.gauss(currentWeight, upperLim)
        #             print currentNode
        #             self.ctlTree[key][ctlNode].setWeight(randWeight)
        #             print currentNode

        #print "Random func Out: %s" % self.allCurrentGenWeights

    def randomCTLweights(self,inputCTLtree, numSampleShapes, upperLim, constrainFlag, sampleFlag, controlGroup, symFlag):

        returnTree = copy.deepcopy(inputCTLtree)

        if constrainFlag:
            for key, value in self.strongestShapes.iteritems():
                if controlGroup != 'All' and controlGroup != key:
                    continue
                if not value:
                    continue
                randKeys = random.sample(list(value), min(numSampleShapes,len(value)))
                print "RandKeys: %s" % randKeys
                for sortedTupleKey in randKeys:
                    currentWeight = inputCTLtree[key][sortedTupleKey[0]]
                    if sampleFlag:
                        randWeight = random.gauss(currentWeight,upperLim)
                    else:
                        minMaxWeight = self.allMinMaxWeights[key][sortedTupleKey[0]]
                        randWeight = random.uniform(minMaxWeight[0], minMaxWeight[1])
                    returnTree[key][sortedTupleKey[0]] = randWeight

                    if symFlag:
                        opposite = self.allSymmetryNames[key][sortedTupleKey[0]]
                        returnTree[key][opposite] = randWeight


        else:
            for key, value in inputCTLtree.iteritems():
                if controlGroup != 'All' and controlGroup != key:
                    continue
                randKeys = random.sample(list(value),min(numSampleShapes,len(value)))
                print "RandKeys: %s" % randKeys
                for ctlKey in randKeys:
                    #print ctlNode
                    currentWeight = inputCTLtree[key][ctlKey]
                    if sampleFlag:
                        randWeight = random.gauss(currentWeight, upperLim)
                    else:
                        minMaxWeight = self.allMinMaxWeights[key][ctlKey]
                        randWeight = random.uniform(minMaxWeight[0], minMaxWeight[1])


                    if symFlag:
                        opposite = self.allSymmetryNames[key][ctlKey]
                        if (opposite == ctlKey) and (ctlKey[-1] == 'X'):
                            print "Key: %s, Opposite: %s" % (ctlKey,opposite)
                            continue
                        if ctlKey[-1] == 'Y':
                            returnTree[key][opposite] = randWeight
                        elif ctlKey[-1] == 'X':
                            returnTree[key][opposite] = randWeight * -1
                        else:
                            print "Error with symmetry"

                    returnTree[key][ctlKey] = randWeight

        return returnTree

    def updateRig(self, weightTreeStr, *args):

        weightDict = {'currentGen':self.allCurrentGenWeights,
                      'starting':self.allStartingWeights,
                      'neutral':self.allNeutralWeights,
                      'current':self.allCurrentWeights}
        weightTree = weightDict[weightTreeStr]
        print "New weights: %s\n" % weightTree

        for groupKey, groupNode in self.ctlTree.iteritems():
            for nodeKey,ctlNode in groupNode.iteritems():
                newWeight = weightTree[groupKey][ctlNode.translateName]
                ctlNode.setWeight(newWeight)



    def getCurrentWeights(self):

        CTL_tree = self.ctlTree
        groupDict = {}
        for key,group in CTL_tree.iteritems():
            nodeDict = {}
            for key2, node in group.iteritems():
                nodeDict[node.translateName] = node.getWeight()

            groupDict[key] = nodeDict

        return groupDict

    def setCurrentGen(self, *args):

        currentTree = self.getCurrentWeights()
        # print "All current gen weights: %s" % self.allCurrentGenWeights
        # print "currentTree: %s" % currentTree
        self.allCurrentGenWeights = currentTree
        print "New all current gen weights: %s" % self.allCurrentGenWeights
        print "New all starting weights: %s" % self.allStartingWeights

    def addCurrentToSelection(self, *args):
        currentTree = self.getCurrentWeights()
        self.generationSelection.append(currentTree)

        IMG_PATH = 'C:/Users/cs/Documents/maya/projects/rigGAShri/images/tmp/'

        SELECTION_SIZE = len(self.generationSelection)
        currentRenderFile = "GASelectionGen%i" % SELECTION_SIZE
        cmds.setAttr("defaultRenderGlobals.imageFilePrefix", currentRenderFile, type="string")
        cmds.render('renderCam')
        print "Rendering %s\n" % currentRenderFile

        selectionUI = 'selectionUI'

        if cmds.window(selectionUI, exists=True):
            cmds.deleteUI(selectionUI)

        cmds.window(selectionUI, width=300, height=100)

        cmds.columnLayout("allLayout", adjustableColumn=True)
        cmds.columnLayout("topLayout",parent = "allLayout")
        cmds.button('selectAll', label = 'Select All', command=partial(self.changeAllSelection, True),parent="topLayout")
        cmds.button('clearAll', label = 'Clear All', command=partial(self.changeAllSelection, False),parent="topLayout")

        cmds.separator(parent="allLayout")

        cmds.gridLayout("gridLayout",numberOfColumns=6,cellWidthHeight=(256, 256), parent = "allLayout" )

        buttonList = []
        for face in range(SELECTION_SIZE):
            currentImg = IMG_PATH + "GASelectionGen" + str(face+1) + ".jpeg"
            print currentImg
            buttonName = 'button%i' % face
            buttonList.append(buttonName)
            print buttonList
            cmds.symbolCheckBox(buttonName,image=currentImg,parent = "gridLayout")
        cmds.showWindow(selectionUI)

        self.buttonList = buttonList

    # def pressSelections(self, buttonName,*args):
    #
    #     if self.selectionIt == 0:
    #         print "Elite"
    #         # cmds.symbolButton(buttonName, edit=True, bgc = (0.0,1.0,0.0))
    #
    #     else:
    #         print "Other"
    #         # cmds.symbolButton(buttonName, edit=True, bgc=(0.0, 0.0, 1.0))
    #
    #     self.selectionIt += 1

    def changeAllSelection(self,flag,*args):

        checkBoxNames = self.buttonList
        for cB in checkBoxNames:
            cmds.symbolCheckBox(cB, edit=True, value=flag)


    def spawnNextGen(self, eliteId,numShapes,mRateUpper, cFlag, cGroup, *args):
        print "Spawning next gen"

        cmds.showWindow('rigUI')

        eliteNum = cmds.intField(eliteId, query=True, value=True) - 1
        numSampleShapes = cmds.intField(numShapes, query=True, value=True)
        upperLim = cmds.floatField(mRateUpper, query=True, value=True)
        constrainFlag = cmds.checkBox(cFlag, query=True, value=True)
        controlGroup = cmds.optionMenu("controlGroup", query=True, value=True)
        symFlag = cmds.checkBox("symFlag", query=True, value=True)

        genSelectionAll = self.generationSelection
        nextGeneration = self.nextGeneration
        print genSelectionAll
        selectedIds = self.getSelectedFromWindow()
        print "SelectedIds: %s" % selectedIds
        genSelection = [x for i,x in enumerate(genSelectionAll) if i in selectedIds]
        # print genSelection

        for child in genSelection:
            print child

        for i in range(20):

            # Small mutations around Elite
            if i < 5:
                eliteCTLtree = copy.deepcopy(genSelectionAll[eliteNum])
                randEliteTree = self.randomCTLweights(eliteCTLtree, numSampleShapes, upperLim, True, True,controlGroup,symFlag)
                nextGeneration.append(randEliteTree)
            # Breeding of Elite and Other Selected
            elif i < 10:
                eliteCTLtree = copy.deepcopy(genSelectionAll[eliteNum])
                secondTree = random.choice(genSelection)
                bredTree = self.breedTrees(eliteCTLtree, secondTree, controlGroup)
                nextGeneration.append(bredTree)
            # Breeding of Elite and Other Selected + Mutation
            elif i < 15:
                eliteCTLtree = copy.deepcopy(genSelectionAll[eliteNum])
                secondTree = random.choice(genSelection)
                bredTree = self.breedTrees(eliteCTLtree, secondTree, controlGroup)
                randEliteTree = self.randomCTLweights(bredTree, numSampleShapes, upperLim, True, False, controlGroup,symFlag)
                nextGeneration.append(randEliteTree)
            # Less constrained mutation
            else:
                eliteCTLtree = copy.deepcopy(genSelectionAll[eliteNum])
                randEliteTree = self.randomCTLweights(eliteCTLtree, 2, upperLim, False, False, controlGroup,symFlag)
                nextGeneration.append(randEliteTree)
            #Add elite face at end

        self.allCurrentGenWeights = eliteCTLtree
        self.updateRig('currentGen')


    def getSelectedFromWindow(self):

        checkBoxNames = self.buttonList
        returnList = []
        for i,cB in enumerate(checkBoxNames):
            flag = cmds.symbolCheckBox(cB, query=True, value=True)
            if flag:
                returnList.append(i)

        return returnList

    def displayNext(self, *args):
        nextGeneration = self.nextGeneration
        currentNode = nextGeneration.pop(0)
        self.allCurrentWeights = currentNode
        self.updateRig('current')
        self.nextGeneration = nextGeneration

    def breedTrees(self, tree1, tree2, controlGroup):

        returnTree = copy.deepcopy(tree1)
        for keys,values in tree1.iteritems():
            if controlGroup != 'All' and controlGroup != keys:
                continue
            for keys2,values2 in values.iteritems():

                coinToss = random.random()

                if coinToss < 0.5:
                    returnTree[keys][keys2] = tree2[keys][keys2]

        return returnTree

    def setKeyframes(self, *args):
        currentTree = self.allCurrentWeights
        for key,vals in currentTree.iteritems():
            for key2 in vals:
                cmds.setKeyframe(key2)







##########################################################
# Plug-in
##########################################################
class Main(om.MPxCommand):

    def __init__(self):
        ''' Constructor. '''
        om.MPxCommand.__init__(self)
        self.NEUTRAL_TIME = 0
        self.STARTING_TIME = 0

    def doIt(self, args):

        # Skeleton working stub
        print "Stub In 1"

        # We recommend parsing your arguments first.
        argVals = self.parseArguments(args)
        ctlId = argVals[0]
        self.NEUTRAL_TIME = argVals[1]

        print "Args... CTLid: %s neutralFrame %i\n" % (ctlId,self.NEUTRAL_TIME)




        selectionList = om.MGlobal.getActiveSelectionList()
        dagIterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)

        CTL_TREE = self.createCTLgroupsList(dagIterator, ctlId)

        allStartingWeights = self.getNodeWeightList(CTL_TREE)
        allCurrentGenWeights = self.getNodeWeightList(CTL_TREE)

        print "allStartingWeights: %s" % allStartingWeights

        self.STARTING_TIME = cmds.currentTime(query=True)
        print "NEUTRAL_FRAME: %i, STARTING_FRAME: %i" % (self.NEUTRAL_TIME, self.STARTING_TIME)
        allNeutralWeights = self.getNodeWeightAtTime(CTL_TREE, self.NEUTRAL_TIME)

        print "allNeutralWeights: %s" % allNeutralWeights



        strongestShapes = self.getStrongestShapes(allStartingWeights, allNeutralWeights)

        print strongestShapes

        minMaxWeights = self.getMinMaxWeight(CTL_TREE)

        allSymmetryNames = self.getSymmetryNames(CTL_TREE)

        print allSymmetryNames

        guiTemp = GUI(CTL_TREE,allStartingWeights,allNeutralWeights,allCurrentGenWeights,
                      strongestShapes,minMaxWeights,allSymmetryNames)


        # Skeleton working stub
        print "Stub 1"

        # # API 1.0
        # selectionList = om.MSelectionList()
        # om.MGlobal.getActiveSelectionList(selectionList)

    def parseArguments(self, args):
        '''
        The presence of this function is not enforced,
        but helps separate argument parsing code from other
        command code.
        '''

        ctlShortFlagName = '-cis'
        ctlLongFlagName = '-controllerIdentifierString'
        neutralShortFlagName = '-nf'
        neutralLongFlagName = '-neutralFrame'

        # The following MArgParser object allows you to check if specific flags are set.
        argData = om.MArgParser(self.syntax(), args)
        print "argData: %s" % argData

        noFlag = True
        flagParams = []
        if argData.isFlagSet(ctlShortFlagName):
            # In this case, we print the passed flags's three parameters, indexed from 0 to 2.
            flagParams.append(argData.flagArgumentString(ctlShortFlagName, 0))
            noFlag = False
        if argData.isFlagSet(neutralLongFlagName):
            # In this case, we print the passed flags's three parameters, indexed from 0 to 2.
            flagParams.append(argData.flagArgumentDouble(neutralLongFlagName, 0))
            noFlag = False
        if noFlag:
            sys.stderr.write(
                "ERROR: No Control Identifier String Provided with function call e.g -cis 'CTL'\n"
            )

        return flagParams


    def createCTLgroupsList(self, pSelectionListIterator, ctlIdString):
        ''' Create a List of CTL group classes '''
        # Create an MDagPath object which will be populated on each iteration.

        if pSelectionListIterator.isDone():
            sys.stderr.write(
                "ERROR: No CTL groups selected. Select in Outliner View\n"
            )

        CTL_GROUP_OPTIONS = ['eye', 'brow', 'mouth', 'lower', 'upper', 'nose', 'ear', 'neck', 'chin', 'lip']


        dagPath = om.MDagPath()
        CTL_TREE = {}
        while (not pSelectionListIterator.isDone()):
            # Populate our MDagPath object. This will likely provide
            # us with a Transform node.
            dagPath = pSelectionListIterator.getDagPath()
            print dagPath
            dagPathStr = str(dagPath)
            print dagPathStr
            # self.printDagNodeInfo(dagPath)

            # Change Group name to a shorter name
            for cName in CTL_GROUP_OPTIONS:
                if cName in dagPathStr:
                    selectedGroupShort = cName
                else:
                    selectedGroupShort = dagPathStr[dagPathStr.rfind('|')+1:]
            print "New group name:%s" % selectedGroupShort

            # Get all Controllers
            leafTransformsLong = cmds.ls(dagPathStr, long=True, dag=True, allPaths=True, leaf=True)

            CTLgroup = {}
            for leaf in leafTransformsLong:
                longName = leaf[:leaf.rfind('|')]
                shortName = leaf[leaf.rfind('|') + 1:leaf.find('Shape')]
                if ctlIdString in shortName:
                    tempNode = CTLnode.createCTLNodePerTranslate(longName, selectedGroupShort)
                    for node in tempNode:
                        print node
                        keyName = node.translateName
                        CTLgroup[keyName] = node

            # Add to Tree and advance to the next item
            CTL_TREE[selectedGroupShort] = CTLgroup
            pSelectionListIterator.next()

        return CTL_TREE

    def getNodeWeightList(self, CTL_tree):


        groupDict = {}
        for key,group in CTL_tree.iteritems():
            nodeDict = {}
            for key2, node in group.iteritems():
                nodeDict[node.translateName] = node.weight

            groupDict[key] = nodeDict

        return groupDict

    def getMinMaxWeight(self, CTL_tree):


        groupDict = {}
        for key,group in CTL_tree.iteritems():
            nodeDict = {}
            for key2, node in group.iteritems():
                nodeDict[node.translateName] = node.weightMinMax

            groupDict[key] = nodeDict

        return groupDict

    def getNodeWeightAtTime(self, CTL_tree, time):

        if time:
            cmds.currentTime(time)

        groupDict = {}
        for key,group in CTL_tree.iteritems():
            nodeDict = {}
            for key2, node in group.iteritems():
                attrWeight = cmds.getAttr(node.translateName)
                nodeDict[node.translateName] = attrWeight

            groupDict[key] = nodeDict

        if time:
            cmds.currentTime(self.STARTING_TIME)

        return groupDict

    def getStrongestShapes(self, currentTree, neutralTree):

        sortedTree = {}
        for key1, group1 in currentTree.iteritems():
            neutralGroup = neutralTree[key1]
            diffDict = {k: abs(group1[k] - neutralTree.get(k, 0)) for k in group1.keys()}
            filteredDict = dict((k, v) for k, v in diffDict.iteritems() if v > 0.05)
            sortedDict = sorted(filteredDict.items(), key=lambda x: x[1], reverse=True)
            sortedTree[key1] = sortedDict

        return sortedTree

    def getSymmetryNames(self, CTL_tree):

        leftRightDict = {'_L_': '_R_', '_l_': '_r_', 'left':'right','Left':'Right', 'l_':'r_' }

        groupDict = {}
        for key,group in CTL_tree.iteritems():
            nodeDict = {}
            for key2, node in group.iteritems():
                for keys,values in leftRightDict.iteritems():
                    key_temp = copy.copy(key2)
                    breakFlag = False
                    if keys in key2 or key2.startswith('l_'):
                        # print "YEah Left"
                        replaceKey = key_temp.replace(keys,values,1)
                        # print replaceKey
                        nodeDict[key_temp] = replaceKey
                        breakFlag = True
                    elif values in key2 or key2.startswith('r_'):
                        # print "yeah right"
                        replaceKey = key_temp.replace(values,keys,1)
                        # print replaceKey
                        nodeDict[key_temp] = replaceKey
                        breakFlag = True

                    if breakFlag:
                        break

                if key2 not in nodeDict:
                    nodeDict[key2] = key2

                    # else:
                    #     nodeDict[key2] = key2

            groupDict[key] = nodeDict

        return groupDict

