import sys
import maya.api.OpenMaya as om
import maya.cmds as cmds

class CTLnode():

    def __init__(self,longname, selectedGroupShort):
        ''' Constructor. '''
        self.DAGpath = longname
        self.name = longname[longname.rfind('|') + 1:]
        self.minXYZ = cmds.getAttr(longname + '.minTransLimit')
        self.maxXYZ = cmds.getAttr(longname + '.maxTransLimit')
        self.weight = cmds.getAttr(longname + '.translate')
        self.startingWeight = cmds.getAttr(longname + '.translate')
        self.groupName = selectedGroupShort

    def __str__(self):
        return "Group: %s CTL: %s, Val: %s" % (self.groupName, self.name, self.weight)


class GUI():

    def __init__(self, CTL_TREE):

        self.ctlTree = CTL_TREE

        winID = 'rigUI'

        if cmds.window(winID, exists=True):
            cmds.deleteUI(winID)
        cmds.window(winID)

        cmds.columnLayout("columnLayout")

        # Add controls into this Layout
        cmds.text(label="Mutate Rate Lower:")
        mRateLower = cmds.floatField("mRateLower", minValue=0.0, maxValue=1.0, value=0.0, editable=True,
                                      parent="columnLayout")
        cmds.text(label="Mutate Rate Upper:")
        mRateUpper = cmds.floatField("mRateUpper", minValue=0.0, maxValue=1.0, value=0.0, editable=True,
                                      parent="columnLayout")
        cmds.button(label='Random', command='randomMizeCTLs(mRateLower,mRateUpper)')

        # Display the window
        cmds.showWindow()

    def randomMizeCTLs(self, mRateLower, mRateUpper):
        print "Randomise"

##########################################################
# Plug-in
##########################################################
class Main(om.MPxCommand):

    def __init__(self):
        ''' Constructor. '''
        om.MPxCommand.__init__(self)

    def doIt(self, args):

        # We recommend parsing your arguments first.
        argVals = self.parseArguments(args)

        # Skeleton working stub
        print "Stub In 7"


        selectionList = om.MGlobal.getActiveSelectionList()
        dagIterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)

        CTL_TREE = self.createCTLgroupsList(dagIterator, argVals)

        guiTemp = GUI(CTL_TREE)

        print CTL_TREE


        # Skeleton working stub
        print "Stub 7"

        # # API 1.0
        # selectionList = om.MSelectionList()
        # om.MGlobal.getActiveSelectionList(selectionList)

    def parseArguments(self, args):
        '''
        The presence of this function is not enforced,
        but helps separate argument parsing code from other
        command code.
        '''

        kShortFlagName = '-cis'
        kLongFlagName = '-controllerIdentifierString'

        # The following MArgParser object allows you to check if specific flags are set.
        argData = om.MArgParser(self.syntax(), args)
        print "argData: %s" % argData

        if argData.isFlagSet(kShortFlagName):
            # In this case, we print the passed flags's three parameters, indexed from 0 to 2.
            flagParam0 = argData.flagArgumentString(kShortFlagName, 0)
        else:
            sys.stderr.write(
                "ERROR: No Control Identifier String Provided with function call e.g -cis 'CTL'\n"
            )

        return flagParam0


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
            print "New group name:%s" % selectedGroupShort

            # Get all Controllers
            leafTransformsLong = cmds.ls(dagPathStr, long=True, dag=True, allPaths=True, leaf=True)

            CTLgroup = []
            for leaf in leafTransformsLong:
                longName = leaf[:leaf.rfind('|')]
                shortName = leaf[leaf.rfind('|') + 1:leaf.find('Shape')]
                if ctlIdString in shortName:
                    tempNode = CTLnode(longName, selectedGroupShort)
                    print tempNode
                    CTLgroup.append(tempNode)

            # Add to Tree and advance to the next item
            CTL_TREE[selectedGroupShort] = CTLgroup
            pSelectionListIterator.next()

        return CTL_TREE


