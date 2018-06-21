#MakeCIDFont

__copyright__ = """Copyright 2015 Adobe Systems Incorporated (http://www.adobe.com/). All Rights Reserved.
"""


__doc__ = """
MakeCIDFont v1.18 April 13 2016
MakeCIDFont  [ -o <output file path>] [-fh] [-nh] [-ns] [-frf] [-nhr] [-f <path to cidfontinfo file>] [-s <subset file path>]   [-l <path to layout file>]   [-lg <path to LanguageGroup file>] [-vf <path to rotated vertical glyph definition file>]
MakeCIDFont  [-u] [-h]

MakeCIDFont will use row font files and meta data files to build a new Type 1 cid font file.

"""

__help__ = """
Options:
-u	Show usage
-h	Show help
-nhr   Suppress hint report
-l <path to layout file> 	Use alternate path to layout definition file. Default is under FDK/Tools/SharedData/CID charsets/<layout name from cidfontinfo file>
-f <path to cidfontinfo file> 	Use alternate path to cidfontinfo file. Default is "cidfontinfo",  in the current working directory.
-s <subset file path> 	Use alternate path to subset definition file. Default is under FDK/Tools/SharedData/CID charsets/<subset name from cidfontinfo file>
-lg <path to LanguageGroup file> 	Use alternate path to LanguageGroup definition file. Default is under FDK/Tools/SharedData/CID charsets/<layout name from cidfontinfo file>.LanguageGroups
-vf <path to  rotated vertical glyph definition file> 	Use alternate path to rotated vertical glyph definition  file. Default is under FDK/Tools/SharedData/CID charsets/<layout name from cidfontinfo file>.VertLayout
-fh	Force auto-hinting of all fonts.
-nh  never hint fonts.
-ns	Suppress hint substitution in all fonts: only one group of hints will be used for an entire glyph.
-frf	Force synthesizing rotated fonts from source row fonts

Assumptions and File Formats.

MakeCIDFont.py assumes that the source font data has a particular
structure. The directory location of the cidfontinfo file defines the
root directory for a font's data. All the row fonts are assumed to be
two directory levels down from the root directory, to be Type 1 (not OTF
or CFF), and  to have the name "font.ps" or "font.pfa". A first level
subdirectory is referred to as a hint directory. All row fonts under a
hint directory must have the same LanguageGroup value, and the same
global metric, alignment and hint information. The second level
directories are referred to as row font directories.

Some row font directories are synthesized by rotating other row font
directories. MakeCIDFont will build these only if they are missing;
otherwise, it will use the existing row font data.

MakeCIDFont will check all row fonts to verify that they have been
hinted, and, if necessary, had global coloring applied. If not,
MakeCIDFont will apply hinting and global coloring, where needed.

The key/value pairs in the cidfontinfo file have two uses. One is to
override the default values for the global name and metric values The
other is to specify the names and paths for the various shared meta-data
files which provide additional information for building the CID font
file. For all font dict keys that are not specified by the cidfontinfo
file, the final output CID font file will inherit the global name and
metric values from the first row font used.

The keywords in the following example cidfontinfo file are all required,
and will override those from the first row font.

Example entries in cidfontinfo file:
FontName      (KozMinPro-Bold)
FullName      (Kozuka Mincho Pro OpenType Bold)		
FamilyName    (Kozuka Mincho Pro OpenType)
Weight	(Bold)
version       (1.012)
Registry      (Adobe)
Ordering      (Japan1)
Supplement    4
Layout        (AJ15-J15)
AdobeCopyright (Copyright 1997 Adobe Systems Incorporated. All Rights Reserved.)
FSType	8

The following  keys are optional.
Trademark     (Kozuka Mincho is either a registered trademark or trademark of Adobe Systems Incorporated in the United States and/or other countries.)
Subset	(Kana)
HintDictParams	(Kanji/r30)

If the HintDictParams keyword is provided, then makeCIDFont will copy the font global metrics and hint
info from the specified row font to all the other fonts under the same hint directory.

The cidfontinfo file  must also contain the keyword "Layout". The value
string must match a file name under the directory
"FDK/Tools/SharedData/CID charsets/.

The layout file provides the location of the row fonts relative to the
cidfontinfo file, and the mapping from glyph name to CID.
Example entry in cidfontinfo file:
Layout        (AJ15-J15)

Each line in a layout file has four fields: 
CID (as a decimal value), the hint directory name, the row font directory name, and the glyph name.
Example lines in a layout file:
0	Generic	NotDef	NOTDEF
1	Proportional	Roman	space
17142	Kanji	K3r7C	c4C

The cidfontinfo file  may also contain the keyword "Subset". The value
string must match the file name "<subset-name>"  under the directory
"FDK/Tools/SharedData/CID charsets/'". The path may be overriden with 
the option "-s <path>".

The subset file restricts the range of CID's included in the font.
Example entry in cidfontinfo file:
Layout        (AJ15-J15)

Each line in a subset file must contain only one text string, containing
no white-space. This may be either a single decimal CID value, or a
range of CID values specified as two CID values separated by a hyphen.
The list of CID values specified by the union of all the lines of the
subset file are used as a filter to select only the specified CID values
from the list of CID values specified in the layout file. Example lines
in a subset file:
0
232-233
238-240
243
245-258

The LanguageGroup file controls the LanguageGroup assigned to a hint
dictionary in the cid font's FDArray, and whether it will get global
coloring. Each line in a layout file has four fields:
hint directory name, row font directory name, LanguageGroup value, and Global Coloring boolean value.
Example lines in a LanguageGroup file:
Generic	NotDef	0	0
Kana	Hiragana	1	1

LanguageGroup should be set to 1 only for those fonts whose glyphs are
ideographs, and have the same horizontal and vertical advance widths.
Note that the LanguageGroup value must be set the same for all row fonts
under a hint directory. If you do not do this, the result is two
different hint dictionaries in the CID font's FDArray which differ only
in their Language group value.

Global Coloring can be set to 1 (on) or 0 (off). It must be set to 0 for
fonts with LanguageGroup == 0. It should be applied only to those fonts
whose glyphs are ideographs.

The rotated vertical glyph definition file (VertLayout) controls which
row fonts will be synthesized, if they are missing. It has a format
similar to the Layout file:
source CID, rotated CID, baseLineAdjustment, y Offset.

Example lines in a rotated vertical glyph definition file :
1	8720	120	880
10	8729	120	880
100	8819	120	880
101	8820	120	880
102	8821	120	880
103	8822	120	880

The hint directory and row font directory names of the synthesized row
font are taken from the layout file, from the values for the source and
destination CIDs. The last two fields give the baseLineAdjustment and
yOffset values. To make a rotated glyph, it is first rotated 90 degrees
clockwise around its point of origin.  It is then shifted up by the
yOffset, and shifted right by the baseLineAdjustment values. The goal is
to return the center of the glyph BBox to the same coordinate position as
it originally had  For most glyphs, the baseLineAdjustment should be set
to the value of the difference between the baseline and the origin's 
y-coordinate, and yOffset should be set to (em-square size -
baseLineAdjustment).

Notes

It can take on the order of 30 to 60 minutes to hint all the row fonts.

The row fonts are merged by alphabetic order of the
<hint-directory/row-font-directory> paths.

The glyphs included in a font must include CID 0, the .notdef glyph. The
output font cannot be made without this glyph,.

All row fonts must be Type 1, not CFF or OTF fonts.

We chose to use the Type 1 format for row fonts because most existing
data is already int his format, and because this format allows adding a
prefix string to the font file to mark it as having been hinted.

If a row font already has global coloring, the addGlobalColor program
will simply copy the data without changing it; to get new global
coloring, you must first re-hint the font, which will remove all global
coloring operators.

"""

import os
import sys
import time
import re
import tempfile
import shutil
import FDKUtils
from subprocess import Popen, PIPE

kOutputFileParentDir = "C1E0"
kOutputFileName = "cidfont.ps"
kRowFontnames = ["font.pfa", "font.ps"] # first name in list is used when generated new rotated fonts.
kCIDFontInfoName = "cidfontinfo"
kTempMergeFont = "tempfont"
kCharsetDir = os.path.join("SharedData", "CID charsets") # relative path to the parent directory for all the layout and subset files
kLanguageGroupFileName = "LanguageGroups"
kVertLayoutFileExtension = "VertLayout"
kCIDFontInfokeyList = [ # Key names in the cidfontinfo file that are required by MakeCIDFont.
	"FontName",
	"FullName",
	"FamilyName",
	"Registry",
	"Ordering",
	"Supplement",
	"Layout",
	"AdobeCopyright",
	"Trademark",
	"FSType",
	]

kHintDictParams = "HintDictParams"

kACPrefix = "%%FDK MakeCIDFont AC" + os.linesep # Prefix added to hinted row fonts to mark that they have been hinted
kGCPrefix = "%%FDK MakeCIDFont GC"+ os.linesep # Prefix added to global-colored row fonts to mark that they have been global-colored

class FDKEnvironmentError(AttributeError):
	pass

class LayoutParseError(KeyError):
	pass

class MissingFontError(KeyError):
	pass

class OptionParseError(KeyError):
	pass

class MergeFontError(KeyError):
	pass

def logMsg(*args):
	for s in args:
		print s

class ToolPaths:
	""" Collect and validate the paths to the several programs and essential directories that are used by MakeCIDFont.py.
	Note that I do not simply check if the program files exist. This is partly becuase they have different extensions under
	Mac and Windows, and partly becaue they are really command files that call the real programs - hence I have
	to execute the program to make sure it can be called. I call the '-u" option for each program, and check for a string
	that is in the output from all these programs.

	Also, the hinting program addGlobalColor is not available in all environments, and so is not reported when missing."""
	def __init__(self):
		try:
			self.exe_dir, fdkSharedDataDir = FDKUtils.findFDKDirs()
		except FDKUtils.FDKEnvError:
			raise FDKEnvironmentError
	
		if not os.path.exists(self.exe_dir ):
			logMsg("The FDK executable dir \"%s\" does not exist." % (self.exe_dir))
			logMsg("Please re-install the FDK. Quitting." )
			raise FDKEnvironmentError

		toolList = ["tx", "autohint", "addGlobalColor", "mergeFonts", "rotateFont"]
		missingTools = []
		self.missingGC = 0
		for name in toolList:
			toolPath = name
			if not missingTools:
				exec("self.%s = toolPath" % (name))
				command = "%s -u 2>&1" % toolPath
				report = FDKUtils.runShellCmd(command)
				if ("version" not in report) and ("options" not in report) and ("Option" not in report):
					if name == "addGlobalColor":
						self.missingGC = 1
					else:
						missingTools.append(name)
						print report
						print command, len(report), report
		if missingTools:
			logMsg("Please re-install the FDK. The executable directory \"%s\" is missing the tools: < %s >." % (self.exe_dir, ", ". join(missingTools)))
			logMsg("or the files referenced by the shell scripts are missing.")
			raise FDKEnvironmentError
				

		self.charsetDir = os.path.join( os.path.dirname(self.exe_dir), kCharsetDir)
		if not os.path.exists(self.charsetDir ):
			logMsg("The cid charset file directory \"%s\" does not exist." % (self.charsetDir))
			logMsg("Please re-install the FDK. Quitting.")
			raise FDKEnvironmentError

class ToolOptions:
	""" Set default values for all options, and then process the user specified values.""" 
	def __init__(self, args):
		self.forceHint = 0
		self.noHintSubstitution = 0
		self.noACReport = 0
		self.forceMakeRotated = 0
		self.cidfontinfoPath = kCIDFontInfoName
		self.outFilePath = None
		self.subsetPath = None
		self.layoutPath = None
		self.vertLayoutPath = None
		self.languageGroupPath = None
		self.neverHint = 0
		
		i = 0
		numArgs = len(args)
		# MakeCIDFont  [ -o <output file path>]  [-fh] [-f <path to cidfontinfo file>] [-s <subset file path]   [-l <path to layout file>]  [-lg <path to language group file>] [-vf <path to rotated vertical glyph definition file>]
		while i < numArgs:
			arg = args[i]
			if arg == "-u":
				logMsg(__doc__)
				raise OptionParseError
			elif arg == "-h":
				logMsg(__doc__)
				logMsg(__help__)
				raise OptionParseError
			elif arg in ["-makelg", "-makev"]: # Hidden options, to make LanguageGroups file and VertLayout file
									# See functions at end of file for more info.
				pass
			elif arg == "-o":
				i +=1
				self.outFilePath = args[i]
			elif arg == "-fh":
				self.forceHint = 1
			elif arg == "-nh":
				self.neverHint = 1
			elif arg == "-ns":
				self.noHintSubstitution = 1
			elif arg == "-nhr":
				self.noACReport = 1
			elif arg == "-frf":
				self.forceMakeRotated = 1
			elif arg == "-f":
				i +=1
				self.cidfontinfoPath = args[i]
			elif arg == "-s":
				i +=1
				self.subsetPath = args[i]
			elif arg == "-l":
				i +=1
				self.layoutPath = args[i]
			elif arg == "-lg":
				i +=1
				self.languageGroupPath = args[i]
			elif arg == "-vf":
				i +=1
				self.vertLayoutPath = args[i]
			else:
				logMsg("Error parsing options. Unrecognized option '%s'. Quitting." % (arg))
				raise OptionParseError
			i +=1
		# end option processing loop.

		if not os.path.isfile(self.cidfontinfoPath):
			logMsg("Could not find cidfontinfo file at: '%s'. Quitting." % (self.cidfontinfoPath))
			raise OptionParseError
		return


def getFontInfo(fontinfoPath):
	""" Read in the key-value pairs from the cidfontinfo file."""
	fontinfo = {}
	fi = file(fontinfoPath, "rU")
	lines =  fi.readlines()
	fi.close()
	for line in lines:
		match = re.match(r"(\S+)\s+(\S.*)", line)
		if match:
			key = match.group(1)
			value = match.group(2)
			if value[0] == "(":
				value = value[1:-1]
			elif value[0] == "[":
				value = value[1:-1]
			elif value.lower() == "true":
				value = 1
			elif value.lower() == "false":
				value = 0
			if key == kHintDictParams:
				hintDictSource  = fontinfo.get(kHintDictParams, {})
				hintDictName = value.split("/")[0]
				try:
					oldValue = hintDictSource[hintDictName]
					logMsg("Error: The hint dict %s is listed more than once in the cidfontinfo file as a source hint dict." % (hintDictName))
				except KeyError:
					if not os.path.exists(value):
						logMsg("Error: The hint dict source dir  '%s' is referenced  in the cidfontinfo file, but does not exist; it will not be used." % (value))
					else:
						hintDictSource[hintDictName] = value
						fontinfo[key] = hintDictSource
			else:
				fontinfo[key] = 	value	
				
		else:
                        line = line.strip()
                        if line:
				logMsg("Warning: could not parse line in cidfontinfo file: '%s'." % (line))

	keys =  fontinfo.keys()
	missingKey = 0
	for key in kCIDFontInfokeyList:
		if not fontinfo.has_key(key):
			missingKey = 1
			logMsg("Error. cidfontinfo file is  missing required key '%s'." % (key))
	if missingKey:
			logMsg("Quitting")
			raise KeyError
		
	return fontinfo

def getLayoutPaths(toolPaths, toolOptions, fontinfo):
	""" Determine the paths to the layout files and (optionally) subset file, and make sure that they exist."""

	# Get paths
	if toolOptions.layoutPath:
		layoutPath = toolOptions.layoutPath
	else:
		layoutPath = os.path.join(toolPaths.charsetDir, fontinfo["Layout"])
	print "Using layout file path: " + layoutPath	
	toolOptions.layoutPath = layoutPath

	if toolOptions.subsetPath:
		subsetPath = toolOptions.subsetPath
	else:
		subsetPath = fontinfo.get("Subset", "")
		if subsetPath:
			subsetPath = os.path.join(toolPaths.charsetDir,  subsetPath)
			print "Using subset file path: " + subsetPath	
	toolOptions.subsetPath = subsetPath

	vertLayoutFileName = fontinfo.get("VertLayout", "")
	if toolOptions.vertLayoutPath:
		vertLayoutPath = toolOptions.vertLayoutPath
	elif vertLayoutFileName:
		vertLayoutPath = os.path.join(os.path.dirname(layoutPath), vertLayoutFileName)
	else:
		vertLayoutPath = layoutPath + "." + kVertLayoutFileExtension
	print "Using VertLayout file path: " + vertLayoutPath	
	toolOptions.vertLayoutPath = vertLayoutPath

	# Get paths
	if toolOptions.languageGroupPath:
		langGroupPath = toolOptions.languageGroupPath
	else:
		langGroupPath = toolOptions.layoutPath + "." + kLanguageGroupFileName
	print "Using LanguageGroups file path: " + langGroupPath	
	toolOptions.languageGroupPath = langGroupPath

	# Test paths
	error = 0
	if not os.path.exists(layoutPath):
		logMsg("Error. Cannot find required layout file '%s'. Quitting." % (layoutPath))
		error = 1

	if subsetPath and not os.path.exists(subsetPath):
		logMsg("Error. Cannot find required subset file '%s'. Quitting." % (subsetPath))
		error = 1

	if not os.path.exists(vertLayoutPath):
		logMsg("Warning. Cannot find  vertical glyph layout file '%s'. This may not be necessary." % (vertLayoutPath))
		toolOptions.vertLayoutPath = None

	if error:
		raise IOError


def getLayout(toolOptions):
	""" Parse the layout files, and build useful dictionaries."""
	layoutPath = toolOptions.layoutPath
	vertLayoutPath = toolOptions.vertLayoutPath
	subsetPath = toolOptions.subsetPath

	rowFontDict, cidDict, subsetDict = getRowFontDict(layoutPath, subsetPath)
	if vertLayoutPath:
		vertFontDict = getVertDict(rowFontDict, cidDict, subsetDict, vertLayoutPath)
	else:
		vertFontDict = None
	return rowFontDict, cidDict, vertFontDict	

def getLanguageGroups(toolPaths, toolOptions, fontinfo):
	""" Parse the LanguageGroup file to get the LanguageGroup setting and the
	Global Coloring on/off setting for each row font. """

	langGroupPath = toolOptions.languageGroupPath
	if not os.path.exists(langGroupPath):
		logMsg("Error. Cannot find required layout file '%s'. Quitting." % (langGroupPath))
		raise IOError
	languageGroupDict = {}
	globalColorDict  = {}
	lfp = file(langGroupPath, "rU")
	lines = lfp.readlines()
	lfp.close()
	itemList = map(lambda line: line.split(), lines)
	lineno = 0
	for entry in itemList:
		lineno += 1
		if not entry:
			continue
		if entry[0][0] == "#":
			continue
		if len(entry) != 4:
			logMsg("Error. Do not have four fields in line number %s of  '%s'. Quitting." % (lineno, langGroupPath))
			raise IOError
		try:
			val =  eval(entry[2])
		except (ValueError, NameError, SyntaxError):
			logMsg("Error. In line number %s of  '%s', LanguageGroup  field is not a number. Quitting." % (lineno, langGroupPath))
			raise IOError
		key = os.path.join(entry[0], entry[1])
		languageGroupDict[key] = val
		try:
			val =  eval(entry[3])
		except ValueError:
			logMsg("Error. In line number %s of  '%s', GlobalColor field is not a number. Quitting." % (lineno, langGroupPath))
			raise IOError
		globalColorDict[key] = val

	return languageGroupDict, globalColorDict

def getRowFontDict(layoutPath, subsetPath):
	""" Get useful dictionaries from the layout file. The one we use the most often is a dictiony where the
	key is the row font directory path, and the value is a dictionary mapping glyph names to CID values.
	Note that a glyph name may map to multiple CID values. As a result, I always put the CID value in a list."""
	subsetDict = {}
	if subsetPath:
		sf= file(subsetPath, "rU")
		lines = sf.readlines()
		sf.close()
		for line in lines:
			# example lines:
			# 	"0"
			#	"16779-20316"
			match = re.match(r"(\d+)-(\d+)\s*", line)
			if match:
				start= eval(match.group(1))
				end= eval(match.group(2))
				cid= start
				while cid <= end:
					subsetDict[cid] = 1
					cid +=1
				continue
			match = re.match(r"(\d+)\s*", line)
			if match:
				cid = eval(match.group(1))
				subsetDict[cid] = 1
			
	lf = file(layoutPath, "rU")
	lines = lf.readlines()
	lf.close()
	rowFontDict = {}
	cidDict = {}
	lineno = 0
	haveError = 0
	for line in lines:
		lineno += 1
		# example lines: " 1	Proportional	Roman	space"   and "23057	KanjiPlus	Hr6D	c62"
		match = re.match(r"(\d+)\s+(\S+)\s+(\S+)\s+(\S+)", line)
		if not match:
			logMsg("Warning: could not parse line number %s in layout file '%s'. Line: %s." % (lineno, layoutPath, line))
			haveError = 1
			continue
		name = match.group(4)
		cid = eval(match.group(1))
		if subsetDict and not subsetDict.has_key(cid):
			continue
		rowFontDir = os.path.join(match.group(2), match.group(3))
		rowDict = rowFontDict.get(rowFontDir, {})
		if rowDict.has_key(name):
			rowDict[name].append(cid)
		else:
			rowDict[name] =[cid]
		rowFontDict[rowFontDir] = rowDict
		if cidDict.has_key(cid):
			logMsg("Error: CID is from more than one glyph name at line number %s in layout file %s. Line: %s" % (lineno, layoutPath, line))
			haveError = 1
			continue
		cidDict[cid] = [rowFontDir, name]
	if haveError:
		raise LayoutParseError
	if not cidDict.has_key(0):
		logMsg("Error. The  final font must contain CID 0. This glyph is not included in the layout + subseet specification for this font.")
		raise LayoutParseError

	
	return rowFontDict, cidDict, subsetDict

def  getVertDict(rowFontDict, cidDict, subsetDict, vertLayoutPath):
	""" Collect the info needed to build rotated fonts from other row fonts.
	The VertLayout file specifies src CID, rotated CID, and x and y offsets.
	I use the info from the layout file to look up the src and dst row font paths for each CID,
	and save this with the X and Y offsets."""
	lf = file(vertLayoutPath, "rU")
	lines = lf.readlines()
	lf.close()
	lineno = 0
	haveError = 0
	vertFontDict = {}
	lastHintDict = None
	for line in lines:
		line = line.strip()
		lineno += 1
		if not line:
			continue
		if line[0] == "#":
			continue
		entry = line.split()
		if len(entry) != 4:
			logMsg("Error reading line %s in vertical layout file %s. There must be 4 fields." % (lineno, vertLayoutPath))
			haveError = 1
			print  len(entry),  entry
			sys.exit(0)
	
		srcCID = eval(entry[0])
		dstCID =  eval(entry[1])
		if subsetDict and not (subsetDict.has_key(srcCID) and subsetDict.has_key(dstCID) ):
			continue
		fontEntry =  cidDict[srcCID]
		srcRowDir = fontEntry[0]
		srcName = fontEntry[1]

		fontEntry =  cidDict[dstCID]
		rotRowDir = fontEntry[0]
		rotName = fontEntry[1]

		if rotRowDir not in rowFontDict:  
			logMsg("Error reading line %s in vertical layout file %s. The destination CID is not in the current sources: %s." % (lineno, vertLayoutPath, line))
			haveError = 1
			continue

		# make sure all numeric values can be parsed as such
		try:
			xOffset = eval(entry[2])
			yOffset = eval(entry[3])
		except  (ValueError, NameError, SyntaxError):
			logMsg("Error in line %s in vertical layout file %s. One of the last three numeric entries is not a number." % (lineno, vertLayoutPath))
			haveError = 1
			continue

		vertEntry = vertFontDict.get(rotRowDir, [srcRowDir, {}])
		vertEntry[1][srcName] = [srcName, rotName,"1000",  entry[2], entry[3]]
		vertFontDict[rotRowDir] = vertEntry

	if haveError:
		raise LayoutParseError
	return vertFontDict

def extractMergeInfo(nameList):
	hasNotdef = 0
	gaList = []
	multipleMapList = []
	listType = type([])
	for item in nameList:
		name = item[0]
		cidList = item[1]
		gaList.append("%s\t%s" % (cidList[0], name))
		if cidList[0] == 0:
			hasNotdef = 1
		if len(cidList) > 1:
			multipleMapList.append([name, cidList[1:]])
	return gaList, multipleMapList, hasNotdef

def buildMergeCommand(fontPath, dirName, rowDict, parentFontName, languageGroupDict, gaCommandList,  notDefFont):
	""" Build the glypha alias (GA) file for this row font, and add the GA file
	and font path to the merge command list. We may add more than one entry for
	this font, as the only way to merge in one glyph to several different CIDs is
	is to merge the the font more than once, each time with a different GA file.
	"""
	
	# some glyphs can be mapped to more than one CID. The only way to handle this
	# is to merge the font more than once; get all the single mapped glyphs on the first pass,
	# and the other mappings on the second and subsequent passes.
	passCount = 0
	gaList, multipleMapList, hasNotdef = extractMergeInfo(rowDict.items())
	if hasNotdef:
		notDefFont = fontPath
	while gaList:
		hintDirName = os.path.dirname(dirName)
		# write heade line for ga filer: program name, hint dir name, language group, then glyph alias list.
		gaList = ["mergeFonts %s-%s %s" %  (parentFontName, hintDirName, languageGroupDict.get(dirName,1) )] + gaList
		gaText = os.linesep.join(gaList) + os.linesep # add the list of dst<-src glyph name pairs.
		gaPath = fontPath + ".ga.%s.txt" % (passCount)
		fg = file(gaPath, "wt")
		fg.write(gaText)
		fg.close()
		gaCommandList +=  [gaPath, fontPath]
		if multipleMapList:
			gaList, multipleMapList, hasNotdef = extractMergeInfo(multipleMapList)
			if hasNotdef:
				notDefFont = fontPath
		else:
			gaList = None
		passCount += 1
	return gaCommandList, notDefFont


def makeSrcGAFile(toolPaths, srcFontPath, srcGAPath):
	command = "%s -mtx \"%s\"  2>&1" % (toolPaths.tx, srcFontPath)
	report = FDKUtils.runShellCmd(command)
	if  ("fatal" in report) or ("error" in report):
		logMsg(report)
		logMsg("Error in using tx program to dump metrics with glyph names from  temporary font '%s'." % (srcFontPath))
		raise MergeFontError
	cidList = re.findall(r"glyph\[\d+\]\s+{([^,]+),", report)
	# Note that we omit the FontName and Language Group values from the header line;
	# the srcFontPath is already a CID font, with these values set correctly.
	lineList = filter(lambda cid: cid != "0", cidList)
	lineList = map(lambda cid: "%s\t%s" % (cid, cid), lineList)
	gaText = "mergeFonts" + os.linesep + os.linesep.join(lineList) + os.linesep
	gf = file(srcGAPath, "wb")
	gf.write(gaText)
	gf.close()
	
def prettyIndent(fixData):
	# indent lines in a dict, and add a blank line beforeand after a dict def.
	lines = re.findall("(.+)", fixData)
	indentLevel = 0
	numLines = len(lines)
	for i in range(numLines):
		isBegin = isEnd = 0
		line = lines[i]
		if re.search(r"^/.+dict.+begin", line):
			line = "   "*indentLevel + line
			indentLevel = indentLevel + 1
			line = os.linesep+line
		elif re.search(r"end.+def", line):
			indentLevel = indentLevel -1
			line = "   "*indentLevel + line
			line = line + os.linesep
		elif "begin" in line:
			line = "   "*indentLevel + line
			line = os.linesep + line + os.linesep
		else:
			line = "   "*indentLevel + line
		lines[i] = line
	newData = os.linesep.join(lines)
	return newData

def addNotDefMapping(gaPath):
	af = file(gaPath, "rb")
	data = af.read()
	af.close()
	af = file(gaPath, "wb")
	af.write(data)
	af.write("0\t.notdef" + os.linesep)
	af.close()
	
def getFontBBox(txPath, dstPath):
	command = "%s -mtx \"%s\"  2>&1" % (txPath, dstPath)
	report = FDKUtils.runShellCmd(command)
	if  ("fatal" in report) or ("error" in report):
		logMsg(report)
		logMsg("Error in using tx program to dump metrics with glyph names from  temporary font '%s'." % (dstPath))
		raise MergeFontError
	mtxList = re.findall(r"glyph.+{(-*\d+),(-*\d+),(-*\d+),(-*\d+)}}", report)
	kExtremeValue = 999999
	minX = kExtremeValue
	maxX = -kExtremeValue
	minY = kExtremeValue
	maxY = -kExtremeValue
	for entry in mtxList:
		val = eval(entry[0])
		if val < minX:
			minX = val
		val = eval(entry[1])
		if val < minY:
			minY = val
		val = eval(entry[2])
		if val > maxX:
			maxX = val
		val = eval(entry[3])
		if val > maxY:
			maxY = val
	return (minX, minY, maxX, maxY)

	
	# Note that we omit the FontName and Language Group values from the header line;
	# the srcFontPath is already a CID font, with these values set correctly.


def doFinalEdit(dstPath, fontinfo, fontBBox):
	fp = open(dstPath, "rb")
	data = fp.read()
	fp.close()
	# Limit the font we search to the first part up to the beginning of the FDArray.
	match = re.search(r"FDArray", data)
	if not match:
		logMsg("Error in editing cidfont dict: FDArray not found in  '%s'." % (dstPath))
		raise MergeFontError
	endSearch = match.end()

	fixData = data[:endSearch]

	# fix or add FamilyName
	match = re.search("FamilyName", fixData)
	if match:
		fixData = re.sub(r"FamilyName\s+\(.+?\)", "FamilyName (%s)" % (fontinfo["FamilyName"]), fixData)
	else:
		fixData  = re.sub(r"(/FullName.+?def.*?)([\r\n])", r"\1\2/FamilyName (%s) def\2" % (fontinfo["FamilyName"]), fixData)

	# fix or add FamilyName
	match = re.search("Weight", fixData)
	if match:
		fixData = re.sub(r"Weight\s+\(.+?\)", "Weight (%s)" % (fontinfo["Weight"]), fixData)
	else:
		fixData  = re.sub(r"(/FamilyName.+?def.*?)([\r\n])", r"\1\2/Weight (%s) def\2" % (fontinfo["Weight"]), fixData)

	# fix or add Notice:
	copyRightText = ("%s %s" % (fontinfo["AdobeCopyright"], fontinfo["Trademark"])).strip()
	match = re.search("Notice", fixData)
	if match:
		fixData = re.sub(r"Notice\s+\(.+?\)\s*(readonly)*\s*def", "Notice (%s) readonly def" % (copyRightText), fixData)
	else:
		fixData  = re.sub(r"(/FamilyName.+?def.*?)([\r\n])", r"/Notice (%s) readonly def\2\1\2" % (copyRightText), fixData)

	# fix or add fsType
	try:
		fsType = fontinfo["FSType"]
		match = re.search("FSType", fixData)
		if match:
				
			fixData = re.sub(r"FSType\s+\d+", "FSType %s" % (fsType), fixData)
		else:
			fixData  = re.sub(r"(Weight.+?def.*?)([\r\n])", r"\1\2/FSType %s def\2" % (fsType), fixData)
	except KeyError:
		pass

	# fix or add UnderlinePosition
	try:
		val = fontinfo["UnderlineThickness"]
		match = re.search("UnderlineThickness", fixData)
		if match:
				
			fixData = re.sub(r"UnderlineThickness\s+\d+", "UnderlineThickness %s" % (val), fixData)
		else:
			fixData  = re.sub(r"(Weight.+?def.*?)([\r\n])", r"\1\2/UnderlineThickness %s def\2" % (val), fixData)
	except KeyError:
		pass

	# fix or add UnderlinePosition
	try:
		val = fontinfo["UnderlinePosition"]
		match = re.search("UnderlinePosition", fixData)
		if match:
				
			fixData = re.sub(r"UnderlinePosition\s+\d+", "UnderlinePosition %s" % (val), fixData)
		else:
			fixData  = re.sub(r"(Weight.+?def.*?)([\r\n])", r"\1\2/UnderlinePosition %s def\2" % (val), fixData)
	except KeyError:
		pass

	# make /FontInfo be a readonly dict, and update the number of entries in the dict.
	fontInfoPat = re.compile(r"FontInfo\s\d+(\s.+?end)\s+def", re.DOTALL)
	fiString = fontInfoPat.search(fixData).group(1)
	numEntries = re.findall(r"\sdef\s", fiString)
	numEntries = len(numEntries) + 3
	substr = r"FontInfo %s\1 readonly def" % (numEntries)
	fixData = fontInfoPat.sub( substr, fixData, re.DOTALL)


	# fix or add XUID
	if fontinfo.has_key("XUID"):
		match = re.search("XUID", fixData)
		if match:
			fixData = re.sub(r"XUID\s+.+?def", "XUID  [%s] def" % (fontinfo["XUID"]), fixData)
		else:
			fixData = re.sub(r"(FontBBox.+?def.*?)([\r\n])", r"\1\2/XUID [%s] def\2" % (fontinfo["XUID"]), fixData)

	# Fix bounding box. The current is the largest of all the added FontBBoxes from the row fonts, which is not necessarily accurate.
	fixData = re.sub(r"(/FontBBox.+?def)", r"/FontBBox {%s %s %s %s} def" % fontBBox, fixData)
	re.sub(r"(CIDFontVersion\s+\d+)(\s)", "\1.000\2", fixData) # fix rounding of whole integers in version numbers.
	re.sub(r"(Version:\s*\d+)(\s)", "\1.000\2", fixData)
	fixData = prettyIndent(fixData)

	fp = open(dstPath, "wb")
	fp.write(fixData)
	fp.write(data[endSearch:])
	fp.close()

def run(args):
	# get paths to all necessary tools and files, and make sure they exist
	try:
		toolPaths = ToolPaths()
	except FDKEnvironmentError:
		return

	# parse the arg list, get default settings
	try:
		toolOptions = ToolOptions(args)
	except OptionParseError:
		return

	logMsg("Checking files..." + "   " + time.asctime())
	#Load the info from the cidfontinfo file
	try:
		fontinfo = getFontInfo(toolOptions.cidfontinfoPath)
	except (IOError, OSError):
		logMsg("Error: could not open and read cidfontinfo file: '%s'. Quitting." % (toolOptions.cidfontinfoPath))
		return
	except KeyError:
		return

	# get useful dicts from layout files
	try:
		getLayoutPaths(toolPaths, toolOptions, fontinfo)
		rowFontDict, cidDict, vertFontDict = getLayout(toolOptions)
	except IOError:
		return
	try:
		languageGroupDict, globalColorDict = getLanguageGroups(toolPaths, toolOptions, fontinfo)
	except IOError:
		return

	rowFontDirs = rowFontDict.keys()
	rowFontDirs.sort() 	# This sets the order in which the fonts are merged, and hence of the font dicts in the 
					# final output font.

	toolPaths.missingList = [] # If any row fonts needed for building the final font are missing, we complain and quit
	toolPaths.vertList = [] # The list of rotated fonts that do not not exist, and must be synthesized.

	# set output file path. This is typically "<R-O-S>/C1E0/cidfont.ps".
	if  toolOptions.outFilePath:
		outFilePath = toolOptions.outFilePath
	else:
		ROS = "-".join( [ fontinfo["Registry"], fontinfo["Ordering"], fontinfo["Supplement"] ])
		outFilePath = os.path.join(ROS, kOutputFileParentDir, kOutputFileName)
		dirName  = os.path.dirname(toolOptions.cidfontinfoPath)
		if dirName:
			outFilePath = os.path.join(dirName, outFilePath)
	 	toolOptions.outFilePath = outFilePath
	outputDir = os.path.dirname(outFilePath)
	if outputDir and not os.path.exists(outputDir):
		os.makedirs(outputDir)

	logMsg("Checking row fonts for vertically rotated fonts that need to be synthesized..." + "   " + time.asctime())
	for dirName in rowFontDirs:
		if vertFontDict and toolOptions.forceMakeRotated and vertFontDict.has_key(dirName):
			# User has asked that all rotated fonts be synthesized, even if this means
			# overwriting existing row fonts.
			toolPaths.vertList.append(dirName)
			continue
			
		foundPath = 0
		for fontName in kRowFontnames:
			fontPath = os.path.join(dirName, fontName)
			if  os.path.exists(fontPath):
				# If a font exists, we won't synthesize it.
				# save a backup copy.
				foundPath = 1
				shutil.copyfile(fontPath, fontPath + ".bak")
				break
		if foundPath:
			continue
			
		if vertFontDict and vertFontDict.has_key(dirName): 
			# It doesn't exist, but it is a rotated font, so we add it to the list to synthesize.
			toolPaths.vertList.append(dirName)
			fontPath =  os.path.join(dirName, kRowFontnames[0])
			logMsg("\tRow font '%s' will be synthesized." % (fontPath))
			continue

		toolPaths.missingList.append(dirName) # It doesn't exist, and we can't make it.
		continue

	if toolPaths.missingList:
		# All row fonts must be available for merging. Complain and quit.
		for dirName in toolPaths.missingList:
			fontPath = os.path.join(dirName, kRowFontnames[0])
			logMsg("\tMissing row font '%s'." % (fontPath))
		raise MissingFontError

	for dirName in toolPaths.vertList: # if is an empty list of vertFontDict is None
		# Need to synthesize these rotated fonts.
		fontPath = os.path.join(dirName, kRowFontnames[0])
		vertInfoPath = fontPath + ".rf.txt" # the info file used by the rotateFont program, to provide

		# Now we need to build the rotation info file. This has an entry for each glyph that should be copied
		# from the source to the rotated font.  Each entry contains:
		# glyph name, xoffset, y offset, new h advance.
		vertEntry = vertFontDict[dirName]
		for fontName in kRowFontnames:
			srcPath = os.path.join(vertEntry[0], fontName)
			if  os.path.exists(srcPath):
				break
		infoList = vertEntry[1].values()

		infoText =  map("\t".join, infoList)
		infoText = os.linesep.join(infoText) +  os.linesep
		if not os.path.exists(dirName):
			os.makedirs(dirName)
		fvi = file(vertInfoPath, "wt")
		fvi.write(infoText)
		fvi.close()

		logMsg("\tSynthesizing row font %s..." % (fontPath))
		# I don't provide useful x and y offset values, as these are overridden by the contents of the vertInfoPath file.
		command = "%s -t1 -rt 90 0 0 -rtf \"%s\" \"%s\"  \"%s\" 2>&1" % (toolPaths.rotateFont, vertInfoPath, srcPath, fontPath)
		report = None
		report = FDKUtils.runShellCmd(command)
		if report:
			print report
			if  "fatal" in report:
				continue

	if fontinfo.has_key(kHintDictParams):
		logMsg("Copying global hint info from hint dict source fonts to rest of the fonts under the hint dict..." + "   " + time.asctime())
		hintDictSource = fontinfo[kHintDictParams]
		hintDirDict = {}
		# build a dict where the keys are all the hint dirs which are named in hintDictSource, and
		# the value is the list of row font dirs under a htin dict. 
		for dirName in rowFontDirs:
			hintDir, fontDir = os.path.split(dirName)
			if not hintDictSource.has_key(hintDir):
				continue
			rowList =  hintDirDict.get(hintDir, [])
			rowList.append(dirName)
			hintDirDict[hintDir] = rowList
		# Now, for each of these hint dicts, use mergeFonts to make a new font with the
		# hint dict stuff copied.
		hintDirList = hintDirDict.keys()
		for hintDir in hintDirList:
			sourceDir = hintDictSource[hintDir]
			for fontName in kRowFontnames:
				sourcePath = os.path.join(dirName, fontName)
				if  os.path.exists(sourcePath):
					break
			fontList = hintDirDict[hintDir]
			for fontDir in fontList:
				if fontDir == sourceDir:
					continue
				for fontName in kRowFontnames:
					fontPath = os.path.join(dirName, fontName)
					if  os.path.exists(fontPath):
						break
				dstPath = fontPath + ".hint"
				gaCommand = "%s -std -hints \"%s\" \"%s\" \"%s\"  2>&1"  % (toolPaths.mergeFonts, dstPath, sourcePath, fontPath)
				report = FDKUtils.runShellCmd(gaCommand)
				if  ("fatal" in report) or ("error" in report):
					logMsg("Error in merge command when copying hint dict from  %s to %s." % (sourcePath, fontPath))
					logMsg(report)
					print gaCommand
					haveError = 1
					logMsg("Error in merge command for group %s." % (groupCount))
					raise MergeFontError
				af = file(fontPath, "rb")
				prefix = af.read(len(kACPrefix) + len(kGCPrefix) + 2)
				af.close()
				newprefix = None
				if kACPrefix in prefix:
					newprefix = kACPrefix
				if kGCPrefix in prefix:
					newprefix = kGCPrefix
				if newprefix:
					# add PS comment showing that the font has been hinted.
					af = file(dstPath, "rb")
					data = af.read()
					af.close()
					af = file(dstPath, "wb")
					af.write(newprefix)
					af.write(data)
					af.close()
				os.rename(dstPath, fontPath)
		
	logMsg("Checking row fonts for hinting..." + "   " + time.asctime())
	hintList = []
	for dirName in rowFontDirs:
		# I first check if the prefix strings kACPrefix or kGCPrefix are at the start of the file. If these
		# are present, the font has been hinted. Editing the font file with FontLab, or converting it with tx
		# will remove any such prefix.
		# if not , I then run tx -cff, dumping the output to /dev/null; this will output warnings
		# for each un-hinted glyph.  If there are such warnings, then add the font to the list of
		# fonts that need hinting.
		if toolOptions.neverHint:
			continue
			
		foundPath = 0
		for fontName in kRowFontnames:
			fontPath = os.path.join(dirName, fontName)
			if  os.path.exists(fontPath):
				foundPath = 1
				break
		if not foundPath:
			continue

		if  toolOptions.forceHint:
			hintList.append(dirName)
			continue

		af = file(fontPath, "rb")
		prefix = af.read(len(kACPrefix) + len(kGCPrefix) + 2)
		af.close()
		if (kACPrefix in prefix) or (kGCPrefix in prefix):
			# The prefix will not survive any editing program. Its presence shows that the font has been hinted by MakeCIDFont.
			continue
		command = "%s  -cff  \"%s\"  /dev/null 2>&1" % (toolPaths.tx, fontPath)
		report = FDKUtils.runShellCmd(command)
		if "unhinted" in report:
			logMsg("\tRow font '%s' needs hinting." % (fontPath))
			hintList.append(dirName)

	if hintList:
		logMsg("Hinting fonts.." + "   " + time.asctime())
	haveError = 0
	for dirName in hintList:
		# autohint modifies the font in place, saving the original as <font path> + ".bak"
		# Hint all the fonts that need it.
		for fontName in kRowFontnames:
			fontPath = os.path.join(dirName, fontName)
			if  os.path.exists(fontPath):
				break
		if toolOptions.noACReport:
			logMsg("\tHinting font %s..." % (fontPath)) 
		if toolOptions.noHintSubstitution:
			noHintSubstitution = " -ns "
		else:
			noHintSubstitution = ""

		command = "%s -a -nf -nb %s \"%s\"   2>&1" % (toolPaths.autohint, noHintSubstitution, fontPath)
		report = FDKUtils.runShellCmd(command)
		if report and not toolOptions.noACReport:
			logMsg( report)
		if  not "Done with font" in report[-200:]:
			haveError = 1
			logMsg("Error in hinting font '%s'." % (fontPath))
			continue
		# add PS comment showing that the font has been hinted.
		af = file(fontPath, "rb")
		data = af.read()
		af.close()
		af = file(fontPath, "wb")
		af.write(kACPrefix)
		af.write(data)
		af.close()
	if haveError:
		raise MergeFontError

	gcList = []
	if (not toolPaths.missingGC) and (not toolOptions.neverHint):
		logMsg("Checking row fonts for global coloring..." + "   " + time.asctime())
		# If a font file has the prefix string kGCPrefix, then it has already had global
		# coloring applied. Else, add it to the list for global coloring.
		# Note that addGlobalColor will not change a font file if it does in fact
		# already have global coloringl it will copy the data through unchanged.
		for dirName in rowFontDirs:
			foundPath = 0
			for fontName in kRowFontnames:
				fontPath = os.path.join(dirName, fontName)
				if  os.path.exists(fontPath):
					foundPath = 1
					break
			if not foundPath:
				continue
			if not globalColorDict.get(dirName, 0):
				continue
			gf = file(fontPath, "rb")
			prefix = gf.read( len(kGCPrefix) )
			gf.close()
			if kGCPrefix != prefix:
				logMsg("\tRow font '%s' needs global coloring." % (fontPath))
				gcList.append(dirName)
	if gcList:
		logMsg("Adding global coloring to fonts.." + "   " + time.asctime())
	for dirName in gcList:
		# Note that addGlobalColor will not in re-color a font that already has global coloring.;
		# it will just copy the font through without change.
		for fontName in kRowFontnames:
			fontPath = os.path.join(dirName, fontName)
			if  os.path.exists(fontPath):
				break
		tempPath = fontPath + ".gc"
		logMsg("\tColoring row font '%s'." % (fontPath))
		# I could use -t1 mode, but running it through CFF mode gets rid of duplicate hints and sorts them nicely.
		command = "%s  -cff  \"%s\"  \"%s\" 2>&1" % (toolPaths.addGlobalColor, fontPath, tempPath)
		report = FDKUtils.runShellCmd(command)
		report.strip()
		if  "fatal" in report:
			print report
			if os.path.exists(tempPath):
				os.remove(tempPath)
			continue
		report = re.sub(r"[^\r\n]+unused hints[^\r\n]+[\r\n]", "", report)
		if report:
			print report
		# convert back to ps
		if os.path.exists(tempPath):
			command = "%s -t1 \"%s\"  \"%s\" 2>&1" % (toolPaths.tx, tempPath, fontPath)
			report = FDKUtils.runShellCmd(command)
			report.strip()
			if report:
				print report
			if  "fatal" in report:
				if os.path.exists(tempPath):
					os.remove(tempPath)
				continue
		os.remove(tempPath)

		# add PS comment showing that the font has gc.
		af = file(fontPath, "rb")
		data = af.read()
		af.close()
		af = file(fontPath, "wb")
		af.write(kGCPrefix)
		af.write(data)
		af.close()

	# Run the merge tool. First. build the glyph alias files, then run the merge command.
	# Because of limitations in the length of the permissible command lines on the different
	# platforms, I have to merge the files in smaller groups. On Mac, the issue is
	# number of open files. I can get around this by using the 'ulimit -n' command, but on
	# Windows, I can't issue a command longer than about 10,000 chars. To be safe I merge
	# the fonts in groups of 100.
	logMsg("Merging source fonts.." + "   " + time.asctime())
	tempPath = os.path.dirname(toolOptions.outFilePath)
	tempPath = os.path.join(tempPath, kTempMergeFont)
	
	parentFontName = fontinfo["FontName"]
	gaCommandList = []
	haveError = 0
	notDefFont = None
	for dirName in rowFontDirs:
		foundPath = 0
		for fontName in kRowFontnames:
			fontPath = os.path.join(dirName, fontName)
			if  os.path.exists(fontPath):
				foundPath = 1
				break
		if not foundPath:
			continue
		rowDict = rowFontDict[dirName]

		gaCommandList, notDefFont = buildMergeCommand(fontPath, dirName, rowDict, parentFontName, languageGroupDict, gaCommandList,  notDefFont)

	# Now actually merge the files in groups of groupSize.  The output font
	# "dstPath" for one  group's merge command is used as the input font "srcPath"
	# for  the next group. For the first group  I just set srcPath to an empty
	# string.

	# A complication is that each output font must contain a notdef, but the only
	# one GA file will contain a mapping that will pass through CID 0. I deal with
	# this by checking , for each group, if CID 0 has been added. If not, then I
	# add a mapping for notdef to the last GA file of the group, and also make a
	# GA file for the srcPath file for the next group that will pass thorugh all
	# its glyphs except the notdef. Once the official notdef has been added,  I
	# just set "srcGAPAth" to am empty string, so that all the "srcPaths' glyphs
	# get merged into the group's output font file.
	tempList = []
	srcFontPath = "" # For the first group, this is just an empty string; for subsequent groups, it is the path to the previous group's output font file.
	srcGAPath = ""  # Used to filter the notdef out of the srcPath font file.  Never needed for the first group.
	groupCount = 0
	fontsInGroup = 50
	groupSize = fontsInGroup * 2
	addingNotDef = 0
	logMsg("Merging fonts in groups of  %s..." % (fontsInGroup) + "   " + time.asctime())
	while gaCommandList:
		logMsg("Merging group %s..." % (groupCount))
		dstPath = tempPath + str(groupCount)
		tempList.append(dstPath) # we'll need to delete this when all done.
		groupList = gaCommandList[:groupSize]
		if notDefFont in groupList:
			addingNotDef = 1
		else:
			addingNotDef = 0
		if (not addingNotDef) and (not srcFontPath):
			# On the first group, and when the first group does not contain the notdef font, we need to add  a notdef from some font. We do so
			# by adding the mapping to the GA file for the last font.
			addNotDefMapping(groupList[-2]) # need to add notdef mapping to last GA file, to pass through the notdef from this last font.
		if srcFontPath and addingNotDef:
			# If one or more groups have been merged so that the src font exists, and we are adding the group
			# with the notdef font, then we need to use a GA file with the CID font so as to filter out its notdef.
			srcGAPath = srcFontPath + ".ga.txt"
			makeSrcGAFile(toolPaths, srcFontPath, srcGAPath)
		 	tempList.append(srcGAPath)
		else:
			srcGAPath = ""
		if srcGAPath:
                    srcGAPath = "\"%s\"" % (srcGAPath)
		if srcFontPath:
                    srcFontPath = "\"%s\"" % (srcFontPath)
		gaCommand = "%s -std -cid \"%s\" \"%s\" %s  %s "  % (toolPaths.mergeFonts, toolOptions.cidfontinfoPath, dstPath, srcGAPath, srcFontPath)
		for name in groupList:
			gaCommand += " \"%s\"" % (name)
		gaCommand +=  " 2>&1"

		# now actually execute the merge command for this group.
		report = FDKUtils.runShellCmd(gaCommand)
		
		# If no error, check the report to make sure that we didn't see two row fonts from
		# under the same hint dict contribute different FDArray FontDicts. This means that
		# the two fonts have different global metrics or glboal hint values, which is a fatal error.
		if  ("fatal" in report) or ("error" in report):
			logMsg("Error in merge command for group %s." % (groupCount))
			logMsg(report)
			print gaCommand
			haveError = 1
			logMsg("Error in merge command for group %s." % (groupCount))
			raise MergeFontError
		else:
			# Look at list of source fonts that contributed a new fontDict to the output FDArray.
			# If two subsequent fonts come from under the same hint family directory, this is a fatal 
			# error.
			fdList = re.findall(r"dict \d+ from (\S+).", report)
			fdList = filter(lambda line: not kTempMergeFont in line, fdList) # remove the temp font entries - these are all fomr previous groups.
			if fdList:
				lastHintDir = None
				lastPath = None
				for path in fdList:
					dirList = path.split(os.sep)
					if lastHintDir and (dirList[0] == lastHintDir):
						logMsg("Error. Two subsequent row fonts under the same hint directory did not share the same global")
						logMsg("font metrics and hinting values, and had to be merged with different FDArray dicts. Please fix this.")
						logMsg("Current font: %s. Previous font: %s" % (path, lastPath))
						haveError = 1
					lastPath = path
					lastHintDir = dirList[0]

		# set up for next group..
		gaCommandList= gaCommandList[groupSize:]
		srcFontPath = dstPath
		groupCount +=1

	if haveError:
		raise IOError("Failed to merge fonts.")

	# Fix up the output cid font.
	fontBBox = getFontBBox(toolPaths.tx, dstPath)
	doFinalEdit(dstPath, fontinfo, fontBBox)

	# Copy the final group output file to the correct destination path,
        # and remove temp files
	shutil.copyfile(dstPath, toolOptions.outFilePath)
	for name in tempList:
		try:
			os.remove(name)
		except (IOError, OSError):
			pass
            

	logMsg("Wrote font file %s." % (os.path.abspath(toolOptions.outFilePath)))
	logMsg("All done." + "   " + time.asctime())

def MakeVertLayout(layoutPath):
	# makeCIDFont -makev <path to layout file>
	# Utility function to build a  VertLayout file from a layout file. 
	# Can be run in any directory; requires the path to the layout file as an argument.
	# Will write the VertLayout file to the same directory as the layout file, and with the
	# same base file name + ".VertLayout".
	#Assumes:
	# - all rotated fonts have a suffix "Rot"
	# - all glyph names in rotated fonts have the same name as in the source fonts.
	# collect the list of row fonts that end in "Rot"
	# FInd the matching row fonts without ROT
	# for each glyph name  in the ROT font, get the cid for that glyph in the Rot font, and in the src font
	# write src row dict, cid, rot cid, std xOffset, stdYOffset

	rowFontDict, cidDict, subsetDict = getRowFontDict(layoutPath, None)
	rowDirList = rowFontDict.keys()
	rotMatchString = "Rot" + os.sep
	rotDirList = filter(lambda name: rotMatchString in name, rowDirList)
	rotDirList.sort()
	rotDirList = map(lambda name: [name, re.sub(rotMatchString,  os.sep, name)], rotDirList)
	vertLayout = []
	for entry in rotDirList:
		rotRowDir = entry[0]
		srcRowDir = entry[1]
		srcDirList = srcRowDir.split(os.sep)
		rotFontDict = rowFontDict[rotRowDir]
		srcFontDict = rowFontDict[srcRowDir]
		rotNames = rotFontDict.keys()
		for rotName in rotNames:
			rotCID = rotFontDict[rotName]
			srcCID = srcFontDict[rotName]
			vertLayout.append("%s\t%s\t%s\t%s" % (srcCID, rotCID, 120, 880) )
	vertLayout.sort()
	vertPath = layoutPath + "." + kVertLayoutFileExtension
	vertText = os.linesep.join(vertLayout) + os.linesep
	print "Writing " + vertPath
	vf = open(vertPath, "wt")
	vf.write(vertText)
	vf.close()

def MakeLanguageGroup():
	"""
	makeCIDFont -makelg
	Function to build a LanguageGroup file. Must be run in the root directory for building a CID font,
	e.g in the same directory as the cidfontinfo file, and the final OTF font must be present.
	From the cidfontinfo file, it will get the paths to the layout and subset files. From these it will
	get the list of row fonts for the CID font. It will look at both row fonts to see if they have global coloring,
	and at the final OTF font to see which hint dicts have LanguageGroup set to 1.
	Note that the must include all the glyphs in the layout file - it cannot be a subset file.
	"""
	# parse the arg list, get default settings
	try:
		toolOptions = ToolOptions(sys.argv[1:])
	except OptionParseError:
		return

	if not os.path.exists(toolOptions.cidfontinfoPath):
		logMsg("Must run in current working directory where cidfontinfo file exists.")
		sys.exit(1)
	try:
		fontinfo = getFontInfo(toolOptions.cidfontinfoPath)
	except (IOError, OSError):
		logMsg("Error: could not open and read cidfontinfo file: '%s'. Quitting." % (toolOptions.cidfontinfoPath))
		return


	# get paths to all necessary tools and files, and make sure they exist
	try:
		toolPaths = ToolPaths()
	except FDKEnvironmentError:
		return

	# get the LanugageGroup settings from tthe OTF file.
	otfName =  fontinfo["FontName"] + ".otf"
	if not os.path.exists(otfName):
		logMsg("Quitting - need file %s." % (otfName))
	command = "%s -0  \"%s\"  2>&1" % ( toolPaths.tx, otfName)
	report = FDKUtils.runShellCmd(command)
	pat = re.compile(r"FontDict[^#]+FontName\s+\"(\S+)\"[^#]+## Private[^#]+LanguageGroup", re.DOTALL)
	lgList = pat.findall(report)
	lgList = map(lambda name: name.split("-")[-1], lgList)

	# get lists and dicts
	try:
		getLayoutPaths(toolPaths, toolOptions, fontinfo)
		rowFontDict, cidDict, vertFontDict = getLayout(toolOptions)
	except IOError:
		return

	gcFilePath = toolOptions.languageGroupPath
	layoutPath = toolOptions.layoutPath
 
	# get lists and dicts
	try:
		rowFontDict, cidDict, subsetDict = getRowFontDict(layoutPath, None)
	except IOError:
		return

	rowFontDirs = rowFontDict.keys()
	rowFontDirs.sort()
	globalList = ['# Hint directory name, Row font name,  LanguageGroup, needs Global Coloring']
	for dirName in rowFontDirs:
		foundPath = 0
		for fontName in kRowFontnames:
			fontPath = os.path.join(dirName, fontName)
			if  os.path.exists(fontPath):
				foundPath = 1
				break
		if  not foundPath:
			logMsg("Font %s  from layout file does not exist; will not be included in the language group file." % (fontPath))
			continue
		command = "%s -6 \"%s\"  2>&1" % ( toolPaths.tx, fontPath)
		report = FDKUtils.runShellCmd(command)
		if re.search(r"\s[vh]cntr\s", report):
			hasGlobalColor = 1
		else:
			hasGlobalColor = 0
		dirList = dirName.split(os.sep)

		langGroup = 0
		if (dirList[0] in lgList):
			langGroup = 1
		globalList.append("%s\t%s\t%s\t%s" % (dirList[0], dirList[1], langGroup, hasGlobalColor ))
	print "Writing file " + gcFilePath
	gcText = os.linesep.join(globalList) + os.linesep
	gcFile = file(gcFilePath, "wt")
	gcFile.write(gcText)
	gcFile.close()

if __name__=='__main__':
	if len(sys.argv) > 1:
		if "-makev"  == sys.argv[1]:
			# Otherwise undocumented option to build a VertLayout file. Can be run from any working directory, requres a path to the
			# source layout file. Must be run before -makelg
			MakeVertLayout(sys.argv[2])
			sys.exit(0)
		if "-makelg"  == sys.argv[1]:
			# Otherwise undocumented option to build a LanguageGroups file, using data from an existing font.
			# Must be run from the root directory for a CID font, at same level as cidfontifno file.
			# Note that the layout and VertLayout file must already exist in the locations implied by the cidfontinfo file values.
			# Also requires that the final <PS Name>.otf file exists, as well as the row fonts.
			MakeLanguageGroup()
			sys.exit(0)
	try:
		run(sys.argv[1:])
	except (LayoutParseError, MissingFontError, OptionParseError, MergeFontError, IOError):
		print "Quiting: there were errors in building the font."
		sys.exit(1)

