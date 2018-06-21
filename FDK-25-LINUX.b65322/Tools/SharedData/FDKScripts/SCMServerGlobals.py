#***********************************************************************#
# This defines in a single place the servers and paths used by the Pre-Release,
# ReleaseOTF, PrereleaseOTF, WINDISGServer, and WINSyncSCMFileServer scripts.
__copyright__ = """Copyright 2014 Adobe Systems Incorporated (http://www.adobe.com/). All Rights Reserved.
"""

import os
import sys

# Paths to the file server, where we keep an image of what's in  perforce.
SCM_SERVER_NAME = "sjshare"
SCM_FILE_SERVER = "%s.corp.adobe.com" % SCM_SERVER_NAME
SCM_FILE_SERVER_VOLUME = "Type"
SCM_FILE_SERVER_SCM_ROOT =  ["OpenTypeBuilds",  "Perforce"]
SCM_SYNC_WHERE_AM_I_FILENAME = "scm_sync_server_address.txt"
DSIG_SERVER_WHERE_AM_I_FILENAME = "dsig_server_address.txt"
kSyncLabel = "DoSync:" # Used to request the WinSyncSCMServer.py to do async.
WIN_SCM_SERVER_LOCAL_DRIVE = "Z:"
MAC_SCM_SERVER_LOCAL_DRIVE = "/Volumes/%s" % SCM_FILE_SERVER_VOLUME


# Standard Perforce settings/
kP4PORT = "boxer.corp.adobe.com:1740"

# Note that the two ports are used by two scripts on the same system - they can't be the same!
kDSIG_SERVICE_PORT = 50008
kSCM_SYNC_SERVICE_PORT = 50009
if os.name == "nt":
	KP4CLIENT_AutoSync = "fontuid_auto"
	KP4CLIENT_Release = "fontuid_release"
	KP4CLIENT_PreRelease = "fontuid_prerelease"
else:
	KP4CLIENT_AutoSync = "fontuid_auto_osx"
	KP4CLIENT_Release = "fontuid_release_osx"
	KP4CLIENT_PreRelease = "fontuid_prerelease_osx"

# These can only run under Windows, so I can hardwire the Windows path.
class FDKEnvError(KeyError):
	pass

def findFDKDirs():
	fdkScriptsDir = None
	fdkToolsDir = None
	fdkSharedDataDir = None
	""" Look up the file path to find the "Tools" directory;
	then add the os.name for the executables, and .'FDKScripts' for the scripts.
	"""
	dir = os.path.dirname(__file__)
	while dir:
		if os.path.basename(dir) == "Tools":
			fdkScriptsDir = os.path.join(dir, "SharedData", "FDKScripts")
			if sys.platform == "darwin":
				fdkToolsDir = os.path.join(dir, "osx")
			elif os.name == "nt":
				fdkToolsDir = os.path.join(dir, "win")
			else:
				print "Fatal error: un-supported platform %s %s." % (os.name, sys.platform)
				raise FDKEnvError

			if not (os.path.exists(fdkScriptsDir) and os.path.exists(fdkToolsDir)):
				print "Fatal error: could not find  the FDK scripts dir %s and the tools directory %s." % (fdkScriptsDir, fdkToolsDir)
				raise FDKEnvError
 
			# the FDK.py bootstrap program already adds fdkScriptsDir to the  sys.path;
			# this is useful only when running the calling script directly using an external Python.
			if not fdkScriptsDir in sys.path:
				sys.path.append(fdkScriptsDir)
			fdkSharedDataDir = os.path.join(dir, "SharedData")
			break
		dir = os.path.dirname(dir)
	return fdkToolsDir,fdkSharedDataDir

fdkToolsDir,fdkSharedDataDir = findFDKDirs()
fdkToolsDir = os.path.dirname(fdkToolsDir)

SIGN_TOOL_PATH = os.path.join(fdkToolsDir, "MSSignTools\\signotf.cmd" )
TIME_STAMP_TOOL_PATH = os.path.join(fdkToolsDir, "MSSignTools\\tstampotf.cmd" )
