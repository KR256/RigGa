########################################################################
# DESCRIPTION:
#
# Produces the command "pyHelloWorld".
#
# This is a simple demonstration of how to use a Python plug-in.
# A "Hello World" text is output to the script editor window.
#
# To use, make sure that pyHelloWorldCmd.py is in your MAYA_PLUG_IN_PATH,
# then do the following:
# #
#   import maya
#   maya.cmds.loadPlugin("pyHelloWorldCmd.py")
#   maya.cmds.pyHelloWorld()
#
########################################################################

import sys
import maya.api.OpenMaya as om
import commandFunctionality

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass

kPluginCmdName = "rigGACommand"


##########################################################
# Plug-in initialization.
##########################################################
def cmdCreator():
    ''' Creates an instance of our command class. '''
    return commandFunctionality.Main()


def syntaxCreator():
    ''' Defines the argument and flag syntax for this command. '''
    ctlShortFlagName = '-cis'
    ctlLongFlagName = '-controllerIdentifierString'
    neutralShortFlagName = '-nf'
    neutralLongFlagName = '-neutralFrame'
    otherFaceIdsLong = '-otherFaceIds'
    otherFaceIdsShort = '-oid'
    rigOrEmulateShort = '-roe'
    rigOrEmulateLong = '-rigOrEmulate'
    syntax = om.MSyntax()

    # In this example, our flag will be expecting a numeric value, denoted by OpenMaya.MSyntax.kDouble.
    syntax.addFlag(ctlShortFlagName, ctlLongFlagName, om.MSyntax.kString)
    syntax.addFlag(neutralShortFlagName, neutralLongFlagName, om.MSyntax.kDouble)
    syntax.addFlag(otherFaceIdsShort, otherFaceIdsLong, om.MSyntax.kString)
    syntax.addFlag(rigOrEmulateShort, rigOrEmulateLong, om.MSyntax.kString)

    # ... Add more flags here ...

    return syntax


def initializePlugin(mobject):
    ''' Initializes the plug-in.'''
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.registerCommand(kPluginCmdName, cmdCreator, syntaxCreator )
    except:
        sys.stderr.write("Failed to register command: %s\n" % kPluginCmdName)


def uninitializePlugin(mobject):
    ''' Uninitializes the plug-in '''
    mplugin = om.MFnPlugin(mobject)
    try:
        mplugin.deregisterCommand(kPluginCmdName)
    except:
        sys.stderr.write("Failed to unregister command: %s\n" % kPluginCmdName)