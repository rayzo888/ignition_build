import os, sys
fileName = os.path.basename(__name__)

#sticky: need SC_EVENT code everywhere
def preSample(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
				
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
				
			state += 1
	
		if state == 1:
				
			#look up destination command id
			sql = (
			"select Instruments_id as instrumentsId, id as destCmdId "
			"from destinationcommands dc "
			"where SampleCommands_id = %s and stepNumber = %d " %(SID,step))
			DCData = system.db.runQuery(sql)
			DestCmdID = DCData[0]['destCmdId']
			
			#query and write instrument parameters
			project.InstrumentModules.MiscFunctions.lookupInstrParm("tagParmData",Instruments_ID,DestCmdID,SID) #this script will contiue when function completes and tags are written
			app.db.saveInstrumentSettingsHistory(SID,Instruments_ID) #calls script that updates sample history with instrument settings enabled for history
			
			conSID = project.InstrumentModules.MiscFunctions.getSampleID(SID)
			NSIDPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NSID")
			system.tag.writeBlocking(NSIDPath, conSID)
			
			#look up sp #
			sql = ("select sp_number "
				"from vw_SampleCommands sc "
				"where sc_id = '%d' " %SID)
		
			seSP = system.db.runScalarQuery(sql)
			
			#expirement id
			expID = system.tag.readBlocking("HMI/SP" + str(seSP) + "/ExpmtID")[0].value
			NBATCHPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NBATCH")
			system.tag.writeBlocking(NBATCHPath, expID)

			#vessel id
			vesID = system.tag.readBlocking("HMI/SP" + str(seSP) + "/VesselID")[0].value
			NVESSELPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NVESSEL")
			system.tag.writeBlocking(NVESSELPath, vesID)			
			state += 1
		
		if state == 2:
				
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		import sys
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
	
def wastePosition(Instruments_ID,SID,step):

	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name

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
	logger = system.util.getLogger("NOVA Flex")
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
				project.InstrumentModules.MiscFunctions.scEvent("END","From InstModule NOVA",SID)
			state += 1
	
		if state == 1:
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",1) #open receptacle valve
			#send auto sample external command to Nova
			NASEPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NASE")
			system.opc.writeValue('Nova',NASEPath,1)
			logger.info("Sending Execute Command to NOVA")
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/2/Simulator/AutoSampleExternal/Execute", 1) #simulator
			state += 1
			
		if state == 2:
			#wait for Nova aquiring auto sample external and readyForSampleTime update
			#NTU = NOVA Time Update TAG NOVA_TIME_UPD set by gateway script and ReadyForSampleTime Tag getting new data.
			#NAQASE = NOVA Acquiring Auto Sample External
			NTUPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NTU")
			NAQASEPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NAQASE")
			#
			if system.tag.readBlocking(NAQASEPath)[0].value == 1 and system.tag.readBlocking(NTUPath)[0].value == 1:
				logger.info("Setting NTUPath to 0, going to state 3")
				system.tag.writeBlocking(NTUPath,0)
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
				
				
			#lookup timeout values					
			NAQASETOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"NAQASETO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(NAQASETOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("NAQASETO",Instruments_ID)
				#lookup and tagpath and reset instrument tag
				logger.info("Sending Execute Command to NOVA after timeout")
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/2/Simulator/AutoSampleExternal/Execute", 0) #reset							
				system.tag.writeBlocking(NTUPath,0)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule NOVA",SID)

		if state == 3:
			#3 second delay because continue was being missed
			if timeInState >= 3:
				state += 1
				timeInState = 0	
			else:
				timeInState += 1
				logger.info("In State 3 Incrementing counter for timer")

		if state == 4:
			#send auto sample external continue command to Nova
			NASECPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NASEC")
			logger.info("Sending Continue Command to NOVA")
			system.opc.writeValue('Nova',NASECPath,1)
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/2/Simulator/AutoSampleExternalContinue/Execute", 1)
			state += 1
			
		if state == 5:
			#wait for Nova analyzing auto sample external
			NANASEPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NANASE")
			if system.tag.readBlocking(NANASEPath)[0].value == 1:
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values
			NANASETOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"NANASETO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(NANASETOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("NANASETO",Instruments_ID)
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/2/Simulator/AutoSampleExternalContinue/Execute", 0) #reset
				state += 1 #sticky: should the state machine continue or abort somehow if timeout
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule NOVA",SID)
				
		if state == 6:
			#3 second delay
			if timeInState >= 3:
				state += 1
				timeInState = 0	
			else:
				timeInState += 1
	
				
		if state == 7:
			#send external auto sample continue command to Nova
			NASECPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NASEC")
			system.opc.writeValue('Nova',NASECPath,1)
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/2/Simulator/AutoSampleExternalContinue/Execute", 1)
			state += 1
	
		if state == 8:
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

	try:
		NAVAILPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"NAVAIL")
#		logger = system.util.getLogger("Nova Check Avail")
#		logger.infof("Instruments_ID = %d", Instruments_ID)
#		logger.infof("NAVAILPath = %d", NAVAILPath)	
		if system.tag.readBlocking("HMI/SIMULATOR_MODE")[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
		else:
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking(NAVAILPath)[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0: #sticky: need to add OPC tag(s)
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
	pass