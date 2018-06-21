#!/public/bin/python

__copyright__ = """Copyright 2014 Adobe Systems Incorporated (http://www.adobe.com/). All Rights Reserved.
"""

__usage__ = """
ConvertUnscaledBez v1.9 Mar 6 2015
ConvertUnscaledBez -srcEM <number> [-new]  [-group] [-na] [-dstEM <number> ]
ConvertUnscaledBez [-u] -[h]
"""

__help__ = """
ConvertUnscaledBez -srcEM <number> [-new]  [-group] [-na] [-dstEM <number> ]

Options

-group With this option, the program will operate on all directories
below the current directory; without it, it will operate only on the
current directory, If you are using the option '-new', it is best to use
the option '-group' as well, as this will cause all the new fonts to
have the same hint dictionary.

-new   With this option, the program will look first for directories
with the name 'bez.unscaled'', and will build a new 'font.ps' file in
the parent directory of the 'bez.unscaled' directory. It will also
derive new global hint data from the sum of all the bez files, and will
write  this single set of global data to all the new 'font.ps' files.
Existing 'font.ps' files will get overwritten.

Without this option, the program will look first for existing "font.ps"
files, and then for directories with the name 'bez.unscaled' in the same
parent directory. It will assume that all the fonts have the same global
hint data, and will get the global hint data from the first 'font.ps'
file and will use this when hinting the new glyphs derived from the bez
data. It will then merge the bez data into the existing 'font.ps' file.

-srcEM <number> Required. This option specifies the em-square size of
the original bez files. Intelligent scaling is used to scale the bez
files to the em-square of the base font.

-dstEM <number> This option specifies the target em-square size. By
default, this is 1000, or the em-size of the final row font if it
already exists. If not specified, the default is 1000

-na	With this option, the program will not autohint the unscaled
glyph before scaling it to the target em-square size. Although scaling
works better for similar glyph outline features when hinted before
scaling, the hinting program does not always hint the same features of
similar glyphs the same way, and this causes the features to be
scaled with one unit position differences. For similar glyphs where this
is a problem, like the annotated glyphs, the hinting step before
scaling must be turned off.


Notes:
Calls the AC,  IS , and mergeFonts tools.

Some bez files will have the suffix ".uc" added when written by
BezierLab. This is because neither Mac nor Windows file systems can put
two files in the same directory that differ only by case of one or more
letters. This program will remove the suffix when adding the bez file to
the font.
"""

__methods__ = """
Overview:
0) If dstFont exists, extract font dict info.
 - use tx -0 to dump font dict; parse out values; scale to origEM.

1) Make temp font out of the bez files using arbitrary font dict values
based on the origEM.
- use template OTF font, and  BezTools.py to stuff bez files into temp
OTF. If have hint values, apply them. Save temp file

2) If not have hint values from dstFont, 
- apply Align, Stem Hist to all the temp fonts in the group, Collect the
data, use heuristics. - apply tx to get the font BBox for each temp font.
- open with FontTools, fix hint and font dict values.

3) Hint temp font

4) Intelligently scale each temp font using IS.

5) Merge font data into  final font.ps
- save dst Font to bak; delete orig
- use tx to convert temp font to Type1.
- use mergeFonts. GA file for dstFont should exclude all glyphs in the
temp font; GA file for temp font should include all glyphs, plus notdef.

"""
import sys
import os
import re
import time
import glob
import shutil
import BezTools
from fontTools.ttLib import TTFont, getTableModule, TTLibError
from fontTools.misc.psCharStrings import T2CharString
from fontTools.pens.boundsPen import BoundsPen
kDstFileName = "font.ps"
kWidthsFileName = "widths.unscaled"
kSrcBezDir = "bez.unscaled"
kUCSuffix = ".uc" # Must be kept in accordance with the suffix added by BezierLab.
kLenUC = len(kUCSuffix)
import FDKUtils

class TempFont:
	xmlData = """<?xml version="1.0" encoding="utf-8"?>
<ttFont sfntVersion="OTTO" >

  <GlyphOrder>
    <!-- The 'id' attribute is only for humans; it is ignored when parsed. -->
    <GlyphID id="0" name=".notdef"/>
    <GlyphID id="1" name="space"/>
  </GlyphOrder>

  <head>
    <!-- Most of this table will be recalculated by the compiler -->
    <tableVersion value="1.0"/>
    <fontRevision value="1.02899169922"/>
    <checkSumAdjustment value="0x291E4CCF"/>
    <magicNumber value="0x5F0F3CF5"/>
    <flags value="00000000 00000011"/>
    <unitsPerEm value="1000"/>
    <created value="Sun Jun  5 17:16:54 2005"/>
    <modified value="Fri Oct 14 15:50:04 2005"/>
    <xMin value="-166"/>
    <yMin value="-283"/>
    <xMax value="1021"/>
    <yMax value="927"/>
    <macStyle value="00000000 00000000"/>
    <lowestRecPPEM value="3"/>
    <fontDirectionHint value="2"/>
    <indexToLocFormat value="0"/>
    <glyphDataFormat value="0"/>
  </head>

  <hhea>
    <tableVersion value="1.0"/>
    <ascent value="726"/>
    <descent value="-274"/>
    <lineGap value="200"/>
    <advanceWidthMax value="1144"/>
    <minLeftSideBearing value="-166"/>
    <minRightSideBearing value="-170"/>
    <xMaxExtent value="1021"/>
    <caretSlopeRise value="1"/>
    <caretSlopeRun value="0"/>
    <caretOffset value="0"/>
    <reserved0 value="0"/>
    <reserved1 value="0"/>
    <reserved2 value="0"/>
    <reserved3 value="0"/>
    <metricDataFormat value="0"/>
    <numberOfHMetrics value="2"/>
  </hhea>

  <maxp>
    <tableVersion value="0x5000"/>
    <numGlyphs value="2"/>
  </maxp>

  <OS_2>
    <version value="2"/>
    <xAvgCharWidth value="532"/>
    <usWeightClass value="400"/>
    <usWidthClass value="5"/>
    <fsType value="00000000 00000100"/>
    <ySubscriptXSize value="650"/>
    <ySubscriptYSize value="600"/>
    <ySubscriptXOffset value="0"/>
    <ySubscriptYOffset value="75"/>
    <ySuperscriptXSize value="650"/>
    <ySuperscriptYSize value="600"/>
    <ySuperscriptXOffset value="0"/>
    <ySuperscriptYOffset value="350"/>
    <yStrikeoutSize value="50"/>
    <yStrikeoutPosition value="269"/>
    <sFamilyClass value="0"/>
    <panose>
      <bFamilyType value="2"/>
      <bSerifStyle value="4"/>
      <bWeight value="5"/>
      <bProportion value="2"/>
      <bContrast value="5"/>
      <bStrokeVariation value="5"/>
      <bArmStyle value="5"/>
      <bLetterForm value="3"/>
      <bMidline value="3"/>
      <bXHeight value="4"/>
    </panose>
    <ulUnicodeRange1 value="10000000 00000000 00000000 10101111"/>
    <ulUnicodeRange2 value="01010000 00000000 00100000 01001010"/>
    <ulUnicodeRange3 value="00000000 00000000 00000000 00000000"/>
    <ulUnicodeRange4 value="00000000 00000000 00000000 00000000"/>
    <achVendID value="ADBE"/>
    <fsSelection value="00000000 01000000"/>
    <fsFirstCharIndex value="32"/>
    <fsLastCharIndex value="64258"/>
    <sTypoAscender value="726"/>
    <sTypoDescender value="-274"/>
    <sTypoLineGap value="200"/>
    <usWinAscent value="927"/>
    <usWinDescent value="283"/>
    <ulCodePageRange1 value="00000000 00000000 00000000 00000001"/>
    <ulCodePageRange2 value="00000000 00000000 00000000 00000000"/>
    <sxHeight value="449"/>
    <sCapHeight value="689"/>
    <usDefaultChar value="32"/>
    <usBreakChar value="32"/>
    <usMaxContex value="4"/>
  </OS_2>

  <name>
    <namerecord nameID="0" platformID="1" platEncID="0" langID="0x0">
      Copyright &#169; 205 Adobe Systems Incorporated.  All Rights Reserved.
    </namerecord>
    <namerecord nameID="1" platformID="1" platEncID="0" langID="0x0">
      Temp Font
    </namerecord>
    <namerecord nameID="2" platformID="1" platEncID="0" langID="0x0">
      Regular
    </namerecord>
    <namerecord nameID="3" platformID="1" platEncID="0" langID="0x0">
      1.001;ADBE;TempFont-Regular
    </namerecord>
    <namerecord nameID="4" platformID="1" platEncID="0" langID="0x0">
      Temp Font Regular
    </namerecord>
    <namerecord nameID="5" platformID="1" platEncID="0" langID="0x0">
      Version 1.00
    </namerecord>
    <namerecord nameID="6" platformID="1" platEncID="0" langID="0x0">
      TempFont-Regular
    </namerecord>
    <namerecord nameID="0" platformID="3" platEncID="1" langID="0x409">
      Copyright &#169; 205 Adobe Systems Incorporated.  All Rights Reserved.
    </namerecord>
    <namerecord nameID="1" platformID="3" platEncID="1" langID="0x409">
      Temp Font
    </namerecord>
    <namerecord nameID="2" platformID="3" platEncID="1" langID="0x409">
      Regular
    </namerecord>
    <namerecord nameID="3" platformID="3" platEncID="1" langID="0x409">
      1.001;ADBE;TempFont-Regular
    </namerecord>
    <namerecord nameID="4" platformID="3" platEncID="1" langID="0x409">
      TempFont-Regular
    </namerecord>
    <namerecord nameID="5" platformID="3" platEncID="1" langID="0x409">
      Version 1.00
    </namerecord>
    <namerecord nameID="6" platformID="3" platEncID="1" langID="0x409">
      TempFont-Regular
    </namerecord>
  </name>

  <cmap>
    <tableVersion version="0"/>
    <cmap_format_4 platformID="0" platEncID="3" language="0">
      <map code="0x20" name="space"/><!-- SPACE -->
    </cmap_format_4>
    <cmap_format_6 platformID="1" platEncID="0" language="0">
      <map code="0x9" name="space"/>
    </cmap_format_6>
    <cmap_format_4 platformID="3" platEncID="1" language="0">
      <map code="0x20" name="space"/><!-- SPACE -->
    </cmap_format_4>
  </cmap>

  <post>
    <formatType value="3.0"/>
    <italicAngle value="0.0"/>
    <underlinePosition value="-75"/>
    <underlineThickness value="50"/>
    <isFixedPitch value="0"/>
    <minMemType42 value="0"/>
    <maxMemType42 value="0"/>
    <minMemType1 value="0"/>
    <maxMemType1 value="0"/>
  </post>

  <CFF>

    <CFFFont name="TempFont-Regular">
      <version value="001.001"/>
      <Notice value="Copyright 2005 Adobe Systems.  All Rights Reserved. This software is the property of Adobe Systems  Incorporated and its licensors, and may not be reproduced, used,   displayed, modified, disclosed or transferred without the express   written approval of Adobe. "/>
      <FullName value="Temp Font"/>
      <FamilyName value="TempFont"/>
      <Weight value="Regular"/>
      <isFixedPitch value="0"/>
      <ItalicAngle value="0"/>
      <UnderlineThickness value="50"/>
      <PaintType value="0"/>
      <CharstringType value="2"/>
      <FontMatrix value="0.001 0 0 0.001 0 0"/>
      <FontBBox value="-166 -283 1021 927"/>
      <StrokeWidth value="0"/>
      <!-- charset is dumped separately as the 'GlyphOrder' element -->
      <Encoding>
      </Encoding>
      <Private>
        <BlueValues value="-20 0 689 709 459 469 726 728"/>
        <BlueScale value="0.039625"/>
        <BlueShift value="7"/>
        <BlueFuzz value="1"/>
        <StdHW value="1"/>
        <StdVW value="1"/>
         <ForceBold value="0"/>
        <LanguageGroup value="0"/>
        <ExpansionFactor value="0.06"/>
        <initialRandomSeed value="0"/>
        <defaultWidthX value="0"/>
        <nominalWidthX value="0"/>
      </Private>
      <CharStrings>
        <CharString name=".notdef">
          0 50 600 50 hstem
          0 50 400 50 vstem
          0 vmoveto
          500 700 -500 hlineto
          250 -305 rmoveto
          -170 255 rlineto
          340 hlineto
          -140 -300 rmoveto
          170 255 rlineto
          -510 vlineto
          -370 -45 rmoveto
          170 255 170 -255 rlineto
          -370 555 rmoveto
          170 -255 -170 -255 rlineto
          endchar
        </CharString>
        <CharString name="space">
          1000 endchar
        </CharString>
      </CharStrings>
    </CFFFont>

    <GlobalSubrs>
      <!-- The 'index' attribute is only for humans; it is ignored when parsed. -->
    </GlobalSubrs>

  </CFF>

  <hmtx>
    <mtx name=".notdef" width="500" lsb="0"/>
    <mtx name="space" width="250" lsb="0"/>
  </hmtx>

</ttFont>
"""

class CBOptions:
	def __init__(self):
		self.doGroup = 0
		self.makeNewFonts = 0
		self.srcEM = None
		self.dstEM = 1000
		self.doPreScalingHinting = 1
		self.debug = 0

class FDKEnvironmentError(AttributeError):
	pass

class CBOptionParseError(KeyError):
	pass

class CBFontError(KeyError):
	pass

class CBError(KeyError):
	pass

def logMsg(*args):
	for s in args:
		print s

class SupressMsg:
	def write(self, *args):
		pass

def makeTempFont(fontPath, supressMsg):
	ttFont = None
	tempFont = TempFont()
	if os.path.exists(fontPath):
		os.remove(fontPath)
	ttxPath = fontPath+".ttx"
	try:
		xf = file(ttxPath, "wt")
		xf.write(tempFont.xmlData)
		xf.close()
	except(IOError, OSError), e:
		logMsg(e)
		logMsg("Failed to open temp file '%s': please check directory permissions." % (fontPath))
		raise CBError
	try:
		ttFont = TTFont()
		# supress fontTools messages:
		stdout = sys.stdout
		stderr = sys.stderr
		#sys.stdout =  supressMsg
		ttFont.importXML(ttxPath)
		sys.stdout = stdout
		sys.stderr = stderr
		ttFont.save(fontPath) # This is now actually an OTF font file
		ttFont.close()
	except:
		import traceback
		traceback.print_exc()
		if os.path.exists(fontPath):
			os.remove(fontPath)
		raise TTLibError("Could not make temp font")
	return

def getOptions():
	options = CBOptions()
	i = 1 # skip the program name.
	numOptions = len(sys.argv)
	try:
		while i < numOptions:
			arg = sys.argv[i]
	
			if arg == "-h":
				print __help__
				sys.exit(0)
			elif arg == "-u":
				print __help__
				sys.exit(0)
			elif arg == "-group":
				options.doGroup = 1
			elif arg == "-new":
				options.makeNewFonts = 1
			elif arg == "-srcEM":
				i += 1
				options.srcEM = eval(sys.argv[i])
			elif arg == "-dstEM":
				i += 1
				options.dstEM = eval(sys.argv[i])
			elif arg == "-d":
				options.debug = 1
			elif arg == "-na":
				options.doPreScalingHinting = 0
			else:
				logMsg("Option Error: unknown option : '%s' ." % (arg))
				raise CBOptionParseError
			i  += 1
	except IndexError:
		logMsg("Option Error: argument '%s' must be followed by a value." % (arg))
		raise CBOptionParseError

	if options.srcEM == None:
		logMsg("Option Error: You must specify the option '-srcEM <value>'.")
		raise CBOptionParseError

	return options

class FontEntry:
	def __init__(self, fontPath, localBezList):
		self.fontPath = fontPath
		self.bezDirs = localBezList
		self.widthsDict = None
		self.tempFontPath = None
		self.tempFontScaledPath = None
		self.tempFontSafeScaledPath = None
		self.ttFont = None
		self.mappingFilePath = None
		self.maxCoord = None
		
kDefaultGlobalBlueValues = [-250, -250, 1100, 1100]
class GlobalHints:
	def __init__(self):
		self.BlueValues = kDefaultGlobalBlueValues # For Kanji glyphs, this is the default. we do NOT want x-height.capheight control/overshoot supression.
		self.OtherBlues = None
		self.StdHW = None
		self.StdVW = None
		self.StemSnapH = None
		self.StemSnapV = None

class ToolPaths:
	def __init__(self):
		try:
			self.exe_dir, fdkSharedDataDir = FDKUtils.findFDKDirs()
		except FDKUtils.FDKEnvError:
			raise FDKEnvironmentError
	
		if not os.path.exists(self.exe_dir ):
			logMsg("The FDK executable dir \"%s\" does not exist." % (self.exe_dir))
			logMsg("Please re-instal. Quitting.")
			raise FDKEnvironmentError

		toolList = ["tx", "autoHint", "IS", "mergeFonts", "stemHist"]
		missingTools = []
		for name in toolList:
			toolPath = name
			exec("self.%s = toolPath" % (name))
			command = "%s -u 2>&1" % toolPath
			report = FDKUtils.runShellCmd(command)
			if ("-u" not in report) and ("options" not in report) and ("Option" not in report):
				print report
				print command, len(report), report
				missingTools.append(name)
		if missingTools:
			logMsg("Please re-install the FDK. The executable directory \"%s\" is missing the tools: < %s >." % (self.exe_dir, ", ". join(missingTools)))
			logMsg("or the files referenced by the shell scripts are missing.")
			raise FDKEnvironmentError

def buildFileList(options):
	""" Get the list of input bez directories and outptu font files.
	if -new option, then we look for 'bez.unscaled' directories, and expect to make a new font.ps file in the same parent directory.
	Else. we look for 'font.ps' files, and then look for 'bez.unscaled' directories in the samer parent directories.
	if -group, then we look for all matches in sub-directories of the current one, else we look in the current directory only.
	We may find two bez sub-directories in one font directory, as there is a separate bez dir for upper-case glyphs.
	"""
	bezDirList = []
	fontList = []
	fileList = []
	if options.makeNewFonts:
		# Make sure we can find the bez.unscaled directoriy
		#  We will look for matching bez.unscaled directoy and make new font.ps files.
		bez_pattern1 = "%s" % (kSrcBezDir)
		if options.doGroup:
			bez_pattern1 = "*/" + bez_pattern1
		bezDirList += glob.glob(bez_pattern1)
		if not bezDirList:
			logMsg("Did not find any directories  which match  '%s' '. Quitting." % (bez_pattern1))
			raise CBError
		bezDirList.sort()
		lastDir = ""
		localBezList = []
		fontPath = kDstFileName
		for bezdir in  bezDirList: 
			dir =  os.path.dirname(bezdir)
			if dir:
				if lastDir != dir:
					if lastDir:
						fileList.append( FontEntry(fontPath, localBezList) ) 
					fontPath = os.path.join(dir, kDstFileName)
					localBezList = []
					lastDir = dir
				localBezList.append(bezdir)
			else:
				localBezList.append(bezdir)
		fileList.append( FontEntry(fontPath, localBezList)  ) 
	else:
		# Make sure we can find some font files.
		#  We will then look for matching bez.unscaled directories, and merge these into the found fonts
		pattern = kDstFileName
		if options.doGroup:
			pattern = "*/" + pattern
		fontList = glob.glob(pattern)
		if not fontList:
			logMsg("Did not find any font files which match '%s' Quitting." % (pattern))
			raise CBError
		for fontPath in  fontList:
			localBezList = []
			fontDir = os.path.dirname(fontPath)
			bezPath1 = kSrcBezDir
			if fontDir:
				bezPath1 = os.path.join(fontDir, bezPath1)
				if os.path.exists(bezPath1):
					localBezList.append(bezPath1)
				if not localBezList:
					logMsg("Warning: did not find any bez.unscaled directories for the font file '%s'." % (os.path.abspath(fontPath)))
				else:
					fileList.append( FontEntry(fontPath, localBezList)  ) 

	# Now check for widths.ps files
	for entry in fileList:
		widthsPath = kWidthsFileName
		dirName = os.path.dirname( entry.fontPath)
		if dirName:
			widthsPath = os.path.join(dirName, widthsPath)
		if os.path.exists(widthsPath):
			wf =  open(widthsPath, "rt")
			data = wf.read()
			wf.close()
			list = re.findall(r"(\S+)\s+(-*\d+)", data)
			widthsDict = {}
			for item in list:
				name = item[0][1:] # get rid of initial back-slash
				width = item[1]
				widthsDict[name] = eval(width) # remember: this is keyed by the bez file name, which may differ by the kUCSuffix from the
										# the final glyph name.
			entry.widthsDict = widthsDict
	return fileList

def mergeBezFiles(bezDirs, widthsDict, fontPath, srcEM, dstEM):
	""" 
	First, fix the ttFont's em-box, and put in useless but hopefully safe alignment zone values.
	Then, for each bez file, convert it to a T2 string, and add it to the font.
	"""
	# Collect list of bez files
	ttFont = TTFont(fontPath)
	bezFileList = []
	dirPath =  os.path.abspath(os.path.dirname(bezDirs[0]))
	logMsg("\tReading glyphs from '%s' in '%s'..." % (bezDirs, dirPath))
	if not widthsDict:
		logMsg("\tCould not find widths file '%s'; all widths will be set to '%s'." % (kWidthsFileName, srcEM))
	for bezDir in bezDirs:
		list = os.listdir(bezDir)
		bezFileList += map(lambda name: os.path.join(bezDir, name), list)
	if not bezFileList:
		logMsg("Error. No bez files were found in '%s'. " % (bezDirs))

	# Merge the bez files.
	glyphList  = ttFont.getGlyphOrder() #force loading of charstring index table
	ttFont.getGlyphID(glyphList[-1])
	cffTable =  ttFont['CFF ']
	pTopDict = cffTable.cff.topDictIndex[0]
	
	invEM = 1.0/srcEM
	scaleFactor = srcEM/dstEM
	pTopDict.FontMatrix = [invEM, 0, 0, invEM, 0, 0];
	pTopDict.rawDict["FontMatrix"] = pTopDict.FontMatrix
	
	pChar = pTopDict.CharStrings
	pCharIndex = pChar.charStringsIndex
	pHmtx = ttFont['hmtx']

	for path in bezFileList:
		glyphName = os.path.basename(path)
		if (glyphName[0] == ".") and (glyphName !=" .notdef"):
			continue
		if glyphName[0]  < 32:
			continue
		# Check if glyph name has kUCSuffix. If so, we need to remove it
		# when inserting this glyph into the font. The suffix is added by BezierLab
		# to avoid conflict between UC/lc file names, which neither Mac nor Win can handle.
		finalName = glyphName
		if finalName[-kLenUC:] == kUCSuffix:
			finalName = finalName[:kLenUC]
		width = srcEM
		if widthsDict:
			try:
				width = widthsDict[glyphName] # widthsDict is keyed by bez file name, not finalName
			except KeyError:
				logMsg("Warning: bez file name %s not found in the widths.unscaled file: assigning default width.", glyphName)
		pHmtx.metrics[finalName] = [width,  0] # assign arbitrary LSB of 0
		bf = open(path, 'rb')
		bezData = bf.read()
		bf.close()
		if BezTools.needsDecryption(bezData):
			bezData = BezTools.bezDecrypt(bezData)
		t2Program = [width] + BezTools.convertBezToT2(bezData)
		newCharstring = T2CharString(program = t2Program)
		nameExists = pChar.has_key(finalName)
		# Note that since the ttFont was read from XML, its properties are somewhat different than
		# when decompiled from an OTF font file: topDict.charset is None, and the charstrings are not indexed.
		if nameExists:
			gid = pChar.charStrings[finalName]
			pCharIndex.items[gid] = newCharstring
		else:
			# update CFF
			pCharIndex.append(newCharstring)
			gid = len(pTopDict.charset)
			pChar.charStrings[finalName] = gid # haven't appended the name to charset yet.
			pTopDict.charset.append(finalName)

	# Now update the font's BBox.
	for key in ttFont.keys():
            table = ttFont[key]
	ttFont.save(fontPath) # Compile charstrings, so that charstrings array is all up to date.
	ttFont.close()

	ttFont = TTFont(fontPath)
	cffTable =  ttFont['CFF ']
	pTopDict = cffTable.cff.topDictIndex[0]
	bbox = [srcEM, srcEM, -srcEM, -srcEM ]
	glyphSet = ttFont.getGlyphSet()
	pen = BoundsPen(glyphSet)
	for glyphName in glyphSet.keys():
		glyph = glyphSet[glyphName]
		glyph.draw(pen)
		if  pen.bounds:
			x0, y0, x1,y1 = pen.bounds
			if x0 < bbox[0]:
				bbox[0] = x0
			if y0 < bbox[1]:
				bbox[1] = y0
			if x1 > bbox[2]:
				bbox[2] = x1
			if y1 > bbox[3]:
				bbox[3] = y1
	pTopDict.FontBBox = bbox
	pTopDict.rawDict["FontBBox"] = bbox
	for key in ttFont.keys():
            table = ttFont[key]

	if not hasattr(pTopDict, "UnderlineThickness"):
		pTopDict.UnderlineThickness = 50
	pTopDict.UnderlineThickness = pTopDict.UnderlineThickness*scaleFactor
	pTopDict.rawDict["UnderlineThickness"] = pTopDict.UnderlineThickness
	if not hasattr(pTopDict, "UnderlinePosition"):
		pTopDict.UnderlinePosition = -100
	pTopDict.UnderlinePosition = pTopDict.UnderlinePosition*scaleFactor
	pTopDict.rawDict["UnderlinePosition"] = pTopDict.UnderlinePosition


	ttFont.save(fontPath)
 	ttFont.close()
 	maxCoord = max( map(abs, bbox) )
	return maxCoord

def getHintData(reportPath, dict):
	try:
		hf = file(reportPath, "rt")
		data = hf.read()
		hf.close()
		hintList = re.findall(r"(\d+)\s+(-*\d+)\s+\[[^]\r\n]+\]", data)
		for entry in hintList:
			dict[ eval(entry[1]) ] = eval(entry[0])
	except (IOError, OSError), e:
		logMsg("Failed to open hint report '%s'. msg: <%s>." % (reportPath, e))
	return

def cmpWidth(first, last):
	first = first[2]
	last = last[2]
	return cmp(first,last)
	
def getBestValues(stemDict, ptSizeRange, srcResolution, dstResolution):
	"""
	For each of a range of point sizes, a hint will cover +- a delta, which may include other hints.
		I want to  construct an optimal StemW hint by finding the hint which covers the largest hint count, for all
		the point sizes of intterest
		I keep the current count total in countDict[stemWdith] = currrentCount. I initially set all the values to 0.
		for each point size
			calculate the delta
			for each stem width
				add up all the counts for all the stem widths which are within +/-  delta of the stem width;
				add this to the  countDict[stemWdith]  value.
	Normalize the count values by the number of pt size we tried
	Pick the stem width the maximum count value.
	Pick all the stems with a count greater than 1 for the StemSnap array, up to a max of 12, that do not overlap with the
	main stem width
	"""
	countDict = {}
	widthList = stemDict.keys()
	for width in widthList:
		countDict[width] = 0

	maxDelta = 0
	for ptSize in ptSizeRange:
		delta =  (0.35*72*srcResolution)/(ptSize*dstResolution)
		if maxDelta < delta:
			maxDelta = delta
		for width in widthList:
			top =  int(round(width+delta))
			bottom = int(round(width-delta))
			if bottom == top:
				top +=1
			for i in range(bottom, top):
				if stemDict.has_key(i):
					countDict[width] = countDict[width] + stemDict[i]
	countList = countDict.items()			
	countList = map(lambda entry: [entry[1], stemDict[ entry[0]], entry[0]], countList)
	countList.sort()
	countList.reverse()
	# This is so  that it will sort in order by
	#	entry[0] =  total count for width, i.e. the sum of all the counts of the widths that it overlaps +/- the delta
	#	etnry[1] = the original count for the width
	#	entry[2] = the width
	bestStem = countList[0][2]
	bestStemList = [bestStem]
	numPtSizes = len(ptSizeRange)
	tempList = [countList[0]]
	for entry in countList[1:]:
		if not entry[0] > numPtSizes:
			break # Weed out any stem width that was represented only once in one glyph
		tempList.append(entry)
	# Now we need to weed out the entries that overlap
	#Sort by ascending width, and then save each succesive width only if does nto overlap with the last saved width.
	countList = tempList
	if len(tempList) > 1:
		tempList = [countList[0]] # save the most popular width
		countList = countList[1:] # remove it from the list
		countList.sort(cmpWidth)
		# Some of these may overlap  with the tolerance of +/- maxDelta. Weed out the ones that overlap
		lastWidth = countList[0][2]
		for entry in countList:
			width = entry[2]
			if ((float(width)*dstResolution)/srcResolution) < 1: # don't copy over any values that will be less than 1 in the final font.
				continue
			if width >  (lastWidth + maxDelta):
				tempList.append(entry)
				lastWidth = width
	tempList.sort() # sort them in order of decreasing popularity again.
	tempList.reverse()
	bestStemList = tempList[:12] # Allow a max of 12 StemSnap values
	bestStemList = map(lambda entry: entry[2], bestStemList)
	bestStemList.sort()
	return bestStem, bestStemList

def getNewHintInfo(toolPaths, options, fileList, useScaledFiles, ptSizeRange, srcResolution, dstResolutiion):
	"""
	This is being called to collect new hint info from one or more fonts. From
	each temp font in turn, we collect the stem info,tracking the total count
	for each stem or zone., and extract the best stem width and StemSnap list.
	"""
	globalHints = GlobalHints()
	hStemDict = {}
	vStemDict= {}
	maxY = srcResolution
	minY = 0
	extensionList = [ ".hstem.txt", ".vstem.txt"]
	for fontEntry in fileList:

		if useScaledFiles:
			path = fontEntry.tempFontScaledPath
		else:
			path = fontEntry.tempFontPath
		print "\tDeriving new hints from temp font: ", path

		hstemPath = path+".hstm.txt"
		vstemPath = path+".vstm.txt"
		if os.path.exists(hstemPath):
			os.remove(hstemPath)
		if os.path.exists(vstemPath):
			os.remove(vstemPath)

		command = "%s  \"%s\" 2>&1" % ( toolPaths.stemHist, path)
		report = FDKUtils.runShellCmd(command)
		print report
		getHintData(hstemPath,  hStemDict)
		getHintData(vstemPath,  vStemDict)
	
		if not options.debug:
			if os.path.exists(hstemPath):
				os.remove(hstemPath)
			if os.path.exists(vstemPath):
				os.remove(vstemPath)

		command = "%s -mtx \"%s\" 2>&1" % ( toolPaths.tx, path)
		report = FDKUtils.runShellCmd(command)
		yList = re.findall(r"glyph.+{(?:-*\d+),(-*\d+),(?:-*\d+),(-*\d+)}}", report)
		my = min(map(lambda entry: eval(entry[0]), yList))
		minY = min(my, minY)
		my = max(map(lambda entry: eval(entry[1]), yList))
		maxY = max(my, maxY)
		
		
	if hStemDict:
		globalHints.StdHW, globalHints.StemSnapH = getBestValues(hStemDict, ptSizeRange, srcResolution, dstResolutiion)
	if vStemDict:
		globalHints.StdVW, globalHints.StemSnapV = getBestValues(vStemDict, ptSizeRange, srcResolution, dstResolutiion)
		# Fix the default BlueValues. We want to set this outside of the max and min Y values.
	minY -= srcResolution*0.2
	maxY += srcResolution*0.2
	globalHints.BlueValues = [minY, minY, maxY, maxY]		
				

	return globalHints

def getOldHintInfo(toolPaths, options, fileList):
	globalHints = GlobalHints()
	srcEM = float(options.srcEM)
	dstEM = float(options.dstEM)
	seenFont = 0

	for entry in fileList:
		fontPath = entry.fontPath
		if os.path.exists(fontPath):
			command = "%s -0 \"%s\"  2>&1" % ( toolPaths.tx, fontPath)
			report = FDKUtils.runShellCmd(command)
			match = re.search(r"BlueValues\s+\{(.+?)\}", report)
			if match:
				globalHints.BlueValues = eval( "[" + match.group(1) + "]")
				globalHints.BlueValues  = map(lambda val: int(val*srcEM/dstEM), globalHints.BlueValues)
			else:
				logMsg("Error. The row font '%s' did not have a BlueValues entry in its font dict." % (fontPath))
				raise CBError

			match = re.search(r"OtherBlues\s+\{(.+?)\}", report)
			if match:
				globalHints.OtherBlues = eval( "[" + match.group(1) + "]")
				globalHints.OtherBlues  = map(lambda val: int(val*srcEM/dstEM), globalHints.OtherBlues)

			match = re.search(r"StdHW\s+(\d+)", report)
			if match:
				globalHints.StdHW = int(eval(match.group(1)) * srcEM/dstEM)

			match = re.search(r"StdVW\s+(\d+)", report)
			if match:
				globalHints.StdVW =  int(eval(match.group(1)) * srcEM/dstEM)

			match = re.search(r"StemSnapH\s+\{(.+?)\}", report)
			if match:
				globalHints.StemSnapH = eval( "[" + match.group(1) + "]")
				globalHints.StemSnapH  = map(lambda val: int(val*srcEM/dstEM), globalHints.StemSnapH)

			match = re.search(r"StemSnapV\s+\{(.+?)\}", report)
			if match:
				globalHints.StemSnapV = eval( "[" + match.group(1) + "]")
				globalHints.StemSnapV  = map(lambda val: int(val*srcEM/dstEM), globalHints.StemSnapV)
				

			seenFont = 1
			logMsg("\tTaking global hint metrics from font %s."  % (os.path.abspath(fontPath)))
			#fields = dir(globalHints)
			#fields = filter(lambda name: name[0] != "_", fields)
			#for name in fields:
			#	print "\t%s: %s" % (name, eval("globalHints.%s" % name))
			break

	if not seenFont:
		logMsg("Could not find existing row font from which to take hint values.")
		raise CBError

	return globalHints

def openFileAsTTFont(path, txPath):
	# If input font is  CFF or PS, build a dummy ttFont in memory for use by AC.
	# return ttFont, and flag if is a real OTF font Return flag is 0 if OTF, 1 if CFF, and 2 if PS/
	fontType  = 0 # OTF
	tempPath = os.path.dirname(path)
	tempPathBase  = os.path.join(tempPath, "temp.autoHint")
	tempPathCFF = tempPathBase + ".cff"
	try:
		ff = file(path, "rb")
		data = ff.read(10)
		ff.close()
	except (IOError, OSError):
		logMsg("Failed to open and read font file %s." % path)

	if data[:4] == "OTTO": # it is an OTF font, can process file directly
		try:
			ttFont = TTFont(path)
		except (IOError, OSError):
			raise ACFontError("Error opening or reading from font file <%s>." % path)
		except TTLibError:
			raise ACFontError("Error parsing font file <%s>." % path)

		try:
			cffTable = ttFont["CFF "]
		except KeyError:
			raise ACFontError("Error: font is not a CFF font <%s>." % fontFileName)

		return ttFont, fontType

	# It is not an OTF file.
	if (data[0] == '\1') and (data[1] == '\0'): # CFF file
		fontType = 1
		tempPathCFF = path
	elif not "%" in data:
		#not a PS file either
		logMsg("Font file must be a PS, CFF or OTF  fontfile: %s." % path)
		raise ACFontError("Font file must be PS, CFF or OTF file: %s." % path)

	else:  # It is a PS file. Convert to CFF.	
		fontType =  2
		command="%s   -cff -b \"%s\" \"%s\" 2>&1" % (txPath, path, tempPathCFF)
		report = FDKUtils.runShellCmd(command)
		if "fatal" in report:
			logMsg("Attempted to convert font %s  from PS to a temporary CFF data file." % path)
			logMsg(report)
			raise ACFontError("Failed to convert PS font %s to a temp CFF font." % path)

	# now package the CFF font as an OTF font for use by AC.
	ff = file(tempPathCFF, "rb")
	data = ff.read()
	ff.close()
	try:
		ttFont = TTFont()
		cffModule = getTableModule('CFF ')
		cffTable = cffModule.table_C_F_F_('CFF ')
		ttFont['CFF '] = cffTable
		cffTable.decompile(data, ttFont)
	except:
		import traceback
		traceback.print_exc()
		logMsg("Attempted to read font %s  as CFF." % path)
		raise ACFontError("Error parsing font file <%s>." % fontFileName)
	return ttFont, fontType

def saveFileFromTTFont(ttFont, inputPath, outputPath, fontType, txPath):
	overwriteOriginal = 0
	if inputPath == outputPath:
		overwriteOriginal = 1
	tempPath = os.path.dirname(inputPath)
	tempPath = os.path.join(tempPath, "temp.autoHint")

	if fontType == 0: # OTF
		if overwriteOriginal:
			ttFont.save(tempPath)
			shutil.copyfile(tempPath, inputPath)
		else:
			ttFont.save(outputPath)
		ttFont.close()

	else:		
		data = ttFont["CFF "].compile(ttFont)
		if fontType == 1: # CFF
			if overwriteOriginal:
				tf = file(tempPath, "wb")
				tf.write(data)
				tf.close()
				shutil.copyfile(tempPath, inputPath)
			else:
				tf = file(outputPath, "wb")
				tf.write(data)
				tf.close()

		elif  fontType == 2: # PS.
			tf = file(tempPath, "wb")
			tf.write(data)
			tf.close()
			if overwriteOriginal:
				command="%s  -t1 \"%s\" \"%s\" 2>&1" % (txPath, tempPath, inputPath)
			else:
				command="%s  -t1 \"%s\" \"%s\" 2>&1" % (txPath, tempPath, outputPath)
			report = FDKUtils.runShellCmd(command)
			logMsg(report)
			if "fatal" in report:
				raise IOError("Failed to convert hinted font temp file with tx %s" % tempPath)
			if overwriteOriginal:
				os.remove(tempPath)
			# remove temp file left over from openFile.
			os.remove(tempPath + ".cff")

def addHints(globalHints, fontPath, txPath):
	ttFont, fontType = openFileAsTTFont(fontPath, txPath)
	privateDict = ttFont['CFF '].cff.topDictIndex[0].Private
	fields = dir(globalHints)
	fields = filter(lambda name: name[0] != "_", fields)
	for name in fields:
		val =  eval("globalHints.%s" % name)
		if val != None:
			exec("privateDict.%s = val" % (name))
			print name,val, eval("privateDict.%s" % (name))
		elif eval("hasattr(privateDict, \"%s\")" % name):
			exec("del privateDict.%s" % name)
	saveFileFromTTFont( ttFont, fontPath, fontPath, fontType, txPath)
	return 

def hintFont(toolPaths, fontPath):
	logMsg("\tHinting font %s..." % (fontPath)) 
	command = "%s -a  -nf -o %s.hinted %s 2>&1" % (toolPaths.autoHint, fontPath, fontPath)
	report = FDKUtils.runShellCmd(command)
	if  not "Done with font" in report[-200:]:
		logMsg(report)
		logMsg("Error  hinting temp font '%s'." % fontPath)
		raise CBError
	return 

def scaleFont(toolPaths,  tempFontPath, tempFontScaledPath, tempFontSafeScaledPath, srcEm, dstEM, maxCoord):
	logMsg("\tScaling font %s..." % (tempFontPath))
	
	kBuildCharLimit = 16000-1 # This value needs to be the same as used in the buildChar:t1interp.c FDK_CS_MAX and MIN limit.
	# as used by IS via the buildchar library.
	# if maxCoord > kBuildCharLimit, then the buildChar library in IS will clamp it. We then need to scale it 
	# so that the max coord is less then kBuildCharLimit.
	if  (kBuildCharLimit < maxCoord): # This value
		logMsg("Warning: Font contained a coordinate value '%s'. This exceeds the max value '%s' that IS can handle, so I am scaling it down first before running IS on font '%s'." % (maxCoord, kBuildCharLimit, tempFontPath))
		safeScale = 6096.0/maxCoord
		if safeScale >= 0.5: # Better for rounding to scale by 1/2 or 1/4.
			safeScale = 0.5
		elif safeScale > 0.25:
			safeScale = 0.25
			
		safeEm = srcEm*safeScale
		command = "rotateFont -t1 -matrix %s 0 0 %s 0 0 -fm  \"%s\" \"%s\" 2>&1" % (safeScale, safeScale, tempFontPath,  tempFontSafeScaledPath)
		report = FDKUtils.runShellCmd(command)
		print report
		if  ("fatal" in report) or ("error" in report):
			logMsg(report)
			logMsg("Error  scaling temp font '%s'." % tempFontPath)
			raise CBError
		tempFontPath = tempFontSafeScaledPath
	else:
		safeEm = srcEm

	command = "%s -t1 -z2 -z  %s  \"%s\" \"%s\" 2>&1" % (toolPaths.IS, dstEM, tempFontPath,  tempFontScaledPath)
	report = FDKUtils.runShellCmd(command)
	print report
	if  ("fatal" in report) or ("error" in report):
		logMsg(report)
		logMsg("Error  scaling temp font '%s'." % tempFontPath)
		raise CBError
	return safeEm


def makeMergeGAFile(fontPath, toolPaths, bezFontPath):
	gaPath = fontPath + ".ga.txt"
	gaBezPath = bezFontPath + ".ga.txt"
	command = "%s -mtx \"%s\"  2>&1" % (toolPaths.tx, fontPath)
	report = FDKUtils.runShellCmd(command)
	if  ("fatal" in report) or ("error" in report):
		logMsg(report)
		logMsg("Error in using tx program to extract glyph names from  font '%s'." % (fontPath))
		raise MergeFontError
	fontNameList = re.findall(r"glyph\[\d+\]\s+{([^,]+),", report)

	command = "%s -mtx \"%s\"  2>&1" % (toolPaths.tx, bezFontPath)
	report = FDKUtils.runShellCmd(command)
	if  ("fatal" in report) or ("error" in report):
		logMsg(report)
		logMsg("Error in using tx program to extract glyph names from  font '%s'." % (bezFontPath))
		raise MergeFontError
	bezNameList = re.findall(r"glyph\[\d+\]\s+{([^,]+),", report)
	bezNameList = filter(lambda name: name != ".notdef", bezNameList)
	# Don't use the .notdef from the bez temp file; this ensures that the fontNameList will
	# have at least one glyph name - .notdef.
	fontNameList = filter(lambda name: not name in bezNameList, fontNameList)

	# Note that we omit the FontName and Language Group values from the header line;
	# the srcFontPath is a name-keyed font.
	lineList = map(lambda name: "%s\t%s" % (name,name), fontNameList)
	gaText = "mergeFonts" + os.linesep + os.linesep.join(lineList) + os.linesep
	gf = file(gaPath, "wb")
	gf.write(gaText)
	gf.close()

	lineList = map(lambda name: "%s\t%s" % (name,name), bezNameList)
	gaText = "mergeFonts" + os.linesep + os.linesep.join(lineList) + os.linesep
	gf = file(gaBezPath, "wb")
	gf.write(gaText)
	gf.close()
	
	return gaPath,gaBezPath

def mergeTempFont(toolPaths, makeNewFonts, fontEntry):
	logMsg("\tMerging temp font %s into %s..." % (fontEntry.tempFontScaledPath, fontEntry.fontPath))

	if makeNewFonts:
		tempFont = fontEntry.tempFontScaledPath
	else:
		tempFont = fontEntry.tempFontPath
		# merge scaled temp font into existing font.
		# We need to filter out from the existing font all the glyph names
		# that conflict with the new bez glyphs, as well as the .notdef.
		# For merging files, all input files must be of the same type.
		gaPath, gaBezPath = makeMergeGAFile(fontEntry.fontPath, toolPaths, fontEntry.tempFontScaledPath)
		command = "%s  \"%s\" \"%s\" \"%s\" \"%s\" \"%s\" 2>&1" % (toolPaths.mergeFonts, tempFont,
                                                    gaPath, fontEntry.fontPath,  gaBezPath, fontEntry.tempFontScaledPath)
		report = FDKUtils.runShellCmd(command)
		print report
		if  ("fatal" in report) or  ("error" in report):
			logMsg(report)
			logMsg("Error  merging  temp font '%s' into final font '%s'." %  (fontEntry.tempFontScaledPath, fontEntry.fontPath))
			raise CBError
		if not options.debug:
                    os.remove(gaPath)
                    os.remove(gaBezPath)
	# copy temp font to final output.
	command = "%s  -t1 \"%s\" \"%s\" 2>&1" % (toolPaths.tx,  tempFont,  fontEntry.fontPath)
	report = FDKUtils.runShellCmd(command)
	print report
	if  ("fatal" in report) or ("error" in report):
		logMsg(report)
		logMsg("Error  merging  temp font '%s' into final font '%s'." %  fontEntry.tempFontScaledPath, fontEntry.fontPath)
		raise CBError
	if not os.path.exists(fontEntry.fontPath):
		print "Error making final font: ", fontEntry.fontPath, report

	return 

def run():
	try:
		options = getOptions()
		paths = ToolPaths()

		# Get the list of input bez directories and output font files.
		fileList = buildFileList(options)

		srcResolution = options.srcEM
		dstResolution = options.dstEM

		# Build temp OTF fonts to hold the bez file data
		supressMsg = SupressMsg()
		logMsg(os.linesep + "Building unscaled temporary fonts..." + time.asctime())
		for fontEntry in fileList:
			fontEntry.tempFontPath = fontEntry.fontPath + ".tmp.otf"
			makeTempFont(fontEntry.tempFontPath, supressMsg)
			fontEntry.maxCoord = mergeBezFiles(fontEntry.bezDirs, fontEntry.widthsDict, fontEntry.tempFontPath, srcResolution, dstResolution)
			logMsg("\tSaved temp font file '%s'..." % (fontEntry.tempFontPath))

		# Add global hint info
		if options.makeNewFonts:
			# If we are making new fonts, use StemHist to get aligment and stem
			# zones from all the new glyphs form all the new fonts , and build new
			# global hints.
			logMsg("Analyzing glyphs to derive global hinting metrics  for intelligent scaling...")
			ptSizeRange = [72]
			useScaledFiles = 0
			globalHints = getNewHintInfo(paths, options,  fileList, useScaledFiles, ptSizeRange, srcResolution, dstResolution)
		else:
			# Get the hint list from the first existing font we find.
			globalHints = getOldHintInfo(paths, options, fileList)
		
		logMsg("Updating unscaled temp fonts with global hint data...")
		for fontEntry in fileList:
			addHints(globalHints, fontEntry.tempFontPath, paths.tx)

		# Hint the font with ACs, and use IS to scale them
		logMsg("Hinting and scaling unscaled temp fonts...")
		for fontEntry in fileList:
			if options.doPreScalingHinting:
				hintFont(paths, fontEntry.tempFontPath)
			else:
				logMsg("\tSkipping hinting before scaling for %s" % (fontEntry.fontPath))
			fontEntry.tempFontScaledPath =  fontEntry.fontPath + ".tmp.scaled.ps"
			fontEntry.tempFontSafeScaledPath =  fontEntry.fontPath + ".tmp.safe.scaled.ps"
			srcResolution = scaleFont(paths, fontEntry.tempFontPath, fontEntry.tempFontScaledPath, fontEntry.tempFontSafeScaledPath, srcResolution, dstResolution, fontEntry.maxCoord)
			
		# If we are making new fonts, we need to build the final global stems a little differently than for doing IS
		if options.makeNewFonts:
			logMsg("Analyzing glyphs to derive global hinting metrics after scaling...")
			ptSizeRange = range(6,24)
			srcResolution = options.dstEM
			dstResolution = 600 # a typical printing dpi now-days.
			useScaledFiles = 1
			globalHints = getNewHintInfo(paths, options,  fileList, useScaledFiles, ptSizeRange, srcResolution, dstResolution)

		# Merge the data into the font files.
		logMsg("Merging scaled temp fonts into final font files... " + time.asctime())
		for fontEntry in fileList:
			if options.makeNewFonts:
				addHints(globalHints, fontEntry.tempFontScaledPath,  paths.tx)
			mergeTempFont(paths, options.makeNewFonts, fontEntry)

		for fontEntry in fileList:
			if not options.debug:
				if os.path.exists(fontEntry.tempFontSafeScaledPath):
					os.remove(fontEntry.tempFontSafeScaledPath)
				if os.path.exists(fontEntry.tempFontScaledPath):
					os.remove(fontEntry.tempFontScaledPath)
				if os.path.exists(fontEntry.tempFontPath):
					os.remove(fontEntry.tempFontPath)

		logMsg("All done. " + time.asctime())
	except(FDKEnvironmentError, CBOptionParseError, CBError):					
		logMsg("Fatal error - all done.")

	return
					
				
				
		


if __name__=='__main__':
	run()
