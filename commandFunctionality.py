import sys
import maya.api.OpenMaya as om
import maya.cmds as cmds

##########################################################
# Plug-in
##########################################################
class Main(om.MPxCommand):

    def __init__(self):
        ''' Constructor. '''
        om.MPxCommand.__init__(self)

    def doIt(self, args):

        # Skeleton working stub
        print "Stub In 9"


        selectionList = om.MGlobal.getActiveSelectionList()
        dagIterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)

        self.createCTLgroupsList(dagIterator)


        # Skeleton working stub
        print "Stub 9"

        # # API 1.0
        # selectionList = om.MSelectionList()
        # om.MGlobal.getActiveSelectionList(selectionList)

    def createCTLgroupsList(self, pSelectionListIterator):
        ''' Create a List of CTL group classes '''
        # Create an MDagPath object which will be populated on each iteration.

        if pSelectionListIterator.isDone():
            sys.stderr.write(
                "ERROR: No CTL groups selected. Select in Outliner View\n"
            )

        CTL_GROUP_OPTIONS = ['eye', 'brow', 'mouth', 'lower', 'upper', 'nose', 'ear', 'neck', 'chin', 'lip']


        dagPath = om.MDagPath()

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

            for leaf in leafTransformsLong:
                longName = leaf[:leaf.rfind('|')]
                shortName = leaf[leaf.rfind('|') + 1:leaf.find('Shape')]
                nodeRef = cmds.listConnections(longName, destination=True, source=False, t="blendShape")
                if nodeRef:
                    print shortName


            # Advance to the next item
            pSelectionListIterator.next()


