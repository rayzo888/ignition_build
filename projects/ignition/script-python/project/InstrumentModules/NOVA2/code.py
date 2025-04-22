import os, sys
fileName = os.path.basename(__name__)

#sticky: need SC_EVENT code everywhere
def preSample(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("NOVA2 PreSample Function")
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
				
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			
			# Set conditional handshake tags to zero.
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/22/RequestSampleUpdated",0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/22/SampleAspiratedUpdated",0)	
			
			state += 1
	
		if state == 1:
				
			#look up destination command id
			sql = (
			"select Instruments_id as instrumentsId, id as destCmdId "
			"from destinationcommands dc "
			"where SampleCommands_id = %s and stepNumber = %d " %(SID,step))
			DCData = system.db.runQuery(sql)
			DestCmdID = DCData[0]['destCmdId']
			
			#query and write instrument parameters to OPC Tags and 
			project.InstrumentModules.MiscFunctions.lookupInstrParm("tagParmData",Instruments_ID,DestCmdID,SID) #this script will contiue when function completes and tags are written
			app.db.saveInstrumentSettingsHistory(SID,Instruments_ID) #calls script that updates sample history with instrument settings enabled for history
			
			#get sampleID and write it to OPC tag.
			conSID = project.InstrumentModules.MiscFunctions.getSampleID(SID)
			NSIDPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NSID")
			system.tag.writeBlocking(NSIDPath, conSID)
			
			#look up sp #
			sql = ("select sp_number "
				"from vw_SampleCommands sc "
				"where sc_id = '%d' " %SID)
		
			seSP = system.db.runScalarQuery(sql)
			
			#Read Experiment ID and write it to the OPC tag			
			expID = system.tag.readBlocking("HMI/SP" + str(seSP) + "/ExpmtID")[0].value
			NBATCHPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NBATCH")
			system.tag.writeBlocking(NBATCHPath, expID)

			#Read Vessel id and write it to the OPC Tag
			vesID = system.tag.readBlocking("HMI/SP" + str(seSP) + "/VesselID")[0].value
			NVESSELPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NVESSEL")
			system.tag.writeBlocking(NVESSELPath, vesID)		
			
			#schedule analysis (trigger instrument to start) if configured for preSample
			NSRPSValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"NSRPS")
			if NSRPSValue == '1':
				NSAPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NSA")
				system.tag.writeBlocking(NSAPath,1)
				logger.info("Set EXT_OLSScheduleAnalysis to request NOVA 2 Sample")	
				state = 2
			else:
				state = 3
			
		if state == 2:
			#waiting in this state until the NOVA Flex II responds that it has scheduled the analysis.

			if system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/22/RequestSampleUpdated")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/22/RequestSampleUpdated",0)
				logger.info("Received EXT_OLSRequestSample acknowledging Sample Request on NOVA 2")
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			NSACValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"NSAC")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(NSACValue):
				project.InstrumentModules.MiscFunctions.setAlarm("NSAC",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule NOVA2",SID)			
			
		if state == 3:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	except:
		import sys
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
	
def wastePosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("NOVA2 WastePosition Function")
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
		
		if state == 1:
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1) #nothing to do
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def destinationPosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("NOVA2 DestinationPosition Function")
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
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
	
def processSample(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("NOVA2 ProcessSample Function")

	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
	
		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			#check if there is a child before trying to pass sample
			nextStepID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step+1))
			if nextStepID == None: #sticky: need to add everywhere for end and cancel
				project.InstrumentModules.MiscFunctions.scEvent("END","From InstModule NOVA2",SID)
			state += 1
	
		if state == 1:
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #open receptacle valve
			#schedule analysis (trigger instrument to start) if configured for processSample
			NSRPSValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"NSRPS")
			if NSRPSValue == '0':
				NSAPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NSA")
				system.tag.writeBlocking(NSAPath,1)
				logger.info("Set EXT_OLSScheduleAnalysis to request NOVA 2 Sample")						
				state = 2
			else:
				state = 4

		if state == 2:
			#waiting in this state until the NOVA Flex II responds that it has scheduled the analysis.

			if system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/22/RequestSampleUpdated")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/22/RequestSampleUpdated",0)
				logger.info("Received EXT_OLSRequestSample acknowledging Sample Request on NOVA 2")
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			NSACValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"NSAC")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(NSACValue):
				project.InstrumentModules.MiscFunctions.setAlarm("NSAC",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule NOVA2",SID)
			
		if state == 3:
			# Delay state between Request Sample signal and Aspirate signal in SyncEvent.
			logger.info("State 3 Delay between Sample request and aspirate signal")
		
			if timeInState < 10:
				timeInState += 1
			else: 
				state += 1
				timeInState = 0
		
		if state == 4:
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/22/Event","EXT_OLSRequestSample")
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/22/SetSyncEvent",1)
			logger.info("Sent EXT_OLSRequestSample SyncEvent to NOVA 2 to trigger sample to aspirate")
			state += 1	
			
		if state == 5:
			#wait for Nova sample apirated (Nova ready for sanitant)
			NSAUPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NSAU")
			if system.tag.readBlocking(NSAUPath)[0].value == 1:
				logger.info("Received SampleAspirated from NOVA")
				system.tag.writeBlocking(NSAUPath,0)
				
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			NSAUTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"NSAUTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(NSAUTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("NSAUTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule NOVA2",SID)
			
		if state == 6:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1) #nothing to do
			state = 0
	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def cleanPosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("NOVA2 CleanPosition Function")
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
		
		if state == 1:
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1) #nothing to do
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
	
def cleanComplete(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("NOVA2 CleanComplete Function")

	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
		
		if state == 1:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 1)	
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
	
def checkAvail(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name 
	logger = system.util.getLogger("NOVA2 CheckAvail Function")

	try:
		NAVAILPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NAVAIL")
#		logger.infof("Instruments_ID = %d", Instruments_ID)
#		logger.infof("NAVAILPath = %d", NAVAILPath)	
		if system.tag.readBlocking("HMI/SIMULATOR_MODE")[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
		else:
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking(NAVAILPath)[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0 and system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/CalPending")[0].value == 0: #sticky: need to add OPC tag(s)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
			else:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 0)
				TimeSinceAvail = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail")[0].value
				NLATOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"NLATO")
#				logger.infof("TimeSinceAvail type = %s", type(TimeSinceAvail))
#				logger.infof("NLATOValue type = %s", type(int(NLATOValue)))
#				logger.infof("matches = %b", TimeSinceAvail == int(NLATOValue))
				if TimeSinceAvail == int(NLATOValue):
					project.InstrumentModules.MiscFunctions.setAlarm("NLATO",Instruments_ID)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", TimeSinceAvail + 1)

		#check if instrument is ready for handoff from upstream instrument	
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction")[0].value == "ready" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/PreviousFunction")[0].value == "preSample" and system.tag.readBlocking(NAVAILPath)[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 1)
		else:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 0)

	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def resetTags(Instrument_id,SID,step):
	NSAUPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instrument_id,"NSAU")
	system.tag.writeBlocking(NSAUPath,0)
