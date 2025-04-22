import os, sys
fileName = os.path.basename(__name__)

def preSample(Instruments_ID,SID,step): 
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value

		if state == 0:
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
			state += 1
	
		if state == 2:
			import sys
			
			#look up destination command id
			sql = (
			"select Instruments_id as instrumentsId, id as destCmdId "
			"from destinationcommands dc "
			"where SampleCommands_id = %s and stepNumber = %d " %(SID,step))
			DCData = system.db.runQuery(sql)
			DestCmdID = DCData[0]['destCmdId']
						
			sql = (
				"select ipv.value "
				"from InstrumentParameter_Lookup ipl "
				"join InstrumentParameterValues ipv on ipv.InstrumentParameter_Lookup_id = ipl.id "
				"where ipv.DestinationCommands_id = '%d' and ipl.code = 'FIALABUPLCCal' " %DestCmdID)
			DCData = system.db.runQuery(sql)
			fialabCal = DCData[0]['value']
							
			if fialabCal == "false": 
				sql = ("select sp_number "
					"from vw_SampleCommands sc "
					"where sc_id = '%d' " %SID)
			
				seSP = system.db.runScalarQuery(sql)
				
				#declare global vars
				DilutionValue = ""
				expID = ""
				TiterValue = ""
				
				#write dilution SP value
				DilutionValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"DILUTIONSP" + str(seSP))
				project.InstrumentModules.MiscFunctions.updateInstrConf(DilutionValue,"FIADF",Instruments_ID,SID) #read or write value to db and write to instrument tag
				project.InstrumentModules.MiscFunctions.updateInstrConf(DilutionValue,"UPLCDV",Instruments_ID,SID) #read or write value to db and write to instrument tag
				
				#write ECCF SP value				
				UPLCECCFVValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"ECCFSP" + str(seSP))
				project.InstrumentModules.MiscFunctions.updateInstrConf(UPLCECCFVValue,"UPLCECCFV",Instruments_ID,SID) #read or write value to db and write to instrument tag				
				
				#expirement id
				expID = system.tag.readBlocking("HMI/SP" + str(seSP) + "/ExpmtID")[0].value
				project.InstrumentModules.MiscFunctions.updateInstrConf(expID,"FIAEXPID",Instruments_ID,SID) #read or write value to db and write to instrument tag		
				project.InstrumentModules.MiscFunctions.updateInstrConf(expID,"UPLCEXPID",Instruments_ID,SID) #read or write value to db and write to instrument tag		
				
				#titer
				TiterValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"TITERSETSP" + str(seSP))
				project.InstrumentModules.MiscFunctions.updateInstrConf(TiterValue,"FIATV",Instruments_ID,SID) #read or write value to db and write to instrument tag
				project.InstrumentModules.MiscFunctions.updateInstrConf(str(seSP),"UPLCTVFSP",Instruments_ID,SID) #read or write value to db and write to instrument tag
	
			else: #fialabCal = True
				#write dilution value of 1
				DilutionValue = 1
				project.InstrumentModules.MiscFunctions.updateInstrConf(DilutionValue,"FIADF",Instruments_ID,SID) #read or write value to db and write to instrument tag
				project.InstrumentModules.MiscFunctions.updateInstrConf(DilutionValue,"UPLCDV",Instruments_ID,SID) #read or write value to db and write to instrument tag
				
				#write ECCF Level value
				UPLCLVLPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"UPLCLVL")
				UPLCLVLValue = system.tag.readBlocking(UPLCLVLPath)[0].value
				ECCFLVLValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"ECCFLEVEL" + UPLCLVLValue)
				project.InstrumentModules.MiscFunctions.updateInstrConf(ECCFLVLValue,"UPLCECCFV",Instruments_ID,SID) #read or write value to db and write to instrument tag
				
				#write null expirement id
				expID = " "
				project.InstrumentModules.MiscFunctions.updateInstrConf(expID,"FIAEXPID",Instruments_ID,SID) #read or write value to db and write to instrument tag
				project.InstrumentModules.MiscFunctions.updateInstrConf(expID,"UPLCEXPID",Instruments_ID,SID) #read or write value to db and write to instrument tag
					
				#write null titer
				project.InstrumentModules.MiscFunctions.updateInstrConf("","FIATV",Instruments_ID,SID) #read or write value to db and write to instrument tag
				project.InstrumentModules.MiscFunctions.updateInstrConf("","UPLCTVFSP",Instruments_ID,SID) #read or write value to db and write to instrument tag

			#sample id
			conSID = project.InstrumentModules.MiscFunctions.getSampleID(SID)
			project.InstrumentModules.MiscFunctions.updateInstrConf(conSID,"FIASID",Instruments_ID,SID) #read or write value to db and write to instrument tag
			project.InstrumentModules.MiscFunctions.updateInstrConf(conSID,"UPLCSID",Instruments_ID,SID) #read or write value to db and write to instrument tag
				
			app.db.saveInstrumentSettingsHistory(SID,Instruments_ID) #calls script that updates sample history with instrument settings enabled for history
			
			#fialab sample type
#			FIALABUPLCFSTValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"FIALABUPLCFST" + FIALABUPLCFSTValue)
			FIALABUPLCFSTValue = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/13/FialabSampleType")[0].value 
			
			#send prepare
			#build json string and write to TCP message tag
#			vars = ["sample_type","titer_value","calibration"]	
#			tags = ["HMI/INSTRUMENTS/MEMORY_TAGS/13/FialabSampleType","HMI/INSTRUMENTS/MEMORY_TAGS/13/FialabTiterValue","HMI/INSTRUMENTS/MEMORY_TAGS/13/FialabCalibration"]
			
#			dict = {}
#			TagValues = system.tag.readBlocking(tags)
#			for x in range(len(tags)):
#				if dict == {}:
#					dict = {vars[x]:str(TagValues[x].value)}
#				else:
#					dict[vars[x]] = str(TagValues[x].value)
			string = {'destination':'fialab','message_type':'prepare','sample_prep':{'sample_type':FIALABUPLCFSTValue,'titer_value':TiterValue,'calibration':fialabCal,'sample_id':conSID,'experiment_id':expID}}
			jsonString = system.util.jsonEncode(string) + "\r\n"
			system.tag.writeBlocking("HMI/Instruments/TCP_TAGS/13/Writable",jsonString)
									
			state += 1
		
		if state == 3:

			FIAMRPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"FIAMR")
			if system.tag.readBlocking(FIAMRPath)[0].value == 1:
				system.tag.writeBlocking(FIAMRPath,0)
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			FIAMRTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"FIAMRTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(FIAMRTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("FIAMRTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule FIALABUPLC",SID)
			#increment time in state tag
			else:
				timeInState += 1
		
		if state == 4:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			#project.InstrumentModules.MiscFunctions.tagWriteDiag("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone",1)
			state = 0

		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)

	except:
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

	try:
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
			#send readygo
			
			#build json string and write to TCP message tag
			string = {'destination':'fialab','message_type':'readygo'}
			jsonString = system.util.jsonEncode(string) + "\r\n"
			system.tag.writeBlocking("HMI/Instruments/TCP_TAGS/13/Writable",jsonString)
			
			#reset message received tag
			FIAMRPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"FIAMR")
			system.tag.writeBlocking(FIAMRPath,0)
			
			
			#send start run command to UPLC
			socketAddress = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"UPLCSA") #look up value
			HTTPMode = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/HTTPMode")[0].value
			myEndpoint = 'http://' + socketAddress + '/api/' + HTTPMode + '/uplcato/start'
			instrumentName = system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/Instrument_Name")[0].value
			
			vars = ["WatersSampleSetMethod","WatersSampleID","WatersExperimentID","WatersLevel","WatersSampleType","WatersECCFValue","WatersDilutionValue"]
			tags = ["HMI/INSTRUMENTS/MEMORY_TAGS/13/WatersSampleSetMethod","HMI/INSTRUMENTS/MEMORY_TAGS/13/WatersSampleID","HMI/INSTRUMENTS/MEMORY_TAGS/13/WatersExperimentID","HMI/INSTRUMENTS/MEMORY_TAGS/13/WatersLevel","HMI/INSTRUMENTS/MEMORY_TAGS/13/WatersSampleType","HMI/INSTRUMENTS/MEMORY_TAGS/13/WatersECCFValue","HMI/INSTRUMENTS/MEMORY_TAGS/13/WatersDilutionValue"]
			
			TagValues = system.tag.readBlocking(tags)
			
			conSID = project.InstrumentModules.MiscFunctions.getSampleID(SID)

			#look up sp #
			sql = ("select sp_number,sc_execBegan "
				"from vw_SampleCommands sc "
				"where sc_id = '%d' " %SID)
			
			SCData = system.db.runQuery(sql)
			seSP = SCData[0]['sp_number']
			sc_execBegan = SCData[0]['sc_execBegan']

			#vessel id
			vesID = system.tag.readBlocking("HMI/SP" + str(seSP) + "/VesselID")[0].value
			
			dict = {}
			for x in range(len(tags)):
				if dict == {}:
					dict = {vars[x]:str(TagValues[x].value)}
				else:
					dict[vars[x]] = str(TagValues[x].value)
			
			pyDict = {"MAST_Sample_ID":dict['WatersSampleID'],"MAST_Experiment_ID":dict['WatersExperimentID'],"MAST_Vessel_ID":str(vesID),"MAST_Start_Time":str(sc_execBegan),"MAST_Sample_Type":dict['WatersSampleType'],"MAST_Sample_Set_Method":dict['WatersSampleSetMethod'],"MAST_Level":dict['WatersLevel'],"MAST_Dilution":dict['WatersDilutionValue'],"MAST_ECCF":dict['WatersECCFValue'],"MAST_Titer_Value_For_SP":seSP}

																										

#			logger.infof("myEndpoint: %s", myEndpoint)
#			logger.infof("pyDict: %s", pyDict)
			
			try:
				logger = system.util.getLogger("Waters start run")
				logger.infof("myEndpoint: %s", myEndpoint)
				logger.infof("pyDict: %s", pyDict)
				jsonString = system.net.httpPost(myEndpoint, "application/json",pyDict) #send start request
				pyDict = system.util.jsonDecode(jsonString)
				result = pyDict.get('result')
#				logger.infof("Waters startrun response: %s", result)
			except:
				project.InstrumentModules.MiscFunctions.setAlarm("UPLCHPF",Instruments_ID) #set alarm if start request fails
				project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
			state += 1

		if state == 2:
			#wait for fialab message received
			#logger.info("state2")
			FIAMRPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"FIAMR")
			if system.tag.readBlocking(FIAMRPath)[0].value == 1:
				system.tag.writeBlocking(FIAMRPath,0)
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			FIAMRTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"FIAMRTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(FIAMRTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("FIAMRTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule FIALABWaters",SID)
			#increment time in state tag
			else:
				timeInState += 1
		
		if state == 3:	
			#wait for fialab busy processing
			FIASTATPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"FIASTAT")
			if system.tag.readBlocking(FIASTATPath)[0].value == "busy_processing_sample":
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			FIABPSTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"FIABPSTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(FIABPSTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("FIABPSTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule FIALABWaters",SID)
			#increment time in state tag
			else:
				timeInState += 1

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
		logger = system.util.getLogger("FIALAB checkAvail")
		
		UPLCMJSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"UPLCMJS")
#		WatersCLAPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"WatersCLA")
		FIASTATPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"FIASTAT")

		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking(FIASTATPath)[0].value == "ready" and system.tag.readBlocking(UPLCMJSPath)[0].value == "System Idle" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:

			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
		else:
			if system.tag.readBlocking(FIASTATPath)[0].value != "Requesting" and system.tag.readBlocking(UPLCMJSPath)[0].value != "Requesting":
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 0)
				TimeSinceAvail = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail")[0].value
				FIALATOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"FIALATO")
				if TimeSinceAvail == int(FIALATOValue):
					project.InstrumentModules.MiscFunctions.setAlarm("FIALATO",Instruments_ID)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", TimeSinceAvail + 1)
				
		#check if instrument is ready for handoff from upstream instrument	
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction")[0].value == "ready" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/PreviousFunction")[0].value == "preSample" and system.tag.readBlocking(UPLCMJSPath)[0].value == "System Idle" and system.tag.readBlocking(FIASTATPath)[0].value == "ready" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			#logger.info("ran")
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 1)
		else:
			if system.tag.readBlocking(FIASTATPath)[0].value != "Requesting" and system.tag.readBlocking(UPLCMJSPath)[0].value != "Requesting":
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 0)
		
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def resetTags(Instrument_id,SID,step):
	pass