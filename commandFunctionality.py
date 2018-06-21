import sys
import maya.api.OpenMaya as om

##########################################################
# Plug-in
##########################################################
class Main(om.MPxCommand):

    def __init__(self):
        ''' Constructor. '''
        om.MPxCommand.__init__(self)

    def doIt(self, args):

        # Skeleton working stub
        print "Stub In 2"

        selectionList = om.MGlobal.getActiveSelectionList()
        dagIterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)

        CTL_groups_list = self.createCTLgroupsList(dagIterator)


        # Skeleton working stub
        print "Stub 2"

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

        dagPath = om.MDagPath()

        # Perform each iteration.

        # Print the paths of the selected DAG objects.
        print '======================='
        print ' SELECTED DAG OBJECTS: '
        print '======================='

        while (not pSelectionListIterator.isDone()):
            # Populate our MDagPath object. This will likely provide
            # us with a Transform node.
            dagPath = pSelectionListIterator.getDagPath()
            self.printDagNodeInfo(dagPath)


            # verticleDagIterator = om.MItDag(om.MItDag.kDepthFirst,
            #                               om.MFn.kTransform)

            # Advance to the next item
            pSelectionListIterator.next()

        print '====================='

    def printDagNodeInfo(self, dPath):
        # Obtain the name of the object.

        # Obtain a reference to MFnDag function set to print the name of the DAG object
        dagFn = om.MFnDagNode()
        dagObject = dPath.node()

        dagFn.setObject(dagObject)
        name = dagFn.name()

        # Obtain the compatible function sets for this DAG object.
        # These values refer to the enumeration values of MFn
        fntypes = []
        fntypes = om.MGlobal.getFunctionSetList(dagObject)

        # Print the DAG object information.
        print name + ' (' + dagObject.apiTypeStr + ')'
        print '\tDAG path: [' + str(dPath.fullPathName()) + ']'
        print '\tCompatible function sets: ' + str(fntypes)
