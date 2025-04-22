import os, sys
fileName = os.path.basename(__name__)

def preSample(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			#funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
		
		if state == 1:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1) #nothing to do
			state = 0
	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def wastePosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	logger = system.util.getLogger("PROSIA WastePosition")
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
		
		if state == 1:
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/" + str(Instruments_ID) + "/RInstRequestWastePosition",1)
			state += 1
			
		if state == 2:
			#wait for waste position
			#PROWSTTOPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"PROWSTTO")
#			logger.info("Waiting on WastePosition = 0")
			if system.tag.readBlocking("HMI/INSTRUMENTS/OPC_TAGS/" + str(Instruments_ID) + "/RInstRequestWastePosition")[0].value == 0:
				timeInState = 0
				state += 1
			else:
				timeInState += 1
			#lookup timeout values					
			PROWSTTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"PROWSTTO")
			#if timeout update instrument instance alarm tag display path and set alarm
#			logger.infof("Wait for in Waste Position timeout value: %s" , PROWSTTOValue )
			
			if timeInState >= int(PROWSTTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("PROWSTTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","PROSIA",SID)
		
		if state == 3:
#			if step == 1:
#				system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
			logger.info("Setting Function complete")
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
		
def destinationPosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("PROSIA destinationPosition")
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
			
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			#funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1

		if state == 1:
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/" + str(Instruments_ID) + "/RInstRequestDestinationPosition",1)
			state += 1
			
		if state == 2:
			#wait for destination position
			#PRODESTTOPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"PRODESTTO")
#			logger.info("Waiting on destinationPosition = 0")
			if system.tag.readBlocking("HMI/INSTRUMENTS/OPC_TAGS/" + str(Instruments_ID) + "/RInstRequestDestinationPosition")[0].value == 0:
				timeInState = 0
				state += 1
			else:
				timeInState += 1
			#lookup timeout values					
			PRODESTTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"PRODESTTO")
			
#			logger.infof("Wait for in Waste Position timeout value: %s" , PRODESTTOValue )
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(PRODESTTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("PRODESTTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","PROSIA",SID)
		
		if state == 3:
#			if step == 1:
#				system.tag.writeBlocking("PLC/OPN_RCP_REQ",1) #open receptacle valve
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
			
def processSample(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("PROSIA processSample")
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value	
		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			#funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			#check if there is a child before trying to pass sample
			nextStepID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step+1))
			if nextStepID == None: #sticky: need to add everywhere for end and cancel
				project.InstrumentModules.MiscFunctions.scEvent("END","From InstModule PROSIA",SID)
			state += 1

		if state == 1:
#			logger.info("Setting Sample Delivered = 1")
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/" + str(Instruments_ID) + "/RInstSampleDelivered",1)
			state += 1
					
		if state == 2:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1) #nothing to do
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def cleanPosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
	logger = system.util.getLogger("PROSIA CleanPosition")	

	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
#		raise TypeError("test")
#		logger = system.util.getLogger("Open Line wastePosition")
#		logger.infof("fileName = %s", fileName)
#		logger.infof("funcName = %s", funcName())
		#system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
		#return
		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			#funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1

		if state == 1:
			#wait for clean position
			#PROCLNTOPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"PROCLNTO")
#			logger.info("Waiting on Sample Delivered = 0")
			if system.tag.readBlocking("HMI/INSTRUMENTS/OPC_TAGS/" + str(Instruments_ID) + "/RInstSampleDelivered")[0].value == 0:
				timeInState = 0
				state += 1
			else:
				timeInState += 1
			#lookup timeout values					
			PROCLNTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"PROCLNTO")
			
#			logger.infof("Wait for in Waste Position timeout value: %s" , PROCLNTOValue )
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(PROCLNTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("PROCLNTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","PROSIA",SID)

		if state == 2:
#			if step == 1:
#				system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)#nothing to do
			state = 0
			
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
			
def cleanComplete(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("PROSIA cleanComplete")
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
			
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			#funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1

		if state == 1:
#			logger.info("Setting Cleaner Delivered = 1")
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/" + str(Instruments_ID) + "/RInstCleanerDelivered",1)
			state += 1
						
		if state == 2:
			#wait for purge position
			#PROPRGTOPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"PROPRGTO")
#			logger.info("Waiting on Cleaner Delivered = 0")
			if system.tag.readBlocking("HMI/INSTRUMENTS/OPC_TAGS/" + str(Instruments_ID) + "/RInstCleanerDelivered")[0].value == 0:
				timeInState = 0
				state += 1
			else:
				timeInState += 1
			#lookup timeout values					
			PROPRGTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"PROPRGTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(PROPRGTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("PROPRGTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","PROSIA",SID)
		
		if state == 3:
#			if step == 1:
#				system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
#			system.tag.writeBlocking("PLC/RCP_DEST_ON_ENA",1) #enable receptacle valve on during sanitization to destination
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 1)	
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
			
def checkAvail(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("PROSIA checkAvail")

	try:
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0 and system.tag.readBlocking("[]HMI/INSTRUMENTS/OPC_TAGS/" + str(Instruments_ID) + "/RInstStatus")[0].value == "Ready":
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
		else:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 0)
			TimeSinceAvail = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail")[0].value
			PROSIAATOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"PROSIAATO")
			if TimeSinceAvail == int(PROSIAATOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("PROSIAATO",Instruments_ID)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", TimeSinceAvail + 1)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def resetTags(Instrument_id,SID,step):
	pass