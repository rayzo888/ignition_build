import os, sys
fileName = os.path.basename(__name__)

def preSample(Instruments_ID,SID,step): 
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
		logger = system.util.getLogger("HiRes PreSample")
		
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value

		if state == 0:
			logger.info("state 0 Set Function Tags")
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
		
		if state == 1:
			logger.info("state 1 Get instrument parameters")
			
			#look up destination command id
			sql = (
			"select Instruments_id as instrumentsId, id as destCmdId "
			"from destinationcommands dc "
			"where SampleCommands_id = %s and stepNumber = %d " %(SID,step))
			DCData = system.db.runQuery(sql)
			DestCmdID = DCData[0]['destCmdId']
			
			#query and write instrument parameters
			project.InstrumentModules.MiscFunctions.lookupInstrParm("tagParmData",Instruments_ID,DestCmdID,SID) #this script will contiue when function completes and tags are written
			state += 1
	
 		if state == 2:
 			logger.info("State 2 Send Prepare Measurement")
 			
 			#Read that another command to the HiRes is not in process
 			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
 			
 			if cmdState == 0:
				#Send Prepare Measurement command 
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/PreSampleComms',1)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',"+CDM#")
				logger.info("State 2 Command sent is: +CDM#")
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus",0)
				state += 1
			
		if state == 3:
			logger.info("state 3 Waiting for Prepare Measurement Response")
			
			#Wait for response back	
 			#Read was command successful
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)
			if cmdStatus == 1:			
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
				state += 1
				timeInState = 0
				
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
				#increment time in state tag
				else:
					timeInState += 1
			
			
		if state == 4:
			logger.info("state 4 Set Workarea")
			#Read that another command to the HiRes is not in process
			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
			
			if cmdState == 0:
				#Send Set Workarea command 
				#Note: workarea is hardcoded to "standard".
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',"+SWAstandard#")
				logger.info("State 4 Command sent is: +SWAstandard#")
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus",0)
				state += 1
			
		if state == 5:
			logger.info("state 5 wait for Set workarea command response")
			
			#Wait for response back	
 			#Read was command successful
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)
			
			if cmdStatus == 1:			
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
				state += 1
				timeInState = 0
				
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
				#increment time in state tag
				else:
					timeInState += 1

			
		if state == 6:
			logger.info("state 6 set Reactor (Vessel) ID")
			#Send Set ReactorID (VesselID) command 
 			#Read that another command to the HiRes is not in process
			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
			
			if cmdState == 0:			
				#look up sp #
				sql = ("select sp_number "
					"from vw_SampleCommands sc "
					"where sc_id = '%d' " %SID)
			
				seSP = system.db.runScalarQuery(sql)
				
				#vessel id
				vesID = system.tag.readBlocking("HMI/SP" + str(seSP) + "/VesselID")[0].value
				vesIDstr = "+RA" + vesID + "#"
				logger.infof("State 6 Command sent is: %s", str(vesIDstr))
				
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',vesIDstr)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus",0)
				state += 1
			
		if state == 7:
			logger.info("state 7 Vessel ID response")
			#Wait for response back	
 			#Read was command successful
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)
			
			if cmdStatus == 1:			
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
				state += 1
				timeInState = 0
				
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
				#increment time in state tag
				else:
					timeInState += 1
		
		if state == 8:
			logger.info("state 8 Set Sample ID")
 			#Read that another command to the HiRes is not in process
			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
			
			if cmdState == 0:
				#Send Set Sample ID command 
				#sample id
				conSID = project.InstrumentModules.MiscFunctions.getSampleID(SID)
				conSIDstr = "+LA" + conSID + "#"
				logger.infof("State 8 Command sent is: %s",conSIDstr)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',conSIDstr)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus",0)
				state += 1
			
		if state == 9:
			logger.info("state 9 Wait for Set Sample ID return")
			#Wait for response back	
 			#Read was command successful
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)
						
			if cmdStatus == 1:			
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
				state += 1
				timeInState = 0
				
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
				#increment time in state tag
				else:
					timeInState += 1
			
		if state == 10:
			logger.info("state 10 Set Cell Type Parameter")			
 			#Read that another command to the HiRes is not in process
			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
			
			if cmdState == 0:
				#Read in cell type parameter
				paramCellType = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/ParmCellType')[0].value
				paramStr = "+SCT" + paramCellType + "#"
				logger.infof("State 10 Command sent is: %s",paramStr)
				
				#Send Set Cell Type command
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',paramStr)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus",0)
				 
				state += 1
			
		if state == 11:
			logger.info("state 11")
			#Wait for response back	
 			#Read was command successful
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)

			if cmdStatus == 1:			
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
				state += 1
				timeInState = 0
				
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
				#increment time in state tag
				else:
					timeInState += 1
		
		if state == 12:
			logger.info("state 12 set Sample Port")					
 			#Read that another command to the HiRes is not in process
			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
			
			if cmdState == 0:
				#Send Set Sample Port Name command 
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',"+SSPNRemote Port#")
				logger.info("State 12 Command sent is: +SSPNRemote Port#")
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus",0)
				state += 1
			
		if state == 13:
			logger.info("state 13")
			#Wait for response back	
 			#Read was command successful
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)
			
			if cmdStatus == 1:			
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
				state += 1
				timeInState = 0
				
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
				#increment time in state tag
				else:
					timeInState += 1
		
		if state == 14:
			logger.info("state 14 set Dilution Ratio")
 			#Read that another command to the HiRes is not in process
			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
			
			if cmdState == 0:
				#Read in Dilution parameter
				paramDilution = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/ParmDilutionRatio')[0].value
				paramStr = "+SDI" + paramDilution + "#"	
				logger.infof("State 14 Command sent is: %s",paramStr)
				#Send Set Dilution
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',paramStr)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus",0)
				state += 1
			
		if state == 15:
			logger.info("state 15")
			#Wait for response back	
 			#Read was command successful
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)
			
			if cmdStatus == 1:			
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
				state += 1
				timeInState = 0
				
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
					#increment time in state tag
				else:
					timeInState += 1

		if state == 16:
			logger.info("state 16 set Precision")
 			#Read that another command to the HiRes is not in process
			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
			
			if cmdState == 0:
				#Read in Precision parameter
				paramPrecision = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/ParmPrecision')[0].value
				paramStr = "+SPR" + paramPrecision + "#"
				logger.infof("State 16 Command sent is: %s",paramStr)
				#Send Set Precision command
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',paramStr)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus",0)
				state += 1 
			
		if state == 17:
			logger.info("state 17")
			#Wait for response back	
 			#Read was command successful
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)
			
			if cmdStatus == 1:			
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
				state += 1
				timeInState = 0
			
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
				#increment time in state tag
				else:
					timeInState += 1
			
		if state == 18:
			logger.info("state 18 set Sample Volume")
 			#Read that another command to the HiRes is not in process
			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
			
			if cmdState == 0:
				#Send Set Sample Volume command 
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',"+SSV300#")
				logger.info("State 18 Command sent is: +SSV300#")
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus",0)
				state += 1
			
		if state == 19:
			logger.info("state 19")
			#Wait for response back	
 			#Read was command successful
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)
			
			if cmdStatus == 1:			
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
				state += 1
				timeInState = 0
				
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
					#increment time in state tag
				else:
					timeInState += 1
	
		if state == 20:
			logger.info("state 20")
			system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/PreSampleComms',0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			#project.InstrumentModules.MiscFunctions.tagWriteDiag("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone",1)
			state = 0

		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)


		if state == 21:
			logger.info("State 2 Send Cancel Prepare Measurement")
			
			#Read that another command to the HiRes is not in process
			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
			
			if cmdState == 0:
				#Send Prepare Measurement command 
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',"+CA#")
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus",0)
			
			state = 20
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def wastePosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name

	try:
		logger = system.util.getLogger("HiRes WastePosition")
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

def destinationPosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name

	try:
		logger = system.util.getLogger("HiRes DestinationPosition")
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

	try:
		logger = system.util.getLogger("HiRes Process Sample")
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			#check if there is a child before trying to pass sample
			nextStepID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step+1))
			if nextStepID == None:
				project.InstrumentModules.MiscFunctions.scEvent("END","From InstModule FIALABUPLC",SID)
			state += 1

		if state == 1:
 			logger.info("state 1")
 			
 			#Read that another command to the HiRes is not in process
 			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
 			
 			if cmdState == 0:
				#Send Prepare Measurement command 
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',"+CM#")
				logger.info("State 1 Command sent is: +CM#")
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				state += 1
			
		if state == 2:
			logger.info("state 2 Process Sample Start Analyis Response")
			
			#Wait for response back	
 			#Read that another command to the HiRes is not in process
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)
 						
			if cmdStatus == 1:
				state += 1
				timeInState = 0
				
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
				#increment time in state tag
				else:
					timeInState += 1
		
		if state == 3:
			#wait for HiRes Measurement complete
			
			if system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/HiResStatus')[0].value == "Measurement Running":
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			HIRESMRUNTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESMRUNTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(HIRESMRUNTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("HIRESMRUNTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
				
						
		if state == 4:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
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
		logger = system.util.getLogger("HiRes Clean Position")
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1

		if state == 1:
			#Delay after start sample process before signaling OK to Clean					
			HIRESCLNDLYValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCLNDLY")
			logger.infof('HiResCLNDLY Value is: %s',HIRESCLNDLYValue)
			logger.infof('HiRes Time in state is: %s',timeInState)
			if timeInState >= int(HIRESCLNDLYValue):
				state += 1
				timeInState = 0
			else:
				timeInState += 1

					
		if state == 2:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1) #nothing to do
			state = 0
	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
		
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
	
def cleanComplete(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
		logger = system.util.getLogger("HiRes Clean Complete")
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1

		if state == 1:
			logger.info("state 1 Wait for HiRes Processing Complete")
			#wait for HiRes Measurement complete
			TmpStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/HiResStatus')[0].value
			logger.infof('HiResStatus is: %s',TmpStatus)
			if TmpStatus == "Ready":
				logger.info("State 1 Measurement Complete Advance")
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			HIRESMCMPTTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESMCMPTTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(HIRESMCMPTTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("HIRESMCMPTTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
							
		if state == 2:
			logger.info("state 2")
			
			#Read that another command to the HiRes is not in process
			cmdState = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent')[0].value
			
			if cmdState == 0:
				#Send Prepare Measurement command 
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/TCP_TAGS/12/Writable',"+MNUltraFastClean#")
				logger.info("State 2 Command sent is: +MNUltraFastClean#")
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',1)
				state += 1
			
		if state == 3:
			logger.info("state 3 UltraFastClean Command Response")
			
			#Wait for response back	
			#Read was command successful
			cmdStatus = system.tag.readBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CmdStatus')[0].value
			logger.infof('cmdStatus value is: %d',cmdStatus)
			
			if cmdStatus == 1:			
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
				state += 1
				timeInState = 0
				
			else:
				#if timeout update instrument instance alarm tag display path and set alarm
				#lookup timeout values					
				HIRESCMDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESCMDTO")
				#if timeout update instrument instance alarm tag display path and set alarm
				if timeInState >= int(HIRESCMDTOValue):
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/MEMORY_TAGS/12/CommandSent',0)
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESCMDTO",12)
					state += 1
					timeInState = 0
					project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule HiRes",SID)
					#increment time in state tag
				else:
					timeInState += 1
		
		if state == 4:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 1)	
			system.tag.writeBlocking("PLC/RCP_DEST_ON_ENA",0) #disable receptacle valve on during sanitization to destination
			state = 0
	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
	
def nextTier(Instruments_ID,SID,step):
	pass

def checkAvail(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
		logger = system.util.getLogger("HiRes checkAvail")
		HIRESAVAILPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"HIRESAVAIL")
#		logger = system.util.getLogger("HiRes Check Avail")
#		logger.infof("Instruments_ID = %d", Instruments_ID)
#		logger.infof("HIRESAVAILPath = %s", HIRESAVAILPath)	
		if system.tag.readBlocking("HMI/SIMULATOR_MODE")[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
		else:
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking(HIRESAVAILPath)[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0: #sticky: need to add OPC tag(s)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
			else:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 0)
				TimeSinceAvail = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail")[0].value
				HIRESAVLTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"HIRESAVLTO")
#				logger.infof("TimeSinceAvail type = %s", type(TimeSinceAvail))
#				logger.infof("HIRESAVLTOValue type = %s", type(int(HIRESAVLTOValue)))
#				logger.infof("matches = %b", TimeSinceAvail == int(NLATOValue))
				if TimeSinceAvail == int(HIRESAVLTOValue):
					project.InstrumentModules.MiscFunctions.setAlarm("HIRESAVLTO",Instruments_ID)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", TimeSinceAvail + 1)

		#check if instrument is ready for handoff from upstream instrument	
		system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction")[0].value == "ready" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/PreviousFunction")[0].value == "preSample" and system.tag.readBlocking(HIRESAVAILPath)[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0
	
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction")[0].value == "ready" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/PreviousFunction")[0].value == "preSample" and system.tag.readBlocking(HIRESAVAILPath)[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 1)
		else:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 0)

	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())


def resetTags(Instrument_id,SID,step):
	pass