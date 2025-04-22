import os, sys
fileName = os.path.basename(__name__)

#logger = system.util.getLogger("CRS")
#logger.infof("dir: %s", os.path.basename(__name__))
#logger.infof("dir: %s", dir(os.path.basename))
#logger.infof("dir: %s", dir())
#logger.infof("dir: %s", os.path.basename(__call__))
#logger.infof("dir: %s", dir(os.path.basename))

def preSample(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
		
		logger = system.util.getLogger("preSample")
		#logger.info("started")
		
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			childID = system.db.runScalarQuery("SELECT childInstruments_id FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step))
			#check for child instrument and initialized nextTier
			if childID != None: #Child instrument found
				project.InstrumentModules.CRS.nextTier(Instruments_ID,SID,step,step + 1) #call this instruments nextTier function
			state += 1
	#		logger.infof("state = %d", state)

		if state == 1:
			
			#look up destination command id
#			logger.infof("SID = %d", SID)
#			logger.infof("step = %d", step)
			sql = (
			"select Instruments_id as instrumentsId, id as destCmdId "
			"from destinationcommands dc "
			"where SampleCommands_id = %s and stepNumber = %d " %(SID,step))
			DCData = system.db.runQuery(sql)
			DestCmdID = DCData[0]['destCmdId']
			
			#query and write instrument parameters
			project.InstrumentModules.MiscFunctions.lookupInstrParm("tagParmData",Instruments_ID,DestCmdID,SID) #this script will contiue when function completes and tags are written
			app.db.saveInstrumentSettingsHistory(SID,Instruments_ID) #calls script that updates sample history with instrument settings enabled for history
			state += 1
	#		logger.infof("state = %d", state)
		
		if state == 2:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
	#		logger.infof("state = %d", state)
	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
		
def wastePosition(Instruments_ID,SID,step): #sticky: need to add in action for ERR gears command
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
#		logger = system.util.getLogger("wastePositionLogger")
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
		
		if state == 1:
			CRSAVPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSAV")
			if system.tag.readBlocking(CRSAVPath)[0].value == 1: #CRS is Available so this is pre sample
				#Send CRS code 40 PendSmpl command
				CRSPESPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSPES")
				system.tag.writeBlocking(CRSPESPath, 0)
				CRSPESPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSPES")
				system.tag.writeBlocking(CRSPESPath, 1)
				state = 2
			else: #CRS is not available so this is post sample
				state = 3
		#raise TypeError("test")
	
		if state == 2:
			#wait for CRS code 43 active
			CRSC43APath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSC43A")
			if system.tag.readBlocking(CRSC43APath)[0].value == 1:
				CRSPESPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSPES")
				system.tag.writeBlocking(CRSPESPath, 0) #reset CRS code 40 PendSmpl command
				state = 4
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			CRSC43ATOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"CRSC43ATO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(CRSC43ATOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("CRSC43ATO",Instruments_ID)
				CRSPESPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSPES")
				system.tag.writeBlocking(CRSPESPath, 0) #reset CRS code 40 PendSmpl command
				state = 4
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule CRS",SID)

		if state == 3:
			state = 4 #nothing to do, CRS code 42 recevied during processSample
			
		if state == 4:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
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

	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value

		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			#check if there is a child before trying to pass sample
			childID = system.db.runScalarQuery("SELECT childInstruments_id FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step))
			if childID == None: #sticky: need to add everywhere for end and cancel
				project.InstrumentModules.MiscFunctions.scEvent("END","From InstModule CRS",SID)
			state += 1
	
		if state == 1:
			#Send CRS code 43 PrepSmpl command
			CRSPRSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSPRS")
			system.tag.writeBlocking(CRSPRSPath, 0)
			CRSPRSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSPRS")
			system.tag.writeBlocking(CRSPRSPath, 1)
			state += 1
			
		if state == 2:
			#wait for CRS code 49 sample received
			CRSC49APath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSC49A")
			if system.tag.readBlocking(CRSC49APath)[0].value == 1:
				CRSPRSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSPRS")
				system.tag.writeBlocking(CRSPRSPath, 0) #reset CRS code 43 PrepSmpl command
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			CRSC49ATOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"CRSC49ATO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(CRSC49ATOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("CRSC49ATO",Instruments_ID)
				CRSPRSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSPRS")
				system.tag.writeBlocking(CRSPRSPath, 0) #reset CRS code 43 PrepSmpl command
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule CRS",SID)
			
		if state == 3:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def cleanPosition(Instruments_ID,SID,step): #sticky: need to add in action for ERR gears command
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
#		logger = system.util.getLogger("wastePositionLogger")
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
		
		if state == 1:
			#wait for CRS code 42 ready for dest san
			CRSC42APath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSC42A")
			if system.tag.readBlocking(CRSC42APath)[0].value == 1:
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			CRSC42ATOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"CRSC42ATO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(CRSC42ATOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("CRSC42ATO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule CRS",SID)
			
		if state == 2:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
				
def nextTier(Instruments_ID,SID,step,ChildStep):
	import time
	#start = time.time()
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name	
	
	try:
		logger = system.util.getLogger("CRSnextTier")
#		logger.infof("Instruments_ID = %d", Instruments_ID)
#		logger.infof("SID = %d", SID)
#		logger.infof("step = %d", step)
		
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierTimeInState")[0].value
				
		#state 0
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReady", 0)	
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStep", ChildStep)
			state += 1
				
		#state 1: call preSample
		if state == 1:
			#check if there is a child instrument
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if childID != None:
				#if child instrument is available call preSample sticky: need timeouts incase function doesn't start
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "standby":
					seDestType = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/Instrument_Type")[0].value
					logger = system.util.getLogger("CRSnextTier state 1")
#					logger.infof("called = %s", seDestType)
					project.InstrumentModules.MiscFunctions.funcDict(seDestType + "preSample",childID,SID,ChildStep)
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "preSample":
					state += 1
			else: #no child instrument found
				state = 0
	
		#state 2 confirm preSample done
		if state == 2:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
#			logger.infof("nextStepID = %d", nextStepID)
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
#				logger.infof("Functiondone = %d", nextStepID)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"ready")
				state += 1
		
		#state 3: call wastePosition
		if state == 3:
			#check if there is a child instrument
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if childID != None:
				#if child instrument is available call wastePosition
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "ready":
					seDestType = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/Instrument_Type")[0].value
					project.InstrumentModules.MiscFunctions.funcDict(seDestType + "wastePosition",childID,SID,ChildStep)
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "wastePosition":
					state += 1
			else: #no child instrument found
				state = 0
			
		#state 4: confirm wastePosition done
		if state == 4:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"ready")
				state += 1
	
		#state 5: dispense waste to child
		if state == 5:
			#Send CRS code 44 waste to child command
			CRSDSWPPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDSWP")	#PLC/CRS1/ProcSmpl
			system.tag.writeBlocking(CRSDSWPPath, 0)
			CRSDSWPPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDSWP")	#PLC/CRS1/ProcSmpl
			system.tag.writeBlocking(CRSDSWPPath, 1)
			state += 1
		
		#state 6: #wait for CRS to be ready for destination position
		if state == 6:
			#wait for CRS code 45 active ready for destination position
			CRSDSWCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDSWC")	#PLC/CRS1/Code45CellFreeToGilson
			if system.tag.readBlocking(CRSDSWCPath)[0].value == 1:
				CRSDSWPPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDSWP")	#PLC/CRS1/ProcSmpl
				system.tag.writeBlocking(CRSDSWPPath, 0)
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			CRSDSWCTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"CRSDSWCTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(CRSDSWCTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("CRSDSWCTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule CRS",SID)	
		
		#state 7: call destinationPosition
		if state == 7:
			#check if there is a child instrument
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if childID != None:
				#if child instrument is available call destinationPosition
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "ready":
					seDestType = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/Instrument_Type")[0].value
					project.InstrumentModules.MiscFunctions.funcDict(seDestType + "destinationPosition",childID,SID,ChildStep)
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "destinationPosition":
					state += 1
			else: #no child instrument found
				state = 0
					
		#state 8: confirm destinationPosition done
		if state == 8:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"ready")
				state += 1
		
		#state 9: dispense sample to child
		if state == 9:
			#Send CRS code 45 dispense to child command
			CRSDTCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDTC")	#PLC/CRS1/Code45DispCmpt
			system.tag.writeBlocking(CRSDTCPath, 0)
			CRSDTCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDTC")	#PLC/CRS1/Code45DispCmpt
			system.tag.writeBlocking(CRSDTCPath, 1)
			state += 1

		#state 10: confirm sample dispensed to child
		if state == 10:
			#wait for CRS code 46 DispCmpt
			CRSDTCCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDTCC")	#PLC/CRS1/Code46DisCmplt
			if system.tag.readBlocking(CRSDTCCPath)[0].value == 1:
				CRSDTCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDTC")
				system.tag.writeBlocking(CRSDTCPath, 0) #reset
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			CRSDTCCTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"CRSDTCCTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(CRSDTCCTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("CRSDTCCTO",Instruments_ID)
				CRSDTCCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDTCC")
				system.tag.writeBlocking(CRSDTCCPath, 0) #reset
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule CRS",SID)		
	
		#state 11: call processSample
		if state == 11:
			#check if there is a child instrument
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if childID != None:
				#if child instrument is available call destinationPosition
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "ready":
					seDestType = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/Instrument_Type")[0].value
					project.InstrumentModules.MiscFunctions.funcDict(seDestType + "processSample",childID,SID,ChildStep)
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "processSample":
					state += 1
			else: #no child instrument found
				state = 0
			
		#state 12: confirm processSample done
		if state == 12:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"ready")
				state += 1
	
		#state 13: call cleanPosition
		if state == 13:
			#check if there is a child instrument
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if childID != None:
				#if child instrument is available call cleanPosition
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "ready":
					seDestType = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/Instrument_Type")[0].value
					project.InstrumentModules.MiscFunctions.funcDict(seDestType + "cleanPosition",childID,SID,ChildStep)
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "cleanPosition":
					state += 1
			else: #no child instrument found
				state = 0
			
		#state 14: confirm cleanPosition done
		if state == 14:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"ready")
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 0) #sticky: need error handeling to reset this if stuck
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 1)
				state += 1

		#state 15: dispense waste to child
		if state == 15:
			#Send CRS code 47 dispense waste to child command
			CRSDWTCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDWTC")	#PLC/CRS1/CRS47ClnRdy
			system.tag.writeBlocking(CRSDWTCPath, 0)
			CRSDWTCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDWTC")	#PLC/CRS1/CRS47ClnRdy
			system.tag.writeBlocking(CRSDWTCPath, 1)
			state += 1
		
		#state 16: confirm waste dispensed to child
		if state == 16:
			#wait for CRS code 60 ClnCmpt
			CRSCCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSCC") #PLC/CRS_PRODUCED/CRS60ClnCmpt
			if system.tag.readBlocking(CRSCCPath)[0].value == 1:
				CRSDWTCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDWTC")
				system.tag.writeBlocking(CRSDWTCPath, 0) #reset
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			CRSCCTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"CRSCCTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(CRSCCTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("CRSCCTO",Instruments_ID)
				CRSDWTCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"CRSDWTC")
				system.tag.writeBlocking(CRSDWTCPath, 0) #reset
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule CRS",SID)
	
		#state 17: call cleanComplete
		if state == 17:
			#check if there is a child instrument
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if childID != None:
				#if child instrument is available call wastePosition
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "ready":
					seDestType = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/Instrument_Type")[0].value
					project.InstrumentModules.MiscFunctions.funcDict(seDestType + "cleanComplete",childID,SID,ChildStep)
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "cleanComplete":
					state += 1
			else: #no child instrument found
				state = 0
			
		#state 18: confirm cleanComplete done
		if state == 18:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(nextStepID) + "/DMActive", 0)
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(nextStepID) + "/DMReady", 1)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"standby")
				logger.infof("state18 childID = %d", childID)

				#check if there is a child instrument
#				nextStepID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step+1))
#				nextNextStepID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step+2))
#				if nextNextStepID == None:
#					system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(nextStepID) + '/ActiveFunction',"ready") #sticky: needs testing
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 0) #sticky: need error handeling to reset this if stuck
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 1)
##				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(nextStepID) + "/DMActive", 0) #sticky: need error handeling to reset this if stuck
##				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(nextStepID) + "/DMReady", 1)
				state += 1

		#state 19
		if state == 19:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierActive", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReady", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierPending", 0)
			state = 0
	
		#sticky: need to add reset call
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierTimeInState", timeInState)
		#end = time.time()
			#system.tag.writeBlocking("HMI/INSTRUMENTS/FUNC_TAGS/0 Time", end - start)
		
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
				
def cleanComplete(Instruments_ID,SID,step): #sticky: need to update all reset functions like this except CRS
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
		
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		startNextTier = 0

		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
		
		if state == 1:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			system.tag.writeBlocking("PLC/RCP_DEST_ON_ENA",0) #disable receptacle valve on during sanitization to destination
			startNextTier = 1
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 0) #sticky: need error handeling to reset this if stuck
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 1)		
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		
		#call next tier function
#		if startNextTier == 1:
#			#check if there is a child before trying to pass sample
#			nextStepID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step+1))
#			if nextStepID != None:
#				project.InstrumentModules.CRS.nextTier(Instruments_ID,SID,step) #call this instruments nextTier function
#			else:
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 0) #sticky: need error handeling to reset this if stuck
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 1)
		
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
		
def checkAvail(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
		#raise TypeError("CRS test")
		logger = system.util.getLogger("CRS Check Avail")
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking("CRS_PLC/CRS_PRODUCED/Avail")[0].value == 1 and system.tag.readBlocking("[]PLC/CRS_ALM")[0].value == 0 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReady")[0].value == 1:
			if system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail")[0].value == 0:
#				nextStepID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step+1))
#				if nextStepID == None: #Child instrument not found
#					project.InstrumentModules.MiscFunctions.scEvent("END","From InstModule CRS",SID)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
		else:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 0)
			TimeSinceAvail = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail")[0].value
			CRSLATOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"CRSLATO")
			if TimeSinceAvail == int(CRSLATOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("CRSLATO",Instruments_ID)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", TimeSinceAvail + 1)
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierActive")[0].value == 1:
			childID = system.db.runScalarQuery("SELECT childInstruments_id FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step))
			#logger.infof("nextStepID = %s", nextStepID)
			if childID != None: #Child instrument found
					#.info("TesttesT")
				childID = system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStep")[0].value
				project.InstrumentModules.CRS.nextTier(Instruments_ID,SID,step,childID) #call this instruments nextTier function

		#check if instrument is ready for handoff from upstream instrument	
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction")[0].value == "ready" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/PreviousFunction")[0].value == "preSample" and system.tag.readBlocking("[]PLC/CRS_CONSUMED/Avail")[0].value == 1 and system.tag.readBlocking("[]PLC/CRS_ALM")[0].value == 0 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 1)
		else:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 0)

	except:
		#logger = system.util.getLogger("IMTimer")
		#logger.info("TesttesT")
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
	
def resetTags(Instrument_id,SID,step):
	system.tag.writeBlocking('CRS_PLC/CRS1/PrepSmpl',0)
	system.tag.writeBlocking('CRS_PLC/CRS1/ProcSmpl',0)
#	system.tag.writeBlocking('CRS_SU_PLC/CRSSU/PendSmpl',0)
	system.tag.writeBlocking('CRS_PLC/CRS1/PendSmpl',0)
	system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instrument_id) + "/NextTierPending", 0)
	system.tag.writeBlocking('CRS_PLC/CRS1/CRS47ClnRdy',0)
	system.tag.writeBlocking('CRS_PLC/CRS1/Code45DispCmpt',0)
			