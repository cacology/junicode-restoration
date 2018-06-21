#!/bin/env python
__copyright__ = """Copyright 2014 Adobe Systems Incorporated (http://www.adobe.com/). All Rights Reserved.
"""

__doc__ = """
bezLab. Wrapper for the Adobe BezierLab program. The BezierLab
program works on only one glyph at a time, expressed in the old 'bez'
format, a bezier-curve language much like PostScript Type 1, but with
text operators and coordinates.

The bezLab script uses Just von Rossum's fontTools library to read
and write a font file. It extracts the PostScript T2 charstring program
for each selected glyph in turn. It converts this into a 'bez language
program, and send this to the BezierLab program. The BezierLab program
returns a modified glyph in the form of a 'bez' program, and this script
converts this back into Type2 and sticks it back into the font.

In order to work on Type 1 font files as well as the OpenType/CFF fonts
supported directly by the fontTools library,  this script uses the 'tx'
tool to convert the font to a 'CFF' font program, and then builds a
partial OpenType font for the fontTools to work with.
"""

__usage__ = """
bezLab  Wrapper for the BezierLab curve-fitting program v1.6 Jan 21 2013
bezLab -h
bezLab -hb
bezLab -u
bezLab [-q] [-c] [-c1] [-c2] [-c3] [-g <glyph list>] [-gf <filename>]  [-o <output font path>] [-rb] [-wb] [-doBezLab] font-path
"""

__help__ = __usage__ + """

Takes a  list fonts, and an optional list of glyphs, and applies
the BezierLab program to glyphs in the fonts. If the list of glyphs
is supplied, the corrections are limited to the specified glyphs.


Options:

-h	Print help

-u	Print usage

-c1 If a bezier control point has a length of 1 unit or less and the segment
	length is less than 20 untis, retract  the bezier control point.
	(that is set to the same position as the parent on-line point).

-c2 Move the start point: if the current start point is not a line, then
	move the start point to the first line, if there is a line in the path.

-c3 If a path is not closed, then BezierLab adds a lineto to close it. 
	This option removes all such line segements when writing the outptu font.

-g <glyphID1>,<glyphID2>,...,<glyphIDn>   Correct only the specified list
	of glyphs. Note that all glyphs will be written to the output file.
	The list must be comma-delimited. The glyph ID's may be glyphID's,
	glyph names, or glyph CID's. If the latter, the CID value must be
	prefixed with the string "/". There must be no white-space in the
	glyph list. Examples: 
	    bezLab -g A,B,C,68 myFont 
	    bezLab -g /1030,/434,/1535, 68 myCIDFont

	A range of glyphs may be specified by providing two names separated
	only by a hyphen: 
	  bezLab -g zero-nine,onehalf myFont
	Note that the range will be resolved by expanding the glyph indices
	(GID)'s, not by alphabetic names.

-gf <file name>   Operate on only the list of glyphs contained in the
	specified file, The file must contain a comma-delimited list of
	glyph identifiers. Any number of space, tab, and new-line characters
	are permitted between glyph names and commas.

-o <output font path> Write corrected font to path. If not specified, then
	bezLab will write the corrected output to the original font path
	name.
	
-wb Simply write the selected glyph data from the font as bezier files. The bez
	files have the same name as the glyphs, with ".uc" added for upper-case
	glyphs. The default directory ia a 'bez' sub-directory in the source font's
	diretory. If the '-o' option is used, then that directory is used.

-rb Replace the selected glyph data in the font with outlines from bezier files.
	The bez files must ave the same name as the glyphs, with ".uc" added for
	upper-case glyphs. The default directory ia a 'bez' sub-directory in the
	source font's diretory. If the '-o' option is used, then that directory is
	used.
    
-doBezLab  By default, -rb and -wb will only read or write the  bez files. With
	the -doBezLab option, BezierLab will be applied after writing the bezier
	files with -wb, or before reading in the bezier files with -rb,. The modified
	bezier files will have the suffix ".new". To write out the font glyph data
	as bezier files, apply BezierLab, and read the modifed bez files back into the
	font, you would specify " -wb -rb -dobez".
	

-debug Leave the temp bez and font files in place, and report their names.

Options not on this list will be passed to the BezierLab program. Use the command:
'BezierLab -u' or 'BezierLab -h' to see the options specific to BezierLab.
"""

# Methods:

# Parse args. If glyphlist is from file, read in entire file as single string,
# and remove all whitespace, then parse out glyph-names and GID's.

# For each font name:
#    use fontTools library to open font and extract CFF table. 
#    If error, skip font and report error.
#    filter specified glyph list, if any, with list of glyphs in the font.
#    for identifier in glyph-list:
#        Get T2 charstring for glyph from parent font CFF table. If not present, report and skip.
#        Convert to bez file
#        CallbezierLab on bez string.
#        Convert bez file to T2 charstring, and update parent font CFF.

import sys
import os
import re
import copy
import time
from fontTools.ttLib import TTFont, getTableModule
import warnings
import FDKUtils
warnings.simplefilter("ignore", RuntimeWarning)

bezDebug = 0 # if true, don't delete the temp files
programName = sys.argv[0]

from BezTools import *


kBezSubDirectory = "bez"
kUCSuffix = ".uc"

class BZOptions:
	def __init__(self):
		self.inputPath = None
		self.outputPath = None
		self.glyphList = []
		self.verbose =1
		self.bezierLabArgs = []
		self.writeBezFiles = 0
		self.readBezFiles = 0
		self.bezPath = ""
		self.doBezierLab = 0
		
class BZOptionParseError(KeyError):
	pass

class BZFontError(KeyError):
	pass

class FDKEnvironmentError(AttributeError):
	pass

def logMsg(*args):
	for s in args:
		print s


def CheckEnvironment():
	txPath = 'tx'
	txError = 0
	command ="%s -u 2>&1" % (txPath)
	report = FDKUtils.runShellCmd(command)
	if "options" not in report:
			txError = 1
	
	if  txError:
		logMsg("Please re-install the FDK. The executable directory \"%s\" is missing the tool: < %s >." % (txPath ))
		logMsg("or the files referenced by the shell script is missing.")
		raise FDKEnvironmentError

	bzPath = 'bezierLab'
	txError = 0
	command = "%s -u 2>&1" % (bzPath)
	report = FDKUtils.runShellCmd(command)
	if "Options:" not in report:
			txError = 1
	
	if  txError:
		logMsg("Please re-install the FDK. The executable directory \"%s\" is missing the tool: < %s >." % (bzPath ))
		logMsg("or the files referenced by the shell script is missing.")
		raise FDKEnvironmentError

	return txPath, bzPath

def expandNames(glyphName):
	glyphRange = glyphName.split("-")
	if len(glyphRange) > 1:
		g1 = expandNames(glyphRange[0])
		g2 =  expandNames(glyphRange[1])
		glyphName =  "%s-%s" % (g1, g2)

	elif glyphName[0] == "/":
		glyphName = "cid" + glyphName[1:].zfill(5)

	elif glyphName.startswith("cid") and (len(glyphName) < 8):
		return "cid" + glyphName[3:].zfill(5)

	return glyphName

def parseGlyphListArg(glyphString):
	glyphString = re.sub(r"[ \t\r\n,]+",  ",",  glyphString)
	glyphList = glyphString.split(",")
	glyphList = map(expandNames, glyphList)
	glyphList =  filter(None, glyphList)
	return glyphList


def processBezArg(argv, i, bezierLabArgs):
	arg = argv[i]
	if arg == "-s":
		bezierLabArgs.append("-s \"%s\"" % (argv[i+1]))
		i += 1
	elif arg == "-c1":
		bezierLabArgs.append("-c1") # pull in 1 unit BCPS's
	elif arg == "-c2":
		bezierLabArgs.append("-c2") # change start point to first line
	elif arg == "-c3":
		bezierLabArgs.append("-c3") # remove final line-to's.
	elif arg == "-d":
		bezierLabArgs.append("-d %s %s" % (argv[i+1], argv[i+2]))
		i += 2
	elif arg == "-S":
		bezierLabArgs.append("-S")
	elif arg == "-m":
		bezierLabArgs.append("-m \"%s\"" % (argv[i+1]))
		i += 1
	elif arg == "-iso":
		bezierLabArgs.append("-iso")
	elif arg == "-only":
		bezierLabArgs.append("-only \"%s\"" % (argv[i+1]))
		i += 1
	elif arg == "-looser":
		bezierLabArgs.append("-looser %s" % (argv[i+1]))
		i += 1
	elif arg == "-noscale":
		bezierLabArgs.append("-noscale")
	elif arg == "-offsetx":
		bezierLabArgs.append("-offsetx %s" % (argv[i+1]))
		i += 1
	elif arg == "-offsety":
		bezierLabArgs.append("-offsety %s" % (argv[i+1]))
		i += 1
	elif arg == "-lo":
		bezierLabArgs.append("-lo %s" % (argv[i+1]))
		i += 1
	elif arg == "-hi":
		bezierLabArgs.append("-hi %s" % (argv[i+1]))
		i += 1
	elif arg == "-v":
		bezierLabArgs.append("-v")
	elif arg == "-U":
		bezierLabArgs.append("-U")
	elif arg == "-w":
		bezierLabArgs.append("-w \"%s\"" % (argv[i+1]))
		i += 1
	elif arg == "-W":
		bezierLabArgs.append("-W \"%s\"" % (argv[i+1]))
		i += 1
	else:
		if arg in ["-f", "-U"]:
			print "The BezierLab option %s is not supported by %s." % (programName, arg)
		else:
			bezierLabArgs.append(arg)
			
		i = 0
	return i
	
def getOptions():
	global bezDebug
	
	options = BZOptions()
	i = 1
	numOptions = len(sys.argv)
	while i < numOptions:
		arg = sys.argv[i]
		if options.inputPath:
			raise BZOptionParseError("Option Error: All options must preceed the  input font path <%s>." % arg) 

		if arg == "-h":
			logMsg(__help__)
			raise BZOptionParseError
		elif arg == "-u":
			logMsg(__usage__)
			raise BZOptionParseError
		elif arg == "-q":
			options.verbose = 0
		elif arg == "-debug":
			bezDebug = 1
		elif arg == "-wb":
			options.writeBezFiles = 1
		elif arg == "-rb":
			options.readBezFiles = 1
		elif arg == "-doBezLab":
			options.doBezierLab = 1
		elif arg == "-g":
			i = i +1
			glyphString = sys.argv[i]
			if glyphString[0] == "-":
				raise BZOptionParseError("Option Error: it looks like the first item in the glyph list following '-g' is another option.") 
			options.glyphList += parseGlyphListArg(glyphString)
		elif arg == "-gf":
			i = i +1
			filePath = sys.argv[i]
			if filePath[0] == "-":
				raise BZOptionParseError("Option Error: it looks like the the glyph list file following '-gf' is another option.") 
			try:
				gf = file(filePath, "rt")
				glyphString = gf.read()
				gf.close()
			except (IOError,OSError):
				raise BZOptionParseError("Option Error: could not open glyph list file <%s>." %  filePath) 
			options.glyphList += parseGlyphListArg(glyphString)
		elif arg == "-o":
			i = i +1
			options.outputPath = sys.argv[i]
		elif arg[0] == "-":
			i = processBezArg(sys.argv, i, options.bezierLabArgs)
			if not i:
				raise BZOptionParseError("Option Error: Unknown option <%s>." %  arg) 
		else:
			options.inputPath = arg
		i  += 1
	if not options.inputPath:
		raise BZOptionParseError("Option Error: You must provide at least one font file path.")
	if not options.outputPath:
		options.outputPath = options.inputPath
	if not os.path.exists(options.inputPath):
		print "Source font file is not found!", options.inputPath
		sys.exit(1)
		
	if options.writeBezFiles or options.readBezFiles:
		options.bezPath = os.path.dirname(options.outputPath)
		options.bezPath = os.path.join(options.bezPath, kBezSubDirectory)
		if not os.path.exists(options.bezPath):
			if options.writeBezFiles:
				os.makedirs(options.bezPath)
			else:
				print "The input directory for the bez files does not exist!", options.bezPath
				sys.exit(1)
	else:
		options.doBezierLab = 1

	return options


def getGlyphID(glyphTag, fontGlyphList):
	glyphID = None
	try:
		glyphID = int(glyphTag)
		glyphName = fontGlyphList[glyphID]
	except IndexError:
		pass
	except ValueError:
		try:
			glyphID = fontGlyphList.index(glyphTag)
		except IndexError:
			pass
		except ValueError:
			pass
	return glyphID

def getGlyphNames(glyphTag, fontGlyphList, fontFileName):
	glyphNameList = []
	rangeList = glyphTag.split("-")
	prevGID = getGlyphID(rangeList[0], fontGlyphList)
	if prevGID == None:
		if len(rangeList) > 1:
			logMsg( "\tWarning: glyph ID <%s> in range %s from glyph selection list option is not in font. <%s>." % (rangeList[0], glyphTag, fontFileName))
		else:
			logMsg( "\tWarning: glyph ID <%s> from glyph selection list option is not in font. <%s>." % (rangeList[0], fontFileName))
		return None
	glyphNameList.append(fontGlyphList[prevGID])

	for glyphTag2 in rangeList[1:]:
		#import pdb
		#pdb.set_trace()
		gid = getGlyphID(glyphTag2, fontGlyphList)
		if gid == None:
			logMsg( "\tWarning: glyph ID <%s> in range %s from glyph selection list option is not in font. <%s>." % (glyphTag2, glyphTag, fontFileName))
			return None
		for i in range(prevGID+1, gid+1):
			glyphNameList.append(fontGlyphList[i])
		prevGID = gid

	return glyphNameList

def filterGlyphList(options, fontGlyphList, fontFileName):
	# Return the list of glyphs which are in the intersection of the argument list and the glyphs in the font
	# Complain about glyphs in the argument list which are not in the font.
	if not options.glyphList:
		glyphList = fontGlyphList
	else:
		# expand ranges:
		glyphList = []
		for glyphTag in options.glyphList:
			glyphNames = getGlyphNames(glyphTag, fontGlyphList, fontFileName)
			if glyphNames != None:
				glyphList.extend(glyphNames)
	return glyphList




def openFile(path, txPath):
	# If input font is  CFF or PS, build a dummy ttFont in memory.
	# return ttFont, and flag if is a real OTF font Return flag is 0 if OTF, 1 if CFF, and 2 if PS/
	fontType  = 0 # OTF
	tempPath = os.path.dirname(path)
	tempPathCFF  = os.path.join(tempPath, "temp.bz.cff")
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
			raise BZFontError("Error opening or reading from font file <%s>." % path)
		except TTLibError:
			raise BZFontError("Error parsing font file <%s>." % path)

		try:
			cffTable = ttFont["CFF "]
		except KeyError:
			raise BZFontError("Error: font is not a CFF font <%s>." % fontFileName)

		return ttFont, fontType

	# It is not an OTF file.
	if (data[0] == '\1') and (data[1] == '\0'): # CFF file
		fontType = 1
		tempPathCFF = path
	elif not "%" in data:
		#not a PS file either
		logMsg("Font file must be a PS, CFF or OTF  fontfile: %s." % path)
		raise BZFontError("Font file must be PS, CFF or OTF file: %s." % path)

	else:  # It is a PS file. Convert to CFF.	
		fontType =  2
		command="%s   -cff +b  \"%s\" \"%s\" 2>&1" % (txPath, path, tempPathCFF)
		report = FDKUtils.runShellCmd(command)
		if "fatal" in report:
			logMsg("Attempted to convert font %s  from PS to a temporary CFF data file." % path)
			logMsg(report)
			raise BZFontError("Failed to convert PS font %s to a temp CFF font." % path)

	# now package the CFF font as an OTF font for use by autohint.
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
		raise BZFontError("Error parsing font file <%s>." % fontFileName)
	return ttFont, fontType


def saveFontFile(ttFont, inputPath, outputPath, fontType, txPath):
	overwriteOriginal = 0
	if inputPath == outputPath:
		overwriteOriginal = 1
	tempPath = os.path.dirname(inputPath)
	tempPath = os.path.join(tempPath, "temp.bz.cff")

	if fontType == 0: # OTF
		if overwriteOriginal:
			ttFont.save(tempPath)
			ttFont.close()
			if os.path.exists(inputPath):
				try:
					os.remove(inputPath)
					os.rename(tempPath, inputPath)
				except (OSError, IOError):
					logMsg("Error: could not overwrite original font file path '%s'. Hinted font file path is '%s'." % (inputPath, tempPath))
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
				os.rename(tempPath, inputPath)
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
				raise IOError("Failed to convert corrected font temp file with tx %s" % tempPath)
			if overwriteOriginal:
				os.remove(tempPath)
			# remove temp file left over from openFile.
			if (not bezDebug) and os.path.exists(tempPath):
				try:
					os.remove(tempPath)
				except (IOError,OSError):
					logMsg("Error: could not delete temporary font file path '%s'." % (tempPath))
					
	print "Save processed file:", outputPath					

def correctFile(options, txPath, bzPath):
	#    use fontTools library to open font and extract CFF table. 
	#    If error, skip font and report error.
	path = options.inputPath
	fontFileName = os.path.basename(path)
	logMsg("Processing font %s. Start time: %s." % (path, time.asctime()))

	ttFont, fontType = openFile(path, txPath)
	fontGlyphList = ttFont.getGlyphOrder()
	cffTable = ttFont["CFF "]
	topDict = cffTable.cff.topDictIndex[0]
	#   filter specified list, if any, with font list.
	glyphList = filterGlyphList(options, fontGlyphList, fontFileName)
	if not glyphList:
		raise BZFontError("Error: None of the selected glyph names are in font <%s>." % fontFileName)

	tempBaseName = os.tempnam()
	tempBez = tempBaseName + ".bez"
	tempBezNew = tempBez + ".new"
	
	#print "tempBaseName", tempBaseName
	psName = cffTable.cff.fontNames[0]
	

	#    for identifier in glyph-list:
	# 	Get charstring.
	charStrings = topDict.CharStrings
	charStringIndex = charStrings.charStringsIndex
	removeHints = 1

	isCID = hasattr(topDict, "FDSelect")
	lastFDIndex = 0
	anyGlyphChanged = 0
	if isCID:
		options.noFlex = 1
		
	if  not options.verbose:
		dotCount = 0
		curTime = time.time()
		
	for name in glyphList:
		if isCID:
			gid = ttFont.getGlyphID(name)
		else:
			gid = charStrings.charStrings[name]

		# 	Convert to bez format
		# 	Build autohint point list identifier
		t2CharString = charStringIndex[gid]
		try:
			bezString, hasHints, t2Wdth = convertT2GlyphToBez(t2CharString, removeHints)
			bezString = "% " + name + os.linesep + bezString
		except SEACError:
			print "\tSkipping %s; can't process 'seac' composite glyphs." % (name)
			continue # skip 'seac' composite glyphs.
		if "mt" not in bezString:
			# skip empty glyphs.
			continue

		if options.verbose:
			logMsg("Processing %s." %name)
		else:
			newTime = time.time()
			if (newTime - curTime) > 1:
				print ".",
				sys.stdout.flush()
				curTime = newTime
				dotCount +=1
			if dotCount > 40:
				dotCount = 0
				print ""
		
		if (options.readBezFiles or options.writeBezFiles):
			# Need use local glyph names for bez files, not temp file names.
			tempBez = os.path.join(options.bezPath, name)
			if not name.islower():
				tempBez = tempBez + kUCSuffix
			# If not doBezierLab, then we'll just read in the file that was written out.
			tempBezNew = tempBez
			if options.doBezierLab:
				tempBezNew = tempBezNew + ".new"
				
		# we should be writing the src glyph data to a bez file only if neither
		# options.readBezFiles or options.writeBezFiles are specified, or if
		# options.writeBezFiles is specified.
		if (not options.readBezFiles) or (options.writeBezFiles):
			bp = open(tempBez, "wt") 
			bp.write(bezString)
			bp.close()
		
		if options.writeBezFiles and not options.doBezierLab:
			continue
		
			
		# 	Call bezierLab on the bez data.
		if options.doBezierLab:
			tempDirNew, tempFileNew = os.path.split(tempBezNew)
			tempDirNewArg = ""
			if tempDirNew:
				tempDirNewArg = " -o \"%s\"" % (tempDirNew)
			bezArgs = ""
			if options.bezierLabArgs:
				bezArgs = " ".join(options.bezierLabArgs)
			command = "BezierLab %s -f \"%s\"  %s  \"%s\"" % (tempDirNewArg, tempFileNew, bezArgs, tempBez)
			log = FDKUtils.runShellCmd(command)
			
			if options.verbose and log:
				print "BezierLab log <<<",log, ">>>"


		if options.writeBezFiles and not  options.readBezFiles:
			continue # we get here if options.writeBezFiles and options.doBezierLab
			
		# Get rid of input bez file if we are using temp files.
		if not (options.readBezFiles or options.writeBezFiles):
			if os.path.exists(tempBez):
				if bezDebug:
					print "src bez file at:", tempBez
				else:
					os.remove(tempBez)

		if os.path.exists(tempBezNew):
			bp = open(tempBezNew, "rt")
			newBezString = bp.read()
			bp.close()
			if bezDebug:
				print "new bez file at:", tempBezNew
			else:
				if not (options.readBezFiles or options.writeBezFiles):
					os.remove(tempBezNew)
		else:
			if options.doBezierLab:
				print "BezierLab did not create expected output file", tempBezNew
				print "BezierLab log <<<",log, ">>>"
			else:
				print "Could not find bezier file for input glyph", tempBezNew
			continue
			
		# 	Convert bez to charstring, and update CFF.
		t2Program = [t2Wdth] + convertBezToT2(newBezString)
		if t2Program:
			t2CharString.program = t2Program
		else:
			logMsg("\t%s Skipping glyph - error in processing hinted outline." % (name))
			continue


	if not options.verbose:
		print "" # print final new line after progress dots.

	if options.readBezFiles or not options.writeBezFiles:	
		saveFontFile(ttFont, path, options.outputPath, fontType, txPath)
	logMsg("Done with font %s. End time: %s." % (options.outputPath, time.asctime()))

def main():

	try:
		txPath, bzPath = CheckEnvironment()
	except FDKEnvironmentError,e:
		logMsg(e)
		return

	try:
		options = getOptions()
	except BZOptionParseError,e:
		logMsg(e)
		return

	# verify that all files exist.
	if not os.path.isfile(options.inputPath):
		logMsg("File does not exist: <%s>." % options.inputPath)
	else:
		try:
			correctFile(options, txPath, bzPath)
			
		except (BZFontError),e:
			logMsg("\t%s" % e)
	return


if __name__=='__main__':
	main()
	

