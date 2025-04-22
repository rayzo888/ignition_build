import os, sys
fileName = os.path.basename(__name__)

def preSample(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("ViCell preSample")
#	state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
#	logger.infof("Instruments_id is: %s", Instruments_ID)
#	logger.infof("active state is %s", state)
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		logger.infof("Instruments_id is: %s", Instruments_ID)
		logger.infof("active state is %s", state)
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			#funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			instrumentName = system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/Instrument_Name")[0].value
			state += 1
			
		if state == 1:
			logger.infof(" In state 1 calling LookupInstParm")
			#look up destination command id
			sql = (
			"select Instruments_id as instrumentsId, id as destCmdId "
			"from destinationcommands dc "
			"where SampleCommands_id = %s and stepNumber = %d " %(SID,step))
			DCData = system.db.runQuery(sql)
			DestCmdID = DCData[0]['destCmdId']
					
			project.InstrumentModules.MiscFunctions.lookupInstrParm("tagParmData",Instruments_ID,DestCmdID,SID) #this script will contiue when function completes and tags are written
			app.db.saveInstrumentSettingsHistory(SID,Instruments_ID) #calls script that updates sample history with instrument settings enabled for history
			
			state += 1
			
		if state == 2:
			try:
				#request automation lock
				socketAddress = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",29,"VICELLSA") #look up value
				
				headers = {
					"User-Agent": "Mast Connect",
					"Accept": "*/*",
					"Host": socketAddress,
					"Accept-Encoding": "gzip, deflate, br",
					"Connection": "keep-alive",
				}
				
				system.net.httpPost('http://' + socketAddress + '/api/V1/vicell/requestlock', headers)
			except:
				system.tag.writeBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/StateAlarmDisplayPath",instrumentName + " HTTP post failed")
				system.tag.writeBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/StateAlarm",1)
				logger.infof("Presample request Lock failed")
				
			state += 1

		if state == 3:
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
	logger = system.util.getLogger("ViCell wastePosition")
	
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
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
		
def destinationPosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("ViCell destinationPosition")
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			#funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
					
		if state == 1:			
#		if state == 1:
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",1) #open receptacle valve
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
			
def processSample(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("ViCell processSample")
	url = ""
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			#funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			nextStepID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step+1))
			if nextStepID == None: #sticky: need to add everywhere for end and cancel
				project.InstrumentModules.MiscFunctions.scEvent("END","From InstModule CHROME",SID)
			state += 1
	
		if state == 1:
			instrumentName = system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/Instrument_Name")[0].value
			
			try:
				#start vicell sample
				socketAddress = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",29,"VICELLSA") #look up value
		
				headers = {
							"User-Agent": "Mast Connect",
							"Accept": "*/*",
							"Host": socketAddress,
							"Accept-Encoding": "gzip, deflate, br",
							"Connection": "keep-alive",
						}
				logger.infof("Headers string is: %s",headers)
				Name = str(project.InstrumentModules.MiscFunctions.getSampleID(SID))
				Dilution = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/ViCellDilute")[0].value 
				Tag = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/ViCellTag")[0].value #look up value
				CellTypeName = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) +"/ViCellCellType")[0].value #look up value
				SaveEveryNthImage = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/"+ str(Instruments_ID) + "/ViCellNthImage")[0].value #look up value
	
				postParams = {
					"Name":Name,
					"Dilution":str(Dilution),
					"Tag":Tag,
					"CellTypeName":CellTypeName,
					"QCName":"",
					"SaveEveryNthImage":str(SaveEveryNthImage),
					"Row":"ACupRow",
					"Column":"",
					"WashType":"Normal"
				}
			
				logger.infof("StartSample Parameters are: %s", postParams)
				url = "http://" + socketAddress + "/api/V1/vicell/startsample"
				logger.infof("StartSample URL is: %s",url)
			
				import urllib
				
				url += "?"
				
				for k, v in postParams.items():
					url += urllib.quote(k) + "=" + urllib.quote(v) + "&"
				url = url[:-1]	

	
				system.net.httpPost(url, headerValues=headers, contentType = "")
				state += 1
				
			except:
				logger.infof("Try for ViCell startSample failed")
				system.tag.writeBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/StateAlarmDisplayPath",instrumentName + " HTTP post failed")
				system.tag.writeBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/StateAlarm",1)
				state += 1
				
		if state == 2:
			# watch for sample acquistion to be complete on the ViCell before removing automation lock.
			status = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/Major")[0].value
			logger.infof("ViCell Major Status is: %s", status)
			if status == "ProcessingSample":
				state += 1
				timeInState = 0
			else:
				timeInState += 1
				
			#lookup timeout values					
			ViCellProcessing = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"VICELLPRO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(ViCellProcessing):
				project.InstrumentModules.MiscFunctions.setAlarm("VICELLPRO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule ViCell",SID)
							
		
		if state == 3:
			
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1) #nothing to do
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def cleanPosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("ViCell cleanPosition")

	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
		
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
			# watch for sample acquistion to be complete on the ViCell before removing automation lock.
			status = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/Minor")[0].value
#			logger.infof("ViCell Minor Status is: %s", status)
			if status == "InProcessAspirating":
				state += 1
				timeInState = 0
			else:
				timeInState += 1
				
			#lookup timeout values					
			ViCellProcessing = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"VICELLPRO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(ViCellProcessing):
				project.InstrumentModules.MiscFunctions.setAlarm("VICELLPRO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule ViCell",SID)
				
				
		if state == 2:			
			instrumentName = system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/Instrument_Name")[0].value
			try:
				#release automation lock
				socketAddress = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",29,"VICELLSA") #look up value
				
				headers = {
					"User-Agent": "Mast Connect",
					"Accept": "*/*",
					"Host": socketAddress,
					"Accept-Encoding": "gzip, deflate, br",
					"Connection": "keep-alive",
				}
				
				system.net.httpPost('http://' + socketAddress + '/api/V1/vicell/releaselock', headers)
			
			except:
				system.tag.writeBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/StateAlarmDisplayPath",instrumentName + " HTTP post failed")
				system.tag.writeBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/StateAlarm",1)
			state += 1
		
		if state == 3:
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
		
def cleanComplete(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("ViCell cleanComplete")
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			#funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1

		if state == 1:
			logger = system.util.getLogger("ViCell cleanComplete")
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
			system.tag.writeBlocking("PLC/RCP_DEST_ON_ENA",1) #enable receptacle valve on during sanitization to destination
			logger.infof("RCP_DEST_ON_ENA write executed")
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 1)
			state = 0
				
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
#		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
			
def checkAvail(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name

	try:
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0 and system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/29/Major")[0].value == "Idle":
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
		else:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 0)
			TimeSinceAvail = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail")[0].value
			VICELLLATOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"VICELLLATO")
#				logger.infof("TimeSinceAvail type = %s", type(TimeSinceAvail))
#				logger.infof("GLATOValue type = %s", type(int(OLLATOValue)))
#				logger.infof("matches = %b", TimeSinceAvail == int(OLLATOValue))
			if TimeSinceAvail == int(VICELLLATOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("VICELLLATO",Instruments_ID)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", TimeSinceAvail + 1)
		#check if instrument is ready for handoff from upstream instrument	
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction")[0].value == "ready" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/PreviousFunction")[0].value == "preSample" and system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/29/Major")[0].value == "Idle" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 1)
		else:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 0)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def resetTags(Instrument_id,SID,step):
	pass