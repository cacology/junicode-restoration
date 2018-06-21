#DeCIDFont


__copyright__ = """Copyright 2014 Adobe Systems Incorporated (http://www.adobe.com/). All Rights Reserved.
"""

__usage__ = """
decid v1.8 Cube July 30 2009
decid <path to CID font file> <path to layout file>
decid [-u] [-h]

DeCID builds all the data needed to run MakeCIDFont in the current
working directory. It takes a path to a CID-keyed OpenType/CFF font as
input. It also requires the path to a layout file. From these files, it
will build:
- a cidfontinfo file, if one does not already exist
- all the row font files, within the hint directory tree specified by
the layout file It will be a fatal error if the font contains CID values
that are not in the layout file.
"""

__methods__ = """ 
DeCID first reads the layout file, and parses this into a list of row
font directory paths, and a dictionary for each row font that maps CID
values to row font glyph names.

For each row font, the DeCID runs the tx tool with the decid option and
a glyph list selecting the glyphs for the row font. It then runs the
mergeFonts tool to rename the glyphs in the row font.

When done, it will use the tx tool to dump the OTF font top font dict,
and will build the cidfontino file from these values.
"""

import os
import re
import sys
import time
import FDKUtils
import traceback

def logMsg(*args):
	for s in args:
		print s

kRowFontFileName= "font.pfa"
kCIDFontInfoPath = "cidfontinfo"

kCharsetDir = os.path.join("SharedData", "CID charsets") # relative path to the parent directory for all the layout and subset files
kCIDFontInfokeyList = [
			"FontName",
			"FullName",
			"FamilyName",
			"Weight",
			"version",
			"Registry",
			"Ordering",
			"Supplement",
			"Layout",
			"isFixedPitch",
			"AdobeCopyright",
			"Trademark",
			"FSType",
			"IsBoldStyle",
			"IsItalicStyle",
			]

kRequiredCIDFontInfoFields = [
			"FontName",
			"Registry",
			"Ordering",
			"Supplement",
			 ]

kOptionalFields = [
			"FSType",
			"IsBoldStyle",
			"IsItalicStyle",
			"isFixedPitch",
			"Layout",
			"Trademark",
			"FullName",
			"FamilyName",
			"Weight",
			"version",
			"XUID",
			"AdobeCopyright", 
			]
kCIDFontInfokeyList = kRequiredCIDFontInfoFields + kOptionalFields

txFields = [ # [field name in tx, key name in cidfontinfo, value]
			["CIDFontName", "FontName", ""],
			["FullName", "FullName", ""],
			["FamilyName", "FamilyName", ""],
			["Weight", "Weight", ""],
			["CIDFontVersion", "version", ""],
			["cid.Registry", "Registry", ""],
			["cid.Ordering", "Ordering", ""],
			["cid.Supplement", "Supplement", ""],
			["Notice", "AdobeCopyright", ""],
			["Copyright", "AdobeCopyright", ""],
			["Trademark", "Trademark", ""],
			["FSType", "FSType", ""],
			["XUID", "XUID", ""],
			]

kLayoutDict = {
			"Adobe-CNS1-2" : "C9",
			"Adobe-CNS1-1" : "C9",
			"Adobe-GB1-2" : "C10",
			"Adobe-GB1-1" : "C9",
			"Adobe-Korea1-1" : "K10",
			"Adobe-Japan1-6" : "J16",
			"Adobe-Japan1-5" : "J15",
			"Adobe-Japan1-4" : "J14",
		 }

class FDKEnvironmentError(AttributeError):
	pass

class OptionParseError(KeyError):
	pass

class DeCIDError(KeyError):
	pass

class LayoutParseError(KeyError):
        pass

class ToolPaths:
	def __init__(self):
		try:
			self.exe_dir, fdkSharedDataDir = FDKUtils.findFDKDirs()
		except FDKUtils.FDKEnvError:
			raise FDKEnvironmentError
	
		if not os.path.exists(self.exe_dir ):
			logMsg("The FDK executable dir \"%s\" does not exist." % (self.exe_dir))
			logMsg("Please re-install the FDK. Quitting.")
			raise FDKEnvironmentError

		toolList = ["txCube", "mergeFontsCube", "spot"]
		missingTools = []
		for name in toolList:
			try:
				toolPath = FDKUtils.findFDKFile(self.exe_dir, name)
				toolPath = os.path.basename(toolPath)
			except FDKUtils.FDKEnvError:
				raise FDKEnvironmentError
			exec("self.%s = toolPath" % (name))
			command = "%s -u 2>&1" % toolPath
			report = FDKUtils.runShellCmd(command)
			if ("options" not in report) and ("Option" not in report):
				print report
				print command, len(report), report
				missingTools.append(name)
		if missingTools:
			logMsg("Please re-install the FDK. The executable directory \"%s\" is missing the tools: < %s >." % (self.exe_dir, ", ". join(missingTools)))
			logMsg("or the files referenced by the shell scripts are missing.")
			raise FDKEnvironmentError
				

		self.charsetDir = os.path.join( os.path.dirname(self.exe_dir), kCharsetDir)
		if not os.path.exists(self.charsetDir ):
			logMsg("The cid charset file directory \"%s\" does not exist." % (self.charsetDir))
			logMsg("Please re-install the FDK. Quitting.")
			raise FDKEnvironmentError

class OptionParseError(KeyError):
	pass

class ToolOptions:
	def __init__(self, args):
		self.inputFontPath = None
		self.layoutPath = None
		i = 0
		numArgs = len(args)
		while i < numArgs:
			arg = args[i]
			if arg == "-u":
				logMsg(__usage__)
				raise OptionParseError
			elif arg == "-h":
				logMsg(__usage__)
				logMsg(__methods__)
				raise OptionParseError
			elif arg[0] == "-":
				logMsg("Error parsing options. Unrecognized option '%s'. Quitting." % (arg))
				raise OptionParseError
			else:
				if not self.inputFontPath :
					self.inputFontPath = arg
				elif not self.layoutPath:
					self.layoutPath = arg
				else:
					logMsg("Error parsing options. Only two paths args are allowed.")
			i += 1

		if not self.inputFontPath:
			logMsg("Error. Must provide font path. Quitting.")
			raise OptionParseError 
		if not self.layoutPath:
			logMsg("Error. Must provide layout path. Quitting.")
			raise OptionParseError
 
		# end option processing loop.
		if not os.path.isfile(self.inputFontPath):
			logMsg("Could not find input font file '%s'. Quitting." % (self.inputFontPath))
		if not os.path.isfile(self.layoutPath):
			logMsg("Could not find layout file '%s'. Quitting." % (self.layoutPath))
		return

def makeCIDFontInfoFile(toolPaths, toolOpts, fontPath):
	command="%s -0 -cubef \"\"%s\"\" 2>&1" % (toolPaths.txCube, fontPath)
	report = FDKUtils.runShellCmd(command)
	if ("fatal" in report) or ("error" in report):
		print report
		logMsg("Failed to dump font dict using tx from font '%s'" % fontPath)
		raise DeCIDError
		
	cfiDict = {}
	for key in kRequiredCIDFontInfoFields + kOptionalFields:
		cfiDict[key] = None

	for entry in txFields:
		match = re.search(entry[0]+ "\s+(.+?)[\r\n]", report)
		if match:
			entry[2] = match.group(1)

	haveError = 0
	for entry in txFields:
		if entry[2]:
			cfiDict[entry[1]] = entry[2]
		elif entry[1] in kRequiredCIDFontInfoFields:
			haveError = 1
			logMsg("Error: did not find required info '%s' in tx dump of font '%s'." % (entry[1], fontPath))
	if haveError:
		logMsg( report)
		raise DeCIDError
	if not cfiDict["XUID"]:
		cfiDict["XUID"] = "[0 0 0000000]"
	else:
		txXUID = cfiDict["XUID"]  # fix the tx dump format to match cidfontinfo format
		txXUID = re.sub(r", *", r"", txXUID)
		cfiDict["XUID"] = "[%s]"% (txXUID[1:-1]) # replace {} with []

	if not cfiDict["Weight"]:
		cfiDict["Weight"] = "(Bold)"
	#Get more fields from spot.
	command="%s -t OS/2,hhea \"%s\" 2>&1" % (toolPaths.spot, fontPath)
	report = FDKUtils.runShellCmd(command)
	if "bad file" in report:
		# Not an OTF font, I'll just assume the following, since they can't be derived from a cid font.
		#  CJKV fonts don;t usually use style keywords anyway.
		cfiDict["IsBoldStyle"] = "true"
		cfiDict["IsItalicStyle"] = "false"
		# very few are monospaced! Assume this as well.
		cfiDict["isFixedPitch"] = "false"
	else: # it is an OTF font.
		if ("fatal" in report) or ("error" in report):
			logMsg( report)
			logMsg("Failed to dump OS2 table using spot from font '%s'" % fontPath)
			raise DeCIDError
		
		match = re.search("selection\s+=([^\r\n]+)", report)
		if not match:
			logMsg( report)
			logMsg("Failed find 'selection' in dump of OS2 table using spot from font '%s'" % fontPath)
			raise DeCIDError
		else:
			if "BOLD" in match.group(1):
				cfiDict["IsBoldStyle"] = "true"
			else:
				cfiDict["IsBoldStyle"] = "false"
			if "ITALIC" in  match.group(1):
				 cfiDict["IsItalicStyle"] = "true"
			else:
				cfiDict["IsItalicStyle"] = "false"

		match = re.search("numberOfLongHorMetrics=\s*(\d+)", report)
		if not match:
			logMsg( report)
			logMsg("Failed find 'numberOfLongHorMetrics' in dump of hhea table using spot from font '%s'" % fontPath)
			raise DeCIDError
		else:
			if eval(match.group(1)) == 1:
				cfiDict["isFixedPitch"] = "true"
			else:
				cfiDict["isFixedPitch"] = "false"

	cfiDict["Layout"] = "(" + os.path.basename(toolOpts.layoutPath) + ")"
	
	if not cfiDict.has_key("Trademark") or not cfiDict["Trademark"] :
		cfiDict["Trademark"] = "\"\"" 

	if not cfiDict.has_key("FamilyName") or not cfiDict["FamilyName"] :
		fontName = cfiDict["FontName"]
		familyName = fontName.split("-")[0]
		cfiDict["FamilyName"] = "%s\""  % (familyName)

	for key in kRequiredCIDFontInfoFields:
		if not cfiDict.has_key(key):
			logMsg("Error.Missing required field for cidfontifno '%s'" % (key))
			raise DeCIDError

	cfiPath = kCIDFontInfoPath
	try:
		fp = open(cfiPath, "wt")
		for key in kRequiredCIDFontInfoFields + kOptionalFields:
			value = cfiDict[key]
			if value == None:
				continue
			if value[0] == "\"":
				value = "(" + value[1:-1] + ")"
			string = "%s\t%s" % (key, value)
			fp.write(string + os.linesep)
		fp.close()
	except (IOError, OSError):
		logMsg("Error. Could not open and write file '%s'" % (cfiPath))
		raise DeCIDError
	logMsg("Wrote file '%s'." % (os.path.abspath(cfiPath)))
	return

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

def getCIDList(toolPaths, fontPath):
	command = "%s -mtx -cubef \"%s\"  2>&1" % (toolPaths.txCube, fontPath)
	report = FDKUtils.runShellCmd(command)
	if  ("fatal" in report) or ("error" in report):
		logMsg(report)
		logMsg("Error in using tx program to dump metrics with glyph names from  temporary font '%s'." % (fontPath))
		raise DeCIDError
	cidList = re.findall(r"glyph\[\d+\]\s+{([^,]+),", report)
	return cidList

def makeGAFile(gaPath, gaList, PSname, isNotDefFont):
	if isNotDefFont:
		notdefList = filter(lambda entry: entry[0] == "0", gaList)
		gaList = filter(lambda entry: entry[0] != "0", gaList)
	lineList = map(lambda entry: "%s\tcid%s" % (entry[1], entry[0]), gaList)
	if not isNotDefFont:
		lineList.append(".notdef\t.notdef")
	else:
		lineList.append("%s\t.notdef" % (notdefList[0][1]))
	
	gaText = "mergeFonts %s 0" % (PSname) + os.linesep + os.linesep.join(lineList) + os.linesep
	gf = file(gaPath, "wb")
	gf.write(gaText)
	gf.close()

def cmpCIDName(first, second):
	try:
		val1 = eval(first)
		val2 = eval(second)
		return cmp(val1, val2)
		
	except TypeError:
		return cmp(first, second)
	except:
		print traceback.print_last()
		return cmp(first, second)
		
def extractRowFont(toolPaths, srcFontPath, fontPath, PSName, glyphList):
	""" First, use tx to  copy the subset of glyphs to the row font, and convert it to a name-keyed font.
	Then use mergeFonts to rename the glyphs in the font."""
	cidList = map(lambda entry: entry[0], glyphList)
	cidList.sort(cmpCIDName)
	isNotDefFont = 0
	if "0" in cidList:
		isNotDefFont = 1

	glyohListArg = "/" + ",/".join(cidList)
	cidFontPath = fontPath + ".cid" # A name-keyed font, with the names in the form "cidXXXX".
	command = "%s -t1 -decid -std -cube -g %s \"%s\"  \"%s\"  2>&1" % (toolPaths.txCube, glyohListArg, srcFontPath, cidFontPath)
	report = FDKUtils.runShellCmd(command)
	if  ("fatal" in report) or ("error" in report):
		if "multiple" in report:			
			# Use tx to dump the glyph info and extract which are in which fd. Then add them  the one group at a time.
			command = "%s -dump -4  -cubef -g %s \"%s\"  2>&1" % (toolPaths.txCube, glyohListArg, srcFontPath)
			report = FDKUtils.runShellCmd(command)
			#	## glyph[tag] {cid,iFD,LanguageGroup}
			#	glyph[0] {0,3,1}
			#	glyph[414] {9275,2,1}
			fdList = re.findall(r"\{(\d+),\s*(\d+),\s*\d+\}", report)
			if not fdList:
				logMsg("Was not able to extract hint dict info for glyphs from source font.")
				logMsg("Quitting.")
				raise DeCIDError
			fdDict = {}
			for entry in fdList:
				glist = fdDict.get(entry[1], [])
				glist.append(entry[0])
				fdDict[entry[1]] = glist
			fdKeys = fdDict.keys()
			fdKeys.sort()
			# For the first group, we used tx with the -decid option
			# For the rest, we need to use mergeFont.
			cidList2 = fdDict[fdKeys[0]]
			cidList2.sort(cmpCIDName)
			glyohListArg = "/" + ",/".join(cidList2)
			cidFontPath = fontPath + ".cid" # A name-keyed font, with the names in the form "cidXXXX".
			command = "%s -t1 -decid -std -cube -g %s \"%s\"  \"%s\"  2>&1" % (toolPaths.txCube, glyohListArg, srcFontPath, cidFontPath)
			report = FDKUtils.runShellCmd(command)
			if  ("fatal" in report) or ("error" in report):
				logMsg("Error in using tx program to copy glyph subset to row font '%s'." % (fontPath))
				logMsg("Quitting.")
				raise DeCIDError
			cidTempFontPath = cidFontPath + ".tmp"
			for fd in fdKeys[1:]:
				# First we need to subset and convert the font to a Type font, then we need to merge it.
				cidList2 = fdDict[fd]
				cidList2.sort(cmpCIDName)
				glyohListArg = "/" + ",/".join(cidList2)
				cidFontPath = fontPath + ".cid" # A name-keyed font, with the names in the form "cidXXXX".
				command = "%s -t1 -decid -std -cube -g %s \"%s\"  \"%s\"  2>&1" % (toolPaths.txCube, glyohListArg, srcFontPath, cidTempFontPath)
				report = FDKUtils.runShellCmd(command)
				if  ("fatal" in report) or ("error" in report):
					logMsg("Error in using tx program to copy glyph subset to row font '%s'." % (fontPath))
					logMsg("Quitting.")
					raise DeCIDError

				# Now we need to merge it in to the cidFontPath
				cidTempFontPath2 = cidFontPath + ".mrg"
				command = "%s  -cube -std \"%s\" \"%s\" \"%s\" 2>&1" % (toolPaths.mergeFontsCube, cidTempFontPath2, cidFontPath, cidTempFontPath)
				report = FDKUtils.runShellCmd(command)
				if  ("fatal" in report) or ("error" in report):
					logMsg(report)
					logMsg("Error in using mergeFonts program to rename glyph subset for row font '%s'." % (fontPath))
					raise DeCIDError
				os.remove(cidTempFontPath)
				os.remove(cidFontPath)
				os.rename(cidTempFontPath2, cidFontPath)

		
		else:
			logMsg(report)
			logMsg("Error in using tx program to copy glyph subset to row font '%s'." % (fontPath))
			logMsg("Quitting.")
			raise DeCIDError

	# Now check that all the CID's got copied.
	nameList = getCIDList(toolPaths, cidFontPath)
	nameList = filter(lambda name: name != ".notdef", nameList)
	finalCIDList = map(lambda name: name[3:], nameList)
	finalCIDList.sort(cmpCIDName)
	testCIDList = filter(lambda name: name != "0", cidList)
	if testCIDList != finalCIDList:
		logMsg("Error. Not all of the CID's specified for the row font %s were successfully copied." % (fontPath))
		logMsg("Requested list: %s."  % (cidList))
		logMsg("Copied list: %s."  % (finalCIDList))
		raise DeCIDError

	# Now use mergeFonts to rename the font.
	# Make the glyph alias file
	gaPath = cidFontPath + ".ga.txt"
	makeGAFile(gaPath, glyphList, PSName, isNotDefFont)
	if isNotDefFont:
		# This is a special case, as cid0 gets renamed to ".notdef" rather than cid0, when the name-keyed CID font is made above.
		# To get ".notdef" and the laytou name for CID0 in the same font, we need to merge the .notdef glyph form a separate font,
		# and then add in the notdef glyph under the alternate name from the cidFontPath. Can't do it in one step from a single
		# font, s mergeFonts will not copy the same glyph twice.
		tempNotDef = "font.notdef.ps"
		fontDir = os.path.dirname(fontPath)
		if fontDir:
			tempNotDef = os.path.join(fontDir, tempNotDef)
		command = "%s -t1 -std -cube -g 0 \"%s\"  \"%s\"  2>&1" % (toolPaths.txCube, cidFontPath, tempNotDef)
		report = FDKUtils.runShellCmd(command)
		if  ("fatal" in report) or ("error" in report):
			logMsg(report)
			logMsg("Error in using tx program to make a temp font for the NotDef font face. '%s'." % (fontPath))
			raise DeCIDError
		command = "%s  -cube -std \"%s\" \"%s\" \"%s\" \"%s\"  2>&1" % (toolPaths.mergeFontsCube, fontPath, tempNotDef, gaPath, cidFontPath)
	else:
		command = "%s  -cube -std \"%s\" \"%s\" \"%s\"  2>&1" % (toolPaths.mergeFontsCube, fontPath, gaPath, cidFontPath)
	report = FDKUtils.runShellCmd(command)
	if  ("fatal" in report) or ("error" in report):
		logMsg(report)
		logMsg("Error in using mergeFonts program to rename glyph subset for row font '%s'." % (fontPath))
		print command
		raise DeCIDError
	os.remove(gaPath)
	os.remove(cidFontPath)
	if isNotDefFont and os.path.exists(tempNotDef):
		os.remove(tempNotDef)

def run(args):
	try:
		logMsg("Parsing layout file... " + time.asctime())
		opts = ToolOptions(args)
		paths = ToolPaths()
		paths.rootDir = os.path.dirname(opts.inputFontPath)
		if os.path.exists(kCIDFontInfoPath):
			logMsg("A '%s' file already exists. Skipping creation of a new one." % (kCIDFontInfoPath))
		else:
			makeCIDFontInfoFile(paths, opts, opts.inputFontPath)
		rowFontDict, cidDict, subsetDict = getRowFontDict(opts.layoutPath, None)

		logMsg("Extracting CID list from parent font... " + time.asctime())
		cidList = getCIDList(paths, opts.inputFontPath)

		# Build the list of row fonts to make.
		logMsg("Building directory tree and glyph lists... " + time.asctime())
		fontTreeDict  = {}
		curGlyphList = []
		for cid in cidList:
			try:
				rowFontDir, glyphName = cidDict[eval(cid)]
			except KeyError:
				logMsg("Error: cid in font ('%s') not in layout file." % (cid))
				raise DeCIDError

			if not fontTreeDict.has_key(rowFontDir):
				if not os.path.exists(rowFontDir):
					os.makedirs(rowFontDir)
				fontPath = os.path.join(rowFontDir, kRowFontFileName)
				fontTreeDict[rowFontDir]= [fontPath,  [ [cid, glyphName]]]
			else:
				fontTreeDict[rowFontDir][1].append( [cid, glyphName])

		# Now write the row fonts
		logMsg("Building row fonts... " + time.asctime())
		rowFontDirList = fontTreeDict.keys()
		rowFontDirList.sort()
		for rowFontDir in rowFontDirList:
			entry = fontTreeDict[rowFontDir]
			fontPath = entry[0]
			glyphList = entry[1]
			logMsg("---%s" % (fontPath))
			PSName = "-".join(os.path.split(rowFontDir))
			extractRowFont(paths, opts.inputFontPath, fontPath, PSName, glyphList)

	except (OptionParseError, DeCIDError, FDKEnvironmentError):
		pass
	logMsg("All done." + time.asctime())
	
if __name__=='__main__':
	run(sys.argv[1:])

