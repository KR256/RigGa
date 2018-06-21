import sys
import maya.api.OpenMaya as om

##########################################################
# Plug-in
##########################################################
class printPathsCmd(om.MPxCommand):

    def __init__(self):
        ''' Constructor. '''
        om.MPxCommand.__init__(self)

    def doIt(self, args):
        # Skeleton working stub
        print "Hello World 2!"

        # # User selection stub
        # selectionList = om.MGlobal.getActiveSelectionList()
        # dagIterator = om.MItSelectionList(selectionList, om.MFn.kDagNode)
        #
        # if dagIterator.isDone():
        #     sys.stderr.write(
        #         "No CTL groups selected for: %s\n. Select in Outliner View\n" % rigGACmd.kPluginCmdName
        #     )
        # else:
        #     # Print the paths of the selected DAG objects.
        #     print '======================='
        #     print ' SELECTED DAG OBJECTS: '
        #     print '======================='
        #     self.printSelectedDAGPaths(dagIterator)

        # # API 1.0
        # selectionList = om.MSelectionList()
        # om.MGlobal.getActiveSelectionList(selectionList)

    # def printSelectedDAGPaths(self, pSelectionListIterator):
    #     ''' Print the DAG path(s) of the selected object(s). '''
    #
    #     # Create an MDagPath object which will be populated on each iteration.
    #     dagPath = om.MDagPath()
    #
    #     # Obtain a reference to MFnDag function set to print the name of the DAG object
    #     dagFn = om.MFnDagNode()
    #
    #     # Perform each iteration.
    #     while (not pSelectionListIterator.isDone()):
    #
    #         # Populate our MDagPath object. This will likely provide
    #         # us with a Transform node.
    #         dagPath = pSelectionListIterator.getDagPath()
    #         try:
    #             # Attempt to extend the path to the shape node.
    #             dagPath.extendToShape()
    #         except Exception as e:
    #             # Do nothing if this operation fails.
    #             pass
    #
    #         # Obtain the name of the object.
    #         dagObject = dagPath.node()
    #         dagFn.setObject(dagObject)
    #         name = dagFn.name()
    #
    #         # Obtain the compatible function sets for this DAG object.
    #         # These values refer to the enumeration values of MFn
    #         fntypes = []
    #         fntypes = om.MGlobal.getFunctionSetList(dagObject)
    #
    #         # Print the DAG object information.
    #         print name + ' (' + dagObject.apiTypeStr + ')'
    #         print '\tDAG path: [' + str(dagPath.fullPathName()) + ']'
    #         print '\tCompatible function sets: ' + str(fntypes)
    #
    #         # Advance to the next item
    #         pSelectionListIterator.next()
    #
    #     print '====================='