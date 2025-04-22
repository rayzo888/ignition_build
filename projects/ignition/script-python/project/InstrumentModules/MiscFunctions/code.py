import os, sys
fileName = os.path.basename(__name__)

def destinationType(seDestNum): #converts destination type number to destination type
	if seDestNum == 0:
		seDestType = "None"
	if seDestNum == 1:
		seDestType = "OL"
	elif seDestNum == 2:
		seDestType = "NOVA"
	elif seDestNum == 3:
		seDestType = "BIOHT"
	elif seDestNum == 4:
		seDestType = "CRS"
	elif seDestNum == 5:
		seDestType = "GILSON"
	return seDestType

def destinationType(seDestType): #converts destination type to destination type number
	if seDestType == "None":
		seDestNum = 0
	if seDestType == "OL":
		seDestNum = 1
	elif seDestType == "NOVA":
		seDestNum = 2
	elif seDestType == "BIOHT":
		seDestNum = 3
	elif seDestType == "CRS":
		seDestNum = 4
	elif seDestType == "GILSON":
		seDestNum = 5
	return seDestNum

def funcDict(funcName,Instrument_id,SID,step): 	#dictionary of functions
	funcDict = {
		'OLpreSample':project.InstrumentModules.OL.preSample, 'OLwastePosition':project.InstrumentModules.OL.wastePosition, 'OLdestinationPosition':project.InstrumentModules.OL.destinationPosition, 'OLprocessSample':project.InstrumentModules.OL.processSample, 'OLcleanPosition':project.InstrumentModules.OL.cleanPosition, 'OLcleanComplete':project.InstrumentModules.OL.cleanComplete, 'OLcheckAvail':project.InstrumentModules.OL.checkAvail, 'OLresetTags':project.InstrumentModules.OL.resetTags,
		'NOVApreSample':project.InstrumentModules.NOVA.preSample, 'NOVAwastePosition':project.InstrumentModules.NOVA.wastePosition, 'NOVAdestinationPosition':project.InstrumentModules.NOVA.destinationPosition, 'NOVAprocessSample':project.InstrumentModules.NOVA.processSample, 'NOVAcleanPosition':project.InstrumentModules.NOVA.cleanPosition, 'NOVAcleanComplete':project.InstrumentModules.NOVA.cleanComplete, 'NOVAcheckAvail':project.InstrumentModules.NOVA.checkAvail, 'NOVAresetTags':project.InstrumentModules.NOVA.resetTags,
		'BIOHTpreSample':project.InstrumentModules.BIOHT.preSample, 'BIOHTwastePosition':project.InstrumentModules.BIOHT.wastePosition, 'BIOHTdestinationPosition':project.InstrumentModules.BIOHT.destinationPosition, 'BIOHTprocessSample':project.InstrumentModules.BIOHT.processSample, 'BIOHTcleanPosition':project.InstrumentModules.BIOHT.cleanPosition, 'BIOHTcleanComplete':project.InstrumentModules.BIOHT.cleanComplete, 'BIOHTcheckAvail':project.InstrumentModules.BIOHT.checkAvail, 'BIOHTresetTags':project.InstrumentModules.BIOHT.resetTags,
		'CRSpreSample':project.InstrumentModules.CRS.preSample, 'CRSwastePosition':project.InstrumentModules.CRS.wastePosition, 'CRSdestinationPosition':project.InstrumentModules.CRS.destinationPosition, 'CRSprocessSample':project.InstrumentModules.CRS.processSample, 'CRScleanPosition':project.InstrumentModules.CRS.cleanPosition, 'CRSnextTier':project.InstrumentModules.CRS.nextTier, 'CRScleanComplete':project.InstrumentModules.CRS.cleanComplete, 'CRScheckAvail':project.InstrumentModules.CRS.checkAvail, 'CRSresetTags':project.InstrumentModules.CRS.resetTags,
		'GILSONpreSample':project.InstrumentModules.GILSON.preSample, 'GILSONwastePosition':project.InstrumentModules.GILSON.wastePosition, 'GILSONdestinationPosition':project.InstrumentModules.GILSON.destinationPosition, 'GILSONprocessSample':project.InstrumentModules.GILSON.processSample, 'GILSONcleanPosition':project.InstrumentModules.GILSON.cleanPosition, 'GILSONnextTier':project.InstrumentModules.GILSON.nextTier,'GILSONcleanComplete':project.InstrumentModules.GILSON.cleanComplete, 'GILSONcheckAvail':project.InstrumentModules.GILSON.checkAvail, 'GILSONresetTags':project.InstrumentModules.GILSON.resetTags,# 'GILSONsaveCRS':project.InstrumentModules.GILSON.saveCRS,
		'EP3BASEpreSample':project.InstrumentModules.EP3BASE.preSample, 'EP3BASEwastePosition':project.InstrumentModules.EP3BASE.wastePosition, 'EP3BASEdestinationPosition':project.InstrumentModules.EP3BASE.destinationPosition, 'EP3BASEprocessSample':project.InstrumentModules.EP3BASE.processSample, 'EP3BASEcleanPosition':project.InstrumentModules.EP3BASE.cleanPosition,'EP3BASEcleanComplete':project.InstrumentModules.EP3BASE.cleanComplete, 'EP3BASEcheckAvail':project.InstrumentModules.EP3BASE.checkAvail, 'EP3BASEerrorHandling':project.InstrumentModules.EP3BASE.errorHandling, 'EP3BASEresetTags':project.InstrumentModules.EP3BASE.resetTags,
		'DMpreSample':project.InstrumentModules.DM.preSample, 'DMwastePosition':project.InstrumentModules.DM.wastePosition, 'DMdestinationPosition':project.InstrumentModules.DM.destinationPosition, 'DMprocessSample':project.InstrumentModules.DM.processSample, 'DMcleanPosition':project.InstrumentModules.DM.cleanPosition, 'DMnextTier':project.InstrumentModules.DM.nextTier,'DMcleanComplete':project.InstrumentModules.DM.cleanComplete, 'DMcheckAvail':project.InstrumentModules.DM.checkAvail, 'DMresetTags':project.InstrumentModules.DM.resetTags,
		'FIALABUPLCpreSample':project.InstrumentModules.FIALABUPLC.preSample, 'FIALABUPLCwastePosition':project.InstrumentModules.FIALABUPLC.wastePosition, 'FIALABUPLCdestinationPosition':project.InstrumentModules.FIALABUPLC.destinationPosition, 'FIALABUPLCprocessSample':project.InstrumentModules.FIALABUPLC.processSample, 'FIALABUPLCcleanPosition':project.InstrumentModules.FIALABUPLC.cleanPosition, 'FIALABUPLCnextTier':project.InstrumentModules.FIALABUPLC.nextTier,'FIALABUPLCcleanComplete':project.InstrumentModules.FIALABUPLC.cleanComplete, 'FIALABUPLCcheckAvail':project.InstrumentModules.FIALABUPLC.checkAvail, 'FIALABUPLCresetTags':project.InstrumentModules.FIALABUPLC.resetTags,
		'HIRESpreSample':project.InstrumentModules.HIRES.preSample, 'HIRESwastePosition':project.InstrumentModules.HIRES.wastePosition, 'HIRESdestinationPosition':project.InstrumentModules.HIRES.destinationPosition, 'HIRESprocessSample':project.InstrumentModules.HIRES.processSample, 'HIREScleanPosition':project.InstrumentModules.HIRES.cleanPosition,'HIREScleanComplete':project.InstrumentModules.HIRES.cleanComplete, 'HIREScheckAvail':project.InstrumentModules.HIRES.checkAvail, 'HIRESresetTags':project.InstrumentModules.HIRES.resetTags,
		'AGLNTOLpreSample':project.InstrumentModules.AGLNTOL.preSample, 'AGLNTOLwastePosition':project.InstrumentModules.AGLNTOL.wastePosition, 'AGLNTOLdestinationPosition':project.InstrumentModules.AGLNTOL.destinationPosition, 'AGLNTOLprocessSample':project.InstrumentModules.AGLNTOL.processSample, 'AGLNTOLcleanPosition':project.InstrumentModules.AGLNTOL.cleanPosition,'AGLNTOLcleanComplete':project.InstrumentModules.AGLNTOL.cleanComplete, 'AGLNTOLcheckAvail':project.InstrumentModules.AGLNTOL.checkAvail, 'AGLNTOLresetTags':project.InstrumentModules.AGLNTOL.resetTags,
		'CHROMEpreSample':project.InstrumentModules.CHROME.preSample, 'CHROMEwastePosition':project.InstrumentModules.CHROME.wastePosition, 'CHROMEdestinationPosition':project.InstrumentModules.CHROME.destinationPosition, 'CHROMEprocessSample':project.InstrumentModules.CHROME.processSample, 'CHROMEcleanPosition':project.InstrumentModules.CHROME.cleanPosition,'CHROMEcleanComplete':project.InstrumentModules.CHROME.cleanComplete, 'CHROMEcheckAvail':project.InstrumentModules.CHROME.checkAvail, 'CHROMEresetTags':project.InstrumentModules.CHROME.resetTags,
		'NOVA2preSample':project.InstrumentModules.NOVA2.preSample, 'NOVA2wastePosition':project.InstrumentModules.NOVA2.wastePosition, 'NOVA2destinationPosition':project.InstrumentModules.NOVA2.destinationPosition, 'NOVA2processSample':project.InstrumentModules.NOVA2.processSample, 'NOVA2cleanPosition':project.InstrumentModules.NOVA2.cleanPosition, 'NOVA2cleanComplete':project.InstrumentModules.NOVA2.cleanComplete, 'NOVA2checkAvail':project.InstrumentModules.NOVA2.checkAvail, 'NOVA2resetTags':project.InstrumentModules.NOVA2.resetTags,
		'OLCSpreSample':project.InstrumentModules.OLCS.preSample, 'OLCSwastePosition':project.InstrumentModules.OLCS.wastePosition, 'OLCSdestinationPosition':project.InstrumentModules.OLCS.destinationPosition, 'OLCSprocessSample':project.InstrumentModules.OLCS.processSample, 'OLCScleanPosition':project.InstrumentModules.OLCS.cleanPosition,'OLCScleanComplete':project.InstrumentModules.OLCS.cleanComplete, 'OLCScheckAvail':project.InstrumentModules.OLCS.checkAvail, 'OLCSresetTags':project.InstrumentModules.OLCS.resetTags,
		'CHROMEVpreSample':project.InstrumentModules.CHROMEV.preSample, 'CHROMEVwastePosition':project.InstrumentModules.CHROMEV.wastePosition, 'CHROMEVdestinationPosition':project.InstrumentModules.CHROMEV.destinationPosition, 'CHROMEVprocessSample':project.InstrumentModules.CHROMEV.processSample, 'CHROMEVcleanPosition':project.InstrumentModules.CHROMEV.cleanPosition,'CHROMEVcleanComplete':project.InstrumentModules.CHROMEV.cleanComplete, 'CHROMEVcheckAvail':project.InstrumentModules.CHROMEV.checkAvail, 'CHROMEVresetTags':project.InstrumentModules.CHROMEV.resetTags,
		'PROSIApreSample':project.InstrumentModules.PROSIA.preSample, 'PROSIAwastePosition':project.InstrumentModules.PROSIA.wastePosition, 'PROSIAdestinationPosition':project.InstrumentModules.PROSIA.destinationPosition, 'PROSIAprocessSample':project.InstrumentModules.PROSIA.processSample, 'PROSIAcleanPosition':project.InstrumentModules.PROSIA.cleanPosition,'PROSIAcleanComplete':project.InstrumentModules.PROSIA.cleanComplete, 'PROSIAcheckAvail':project.InstrumentModules.PROSIA.checkAvail, 'PROSIAresetTags':project.InstrumentModules.PROSIA.resetTags,
		'CRSSUpreSample':project.InstrumentModules.CRSSU.preSample, 'CRSSUwastePosition':project.InstrumentModules.CRSSU.wastePosition, 'CRSSUdestinationPosition':project.InstrumentModules.CRSSU.destinationPosition, 'CRSSUprocessSample':project.InstrumentModules.CRSSU.processSample, 'CRSSUcleanPosition':project.InstrumentModules.CRSSU.cleanPosition,'CRSSUcleanComplete':project.InstrumentModules.CRSSU.cleanComplete, 'CRSSUcheckAvail':project.InstrumentModules.CRSSU.checkAvail, 'CRSSUresetTags':project.InstrumentModules.CRSSU.resetTags,
		'VICELLpreSample':project.InstrumentModules.VICELL.preSample, 'VICELLwastePosition':project.InstrumentModules.VICELL.wastePosition, 'VICELLdestinationPosition':project.InstrumentModules.VICELL.destinationPosition, 'VICELLprocessSample':project.InstrumentModules.VICELL.processSample, 'VICELLcleanPosition':project.InstrumentModules.VICELL.cleanPosition,'VICELLcleanComplete':project.InstrumentModules.VICELL.cleanComplete, 'VICELLcheckAvail':project.InstrumentModules.VICELL.checkAvail, 'VICELLresetTags':project.InstrumentModules.VICELL.resetTags,
		'OLNDpreSample':project.InstrumentModules.OLND.preSample, 'OLNDwastePosition':project.InstrumentModules.OLND.wastePosition, 'OLNDdestinationPosition':project.InstrumentModules.OLND.destinationPosition, 'OLNDprocessSample':project.InstrumentModules.OLND.processSample, 'OLNDcleanPosition':project.InstrumentModules.OLND.cleanPosition, 'OLNDcleanComplete':project.InstrumentModules.OLND.cleanComplete, 'OLNDcheckAvail':project.InstrumentModules.OLND.checkAvail, 'OLNDresetTags':project.InstrumentModules.OLND.resetTags,
		'SIpreSample':project.InstrumentModules.SI.preSample, 'SIwastePosition':project.InstrumentModules.SI.wastePosition, 'SIdestinationPosition':project.InstrumentModules.SI.destinationPosition, 'SIprocessSample':project.InstrumentModules.SI.processSample, 'SIcleanPosition':project.InstrumentModules.SI.cleanPosition, 'SIcleanComplete':project.InstrumentModules.SI.cleanComplete, 'SIcheckAvail':project.InstrumentModules.SI.checkAvail, 'SIresetTags':project.InstrumentModules.SI.resetTags,
		}
	
	funcDict[funcName](Instrument_id,SID,step)
	
#	'OLpreSample':project.InstrumentModules.OL.preSample, 'OLwastePosition':project.InstrumentModules.OL.wastePosition, 'OLdestinationPosition':project.InstrumentModules.OL.destinationPosition, 'OLprocessSample':project.InstrumentModules.OL.processSample, 'OLreset':project.InstrumentModules.OL.reset,
#	'NOVA2preSample':project.InstrumentModules.NOVA2.preSample, 'NOVA2wastePosition':project.InstrumentModules.NOVA2.wastePosition, 'NOVA2destinationPosition':project.InstrumentModules.NOVA2.destinationPosition, 'NOVA2processSample':project.InstrumentModules.NOVA2.processSample, 'NOVA2reset':project.InstrumentModules.NOVA2.reset,
#	'BIOHTpreSample':project.InstrumentModules.BIOHT.preSample, 'BIOHTwastePosition':project.InstrumentModules.BIOHT.wastePosition, 'BIOHTdestinationPosition':project.InstrumentModules.BIOHT.destinationPosition, 'BIOHTprocessSample':project.InstrumentModules.BIOHT.processSample, 'BIOHTreset':project.InstrumentModules.BIOHT.reset,
#	'CRSpreSample':project.InstrumentModules.CRS.preSample, 'CRSwastePosition':project.InstrumentModules.CRS.wastePosition, 'CRSdestinationPosition':project.InstrumentModules.CRS.destinationPosition, 'CRSprocessSample':project.InstrumentModules.CRS.processSample, 'CRSreset':project.InstrumentModules.CRS.reset,
#	'UPLCpreSample':project.InstrumentModules.UPLC.preSample, 'UPLCwastePosition':project.InstrumentModules.UPLC.wastePosition, 'UPLCdestinationPosition':project.InstrumentModules.UPLC.destinationPosition, 'UPLCprocessSample':project.InstrumentModules.UPLC.processSample, 'UPLCnextTier':project.InstrumentModules.UPLC.nextTier,'UPLCreset':project.InstrumentModules.UPLC.reset,

def passDelay(Instrument_id,seconds):
	def delay():
		import system
		import time
		time.sleep(seconds)
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instrument_id) + "/ActiveState")[0].value
		system.tag.writeBlocking("[]HMI/TESTING/delayDone",1)
	system.util.invokeAsynchronous(delay)

def delayFunc(seconds):
	def delay():
		import system
		import time
		time.sleep(seconds)
		system.tag.writeBlocking("HMI/TagWriteTest",seconds)
	system.util.invokeAsynchronous(delay)
	
def setTag(path,value):
	def loop():
		import time
		import system
		logger = system.util.getLogger("setTag")
		isSet = 0
		timeAcc = 0
		timeOut = 15
		tries = 1
		maxTries = 3
		system.tag.writeBlocking(path,value) #initial tag write
		while isSet == 0: #until tag is set, keep looping
			import time
			import system
			if system.tag.readBlocking(path)[0].value == value: #check if tag is set
				isSet = 1
				logger.infof("Tag write succeded in %d second(s) of try %d", (timeAcc,tries))
				return
			else: #if maxTries exceeded give up on setting this tag
				time.sleep(1)
				timeAcc += 1 #increment time
				if tries >= maxTries: 
					logger.infof("tries: %d", tries)
					logger.infof("Tag write failed after %d tries", maxTries)
					return
				else: #if tag not set check if maxTries exceeded
					if timeAcc >= timeOut: #if tag not set and maxTries not exceeded write to tag again
						logger.infof("timeAcc: %d", timeAcc)
						system.tag.writeBlocking(path,value)
						timeAcc = 0
						tries += 1
	system.util.invokeAsynchronous(loop)
	
def lookupInstrConf(info,Instruments_id,code): #sticky: update all functions so code doesn't lock up when no value returned
	if info == "value":
		value = system.db.runScalarQuery(
			"select value "
			"from InstrumentConfiguration_Lookup icl "
			"join InstrumentConfigurationValues icv on icv.InstrumentConfiguration_Lookup_id = icl.id "
			"where Instruments_id = %d and code = '%s' " %(Instruments_id,code))
		return value
	if info == "displayName":
		displayName = system.db.runScalarQuery(
			"select displayName "
			"from InstrumentConfiguration_Lookup icl "
			"join InstrumentConfigurationValues icv on icv.InstrumentConfiguration_Lookup_id = icl.id "
			"where Instruments_id = %d and code = '%s' " %(Instruments_id,code))
		return displayName
	if info == "tagPath":
		tagPath = system.db.runScalarQuery(
			"select tagPath "
			"from InstrumentConfiguration_Lookup icl "
			"join InstrumentConfigurationTags ict on ict.InstrumentConfiguration_Lookup_id = icl.id "
			"where Instruments_id = %d and code = '%s' " %(Instruments_id,code))
		return tagPath

def lookupInstrParm(info,Instruments_ID,DestCmdID,SID):
	funcName = lambda n=0: sys._getframe(n + 2).f_code.co_name

	try:
		if info == "tagParmData":
			#query all parameters
			sql = (
				"select value,tagPath "
				"from InstrumentParameter_Lookup ipl "
				"join InstrumentParameterValues ipv on ipv.InstrumentParameter_Lookup_id = ipl.id "
				"where Instruments_ID = %d and DestinationCommands_id = %d" %(Instruments_ID,DestCmdID))
			
			pyDataSet = system.db.runQuery(sql)
			
			#write all parameters to instrument tags
			for row in pyDataSet:
				if row["tagPath"] != None and row["value"] != None and row["tagPath"] != "" and row["value"] != "":
					logger = system.util.getLogger("Writing Parms")
					#logger.info("test")
					value = row["value"]
#					if "BioHTTestInfo" in row["tagPath"]:
#						conSID = project.InstrumentModules.MiscFunctions.getSampleID(SID)
#						value = '{"BioHTSampleID":' + '"' + conSID + value
					system.tag.writeBlocking(row["tagPath"], value)
					logger.infof("tagPath = %s", row["tagPath"])
					logger.infof("value = %s", value)

#						system.tag.writeBlocking(row["tagPath"],row["value"])
#					else:
#						system.tag.writeBlocking(row["tagPath"],row["value"])
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def lookupInstrType(scid,startStep): 	#lookup instrument type at starting point for the active sample
	sql = ("select instrumentType "
		"from destinationcommands dc "
		"where dc.stepNumber = %i "
		"and dc.SampleCommands_id = '%d' " %(startStep,scid))
	seInstrType = system.db.runScalarQuery(sql)
	return seInstrType

def logger(fileName,funcName,tracebk):
	logger = system.util.getLogger("Logger")
	logger.infof("File: %s. Function: %s. Error: %s, Line: %s"%(fileName,funcName,tracebk[1],tracebk[2].tb_lineno))
	
def scEvent(code,desc,SID):
	logger = system.util.getLogger("scEvent")
	#logger.info("started %d, %s"%(SID,code))
		
	destNum = system.db.runScalarQuery( 
	"SELECT d.number FROM SampleCommands sc " 
	"INNER JOIN SampleCommandData scd ON scd.id = sc.SampleCommandData_id " 
	"INNER JOIN Destinations d ON d.id = scd.Destinations_id " 
	"WHERE sc.id = %i" %SID)
	if desc in (None,""):
		desc = "No descrip"
	system.tag.writeBlocking("HMI/SC_EVENT/DEST_%d/SC_EVENT_CODE" %destNum, code)
	system.tag.writeBlocking("HMI/SC_EVENT/DEST_%d/SC_EVENT_SCID" %destNum, SID)
	system.tag.writeBlocking("HMI/SC_EVENT/DEST_%d/SC_EVENT_DESC" %destNum, desc)
	system.tag.writeBlocking("HMI/SC_EVENT/DEST_%d/SC_EVENT_SEND" %destNum, 1)
	logger.info("HMI/SC_EVENT/DEST_%d/SC_EVENT sent SID %d, code %s, desc %s" %(destNum,SID,code,desc))

#def setAlarm(code,Instruments_ID):
#	DisplayName = project.InstrumentModules.MiscFunctions.lookupInstrConf("displayName",Instruments_ID,code)
#	system.tag.editAlarmConfig(["HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/StateAlarm"], {"StateAlarmName":[["displayPath","Value","(" + code + ") " + str(DisplayName)]]})
#	system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/StateAlarm",1)

def setAlarm(code,Instruments_ID):
	DisplayName = project.InstrumentModules.MiscFunctions.lookupInstrConf("displayName",Instruments_ID,code)
	system.tag.writeBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/StateAlarmDisplayPath", "(" + code + ") " + str(DisplayName))
	system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/StateAlarm",1)

def getSampleID(SID):
	
	sql = ("select sc_sampleId "
		"from vw_SampleCommands sc "
		"where sc_Id = '%d' " %SID)
		
	return system.db.runScalarQuery(sql)
		
	#logger.info("finished")

def tagWriteDiag(path,value):
	import traceback
	logger = system.util.getLogger("Tag Write Diagnostics")
	logger.infof("Tag Path = %s", path)
	logger.infof("Value = %s", value)
	#logger.infof("Traceback: %s", traceback.format_exc())
	logger.infof("Traceback: %s", ''.join(traceback.format_stack()))
	
	valueBefore = system.tag.readBlocking(path)[0].value
	system.tag.writeBlocking(path, value)
	valueAfter = system.tag.readBlocking(path)[0].value

	if value == valueAfter: #updated to requested value
		logger.info("Tag has correct value")
		if valueBefore == valueAfter and valueBefore == value: #requested value = old value so not expecting to see a change
			logger.info("Tag did not need to update")
	else: #did not update to requeted value
		if valueBefore == valueAfter: #tag did not update
			logger.info("Tag did not update")
			print system.util.threadDump()
		else: 
			logger.info("Tag updated with bad value")
			print system.util.threadDump()

def updateInstrConf(value,code,Instruments_id,scId):
	#	
	logger = system.util.getLogger("Writing Instrument Settings")
	if value == "none":
		value = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_id,code) #look up value
	else:
		sql = (
			"update icv set value = ?, updatedOn = getdate(), updatedBy = 'system' "
			"from InstrumentConfigurationValues icv "
			"join InstrumentConfiguration_Lookup icl on icl.id = icv.InstrumentConfiguration_Lookup_id "
			"where icl.code = ? and icl.Instruments_id = ? "
		)
	
		system.db.runPrepUpdate(sql,[value,code,Instruments_id],skipAudit=1) #update value in db
	path = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_id,code) #look up tag path
	system.tag.writeBlocking(path,value) #write to tag path
	logger.infof("path = %s", path)
	logger.infof("value = %s", value)
	


