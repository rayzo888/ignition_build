import os, sys
fileName = os.path.basename(__name__)

def preSample(Instruments_ID,SID,step): 
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name

	try:
		#raise TypeError("test") #used to create a test exception
		
		logger = system.util.getLogger("Gilson preSample")

		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
				
#			nextStepID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step+1))
			childID = system.db.runScalarQuery("SELECT childInstruments_id FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step))
			#check for child instrument and initialized nextTier
			if childID != None: #Child instrument found
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierPending", 1)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStepUpdated",0)
				project.InstrumentModules.GILSON.nextTier(Instruments_ID,SID,step,step + 1) #call this instruments nextTier function
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStepUpdated",0)
			else:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStep",-1)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStepUpdated",2)
			state += 1
	#		logger.infof("state = %d", state)
		
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
#			logger.info("Line after Gilson parms")
	#		logger.infof("state = %d", state)
			
			GDSSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSS")
			system.tag.writeBlocking(GDSSPath, 0) #reset
			#project.InstrumentModules.MiscFunctions.tagWriteDiag(GDSSPath,0)
			
			sql = ("select startStep "
				"from sampleCommandData scd "
				"join SampleCommands sc on sc.SampleCommandData_id = scd.id "
				"where sc.id = '%d' " %SID)
		
			seStartStep = system.db.runScalarQuery(sql)
#			logger.infof("seStartStep = %d", seStartStep)
			
			#write sample ID to Gilson
			conSID = project.InstrumentModules.MiscFunctions.getSampleID(SID)
			system.tag.writeBlocking("PLC/GDS_SAMPLE_ID", conSID)
			
			#write experiment ID to Gilson
			if seStartStep == 0:			
				sql = ("select sp_number "
					"from vw_SampleCommands sc "
					"where sc_id = '%d' " %SID)
			
				seSP = system.db.runScalarQuery(sql) #look up current SP#
				expID = system.tag.readBlocking("HMI/SP" + str(seSP) + "/ExpmtID")[0].value #look up experiment id for current SP#
				project.InstrumentModules.MiscFunctions.updateInstrConf(expID,"GEXPID",Instruments_ID,SID) #read or write value to db and write to instrument tag		
			else:
				project.InstrumentModules.MiscFunctions.updateInstrConf("NULL","GEXPID",Instruments_ID,SID) #read or write value to db and write to instrument tag
#			logger.infof("SID = %d", SID)
#			logger.infof("Instruments_ID = %d", Instruments_ID)
			#app.db.saveInstrumentSettingsHistory(SID,Instruments_ID) #calls script that updates sample history with instrument settings enabled for history
			
			childID = system.db.runScalarQuery("SELECT childInstruments_id FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step))
			#write port number to Gilson
			if childID != None: #Child instrument found
				sql = ("select Destinations_number "
					"from DestinationCommands dc "
					"where dc.SampleCommands_id = '%d' and stepNumber = '%d' " %(SID,step))
				
				Destinations_number = system.db.runScalarQuery(sql)
				
		
				sql = ("select dc.y "
					"from DestinationConfiguration dc "
					"where dc.Destinations_number = '%d' and instruments_id = '%d' " %(Destinations_number,childID))
				
				portNumber = system.db.runScalarQuery(sql)
			
				if portNumber > 0 and portNumber < 5:
					#system.tag.writeBlocking(GPORTNPath, portNumber)
					project.InstrumentModules.MiscFunctions.updateInstrConf(portNumber,"GPORTN",Instruments_ID,SID) #read or write value to db and write to instrument tag
			else:
				#system.tag.writeBlocking(GPORTNPath, 0)
				project.InstrumentModules.MiscFunctions.updateInstrConf("0","GPORTN",Instruments_ID,SID) #read or write value to db and write to instrument tag
			
			#Search upstream steps of destination command for any CRS instrument types and write sample type to Gilson
			#XCEL if comes from CRS. WCEL for all other samples. Null for deck sample.
			if seStartStep == 1:
				sampleType = "DECK"
			else:
				sql = ("select dc.stepNumber, dc.instrumentType "
					"from  DestinationCommands dc "
					"where dc.SampleCommands_id = '%d' " %SID)
				
				dcChainDataSet = system.db.runQuery(sql)
				
				sampleType = "None"
				if step == 1:
					sampleType = "WCEL"
				else:
					for row in range(step - 1):
					   #print dcChainDataSet[row]["instrumentType"]
					   if dcChainDataSet[row]["instrumentType"] in "CRS":
						sampleType = "XCEL"
					   else:
						sampleType = "WCEL"			
			project.InstrumentModules.MiscFunctions.updateInstrConf(sampleType,"GSMPLT",Instruments_ID,SID) #read or write value to db and write to instrument tag
			state += 1

		if state == 2:
			#wait for GSI then respond with sample info
			GGSIPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GGSI")
		
			if system.tag.readBlocking(GGSIPath)[0].value == 1:
				GDSSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSS")
				system.tag.writeBlocking(GDSSPath, 2)
				timeInState = 0
				state += 1
			else:
				timeInState += 1
			#lookup timeout values					
			GGSITOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GGSITO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(GGSITOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GGSITO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)

		if state == 3:
			#wait for GSI response received
			GGSIPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GGSI")
		
			if system.tag.readBlocking(GGSIPath)[0].value == 0:
				timeInState = 0
				state += 1
			else:
				timeInState += 1
			#lookup timeout values					
			GGSIRTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GGSIRTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(GGSIRTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GGSIRTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)
					
		if state == 4:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			
			sql = ("select startStep "
				"from sampleCommandData scd "
				"join SampleCommands sc on sc.SampleCommandData_id = scd.id "
				"where sc.id = '%d' " %SID)
			
			#if this is a Gilson deck sample then set instrument module active/ready tags
			seStartStep = system.db.runScalarQuery(sql)
			if seStartStep == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 0)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 1)
				GDSSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSS")
				system.tag.writeBlocking(GDSSPath, 0)
			
			state = 0
	#		logger.infof("state = %d", state)


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
		logger = system.util.getLogger("Gilson wastePosition")
		
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
						
			#set simulator tags based on GDS_STATE
			if system.tag.readBlocking("PLC/GDS_STATE")[0].value == 0:
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_GSI_IND",1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_DSP_IND",0)
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_RNS_IND",0)
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_SLN_IND",0)
			if system.tag.readBlocking("PLC/GDS_STATE")[0].value == 5:
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_SLN_IND",0)
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_RNS_IND",1)
		
		if state == 1:
			#wait for WSR
			GWSRPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GWSR")
			if system.tag.readBlocking(GWSRPath)[0].value == 1:
				GDSSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSS")
				timeInState = 0
				state += 1
			else:
				timeInState += 1
			#lookup timeout values					
			GWSRTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GWSRTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(GWSRTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GWSRTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)

		if state == 2:
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",1) #open receptacle valve
			state += 1
			
		if state == 3:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0

		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def destinationPosition(Instruments_ID,SID,step): #sticky: need to add in action for ERR gears command
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name

	try:
		logger = system.util.getLogger("Gilson destinationPosition")
		
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
	
		if state == 1:
			#Send waste done move to destination
			GDSSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSS")
			system.tag.writeBlocking(GDSSPath, 4) #WSR, Done
			#logger = system.util.getLogger("Gilson destinationPosition state 1")
			#project.InstrumentModules.MiscFunctions.tagWriteDiag(GDSSPath,2)
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_GSI_IND",0) #set simulator tag
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_DSP_IND",1) #set simulator tag
			state += 1
			
		if state == 2:
			#wait for Gilson dispense command
			GDSPPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSP")
			if system.tag.readBlocking(GDSPPath)[0].value == 1:
				GDSSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSS")
				#project.InstrumentModules.MiscFunctions.tagWriteDiag(GDSSPath,3)
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			GDSPTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GDSPTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(GDSPTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GDSPTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)
			
		if state == 3:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
	
def processSample(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name

	try:
		logger = system.util.getLogger("Gilson processSample")
		
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
		
		if state == 0:
			timeInState = 0
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			#check if there is a child before trying to pass sample
			childID = system.db.runScalarQuery("SELECT childInstruments_id FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step))
			if childID == None: #sticky: need to add everywhere for end and cancel
				project.InstrumentModules.MiscFunctions.scEvent("END","From InstModule Gilson",SID)
			state += 1
	
		if state == 1:
			system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
			state += 1
			
		if state == 2:
			#Inform Gilson that sample delivery is complete
			GDSSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSS")
			system.tag.writeBlocking(GDSSPath, 5) #DSP, Done
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_DSP_IND",0) #set simulator tag
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_SLN_IND",1) #set simulator tag
			state += 1
	
		if state == 3:
			#wait for sample location code
			GSLNPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GSLN")
			if system.tag.readBlocking(GSLNPath)[0].value == 1:
				GDSSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSS")
				system.tag.writeBlocking(GDSSPath, 6) #prepare for RNS command
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			GSLNTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GSLNTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(GSLNTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GSLNTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)
		
		if state == 4:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			#system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(Instruments_ID) + '/ActiveFunction',"ready")
			state = 0

		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	except:
		import sys
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def cleanPosition(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name

	try:
		logger = system.util.getLogger("Gilson cleanPosition")
		
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
	
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
						
			#set simulator tags based on GDS_STATE
			if system.tag.readBlocking("PLC/GDS_STATE")[0].value == 0:
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_GSI_IND",1)
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_DSP_IND",0)
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_RNS_IND",0)
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_SLN_IND",0)
			if system.tag.readBlocking("PLC/GDS_STATE")[0].value == 5:
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_SLN_IND",0)
				system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_RNS_IND",1)
		
		if state == 1:
			#wait for rinse command
			GRNSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GRNS")
		
			if system.tag.readBlocking(GRNSPath)[0].value == 1:
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			GRNSTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GRNSTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(GRNSTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GRNSTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)

		if state == 2:
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",1) #open receptacle valve
			state += 1
			
		if state == 3:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0

		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def nextTier(Instruments_ID,SID,step,ChildStep):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierTimeInState")[0].value
		
		logger = system.util.getLogger("Gilson nextTier")
#		logger.info("Log test")

			
		#state 0
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStep", ChildStep)
			state += 1
	
		#state : call preSample
		if state == 1:
			sql = ("SELECT stepNumber, childInstruments_ID, childStepNumber "
				"FROM DestinationCommands "
#				"WHERE SampleCommands_id = %d and stepNumber >= (select stepNumber from DestinationCommands where Instruments_id = 9 and SampleCommands_id = %d) "
				"WHERE SampleCommands_id = %d and childInstruments_id is not Null and stepNumber >= (select stepNumber from DestinationCommands where Instruments_id = 9 and SampleCommands_id = %d) "
				%(SID,SID))
			children = system.db.runQuery(sql)
			if children.rowCount != 0:
				allInPreSample = 1
				for child in range(children.rowCount):
					childID = children.getValueAt(child,"childInstruments_ID")
					ChildStep = children.getValueAt(child,"childstepNumber")
					if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "standby":
						seDestType = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/Instrument_Type")[0].value
						logger.infof("childID = %d", childID)
						logger.infof("SID = %d", SID)
						logger.infof("ChildStep preSample = %d", ChildStep)
						project.InstrumentModules.MiscFunctions.funcDict(seDestType + "preSample",childID,SID,ChildStep)
					if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value != "preSample":
						allInPreSample = 0
				if allInPreSample == 1:
					state += 1
				else: #no child instrument found
					state = 0	
		
		#confirm preSample done
		if state == 2:
			sql = ("SELECT stepNumber, childInstruments_ID, childStepNumber "
					"FROM DestinationCommands "
					"WHERE SampleCommands_id = %d and childInstruments_id is not Null and stepNumber >= (select stepNumber from DestinationCommands where Instruments_id = 9 and SampleCommands_id = %d) "
					%(SID,SID))
			children = system.db.runQuery(sql)
			allPreSampleDone = 1
			for child in range(children.rowCount):
				childID = children.getValueAt(child,"childInstruments_ID")
						#	childID = children.getValueAt(child,"Instruments_ID")			
						#	print "childID:",childID
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
					system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
					system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"ready")
#					print "functionDone: ", str(childID)
				else:
					allPreSampleDone = 0
			if allPreSampleDone == 1:
				state += 1
		
		if state == 3:
			#ChildStep tag event script writes 1 to ChildStepUpdated.  This state waits for ChildStepUpdated = 1 then writes 2 to indicate tag changes has been detected which the
			#checkAvail script monitors for when it can reply to TRQ.  This also gates the state machine execution to wait for valid ChildStep value before proceeding. 
			ChildStepUpdated = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStepUpdated")[0].value
			if  ChildStepUpdated == 1: #indicates tag has changed
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStepUpdated",2) #indicates this gate has checked it.
		#		system.tag.writeBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/ReadyForTRQ",1)
				state += 1
				timeInState = 0
			else:
				timeInState += 1
			#lookup timeout values					
			GCSUTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GCSUTO")
			if timeInState >= int(GCSUTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GCSUTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)
		
		#wait for TRW
		if state == 4:
			GTRWPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRW")
#			GTRPSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRPS")

			if system.tag.readBlocking(GTRWPath)[0].value == 1:
#				system.tag.writeBlocking(GTRPSPath, 1) #TRW, done
				state += 1
				timeInState = 0
			else:
				timeInState += 1
			#lookup timeout values					
			GTRWTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GTRWTO")
			if timeInState >= int(GTRWTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GTRWTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)
	
		#call wastePosition
		if state == 5:
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
			
		#confirm wastePosition done
		if state == 6:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"ready")
				GTRPSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRPS")
				system.tag.writeBlocking(GTRPSPath, 1) #TRW, done
				state += 1

		#wait for TRD
		if state == 7:
			GTRDPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRD")
#			GTRPSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRPS")
			if system.tag.readBlocking(GTRDPath)[0].value == 1:
#				system.tag.writeBlocking(GTRPSPath, 2) #TRD, done
				state += 1
				timeInState = 0
			else:
				timeInState += 1
			#lookup timeout values					
			GTRDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GTRDTO")
			if timeInState >= int(GTRDTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GTRDTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)
							
		#call destinationPosition
		if state == 8:
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
					
		#confirm destinationPosition done
		if state == 9:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"ready")
				GTRPSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRPS")
				system.tag.writeBlocking(GTRPSPath, 2) #TRD, done
				state += 1
		
		#wait for TRP
		if state == 10:
			GTRTPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRT")
			if system.tag.readBlocking(GTRTPath)[0].value == 1:
				state += 1
				timeInState = 0
			else:
				timeInState += 1
			#lookup timeout values					
			GTRTTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GTRTTO")
			if timeInState >= int(GTRTTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GTRTTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)
							
		#call processSample
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
	
		#confirm processSample done
		if state == 12:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"ready")
				GTRPSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRPS")
				system.tag.writeBlocking(GTRPSPath, 3) #TRT, done
				state += 1

		#wait for TRC
		if state == 13:
			GTRCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRC")
			if system.tag.readBlocking(GTRCPath)[0].value == 1:
				state += 1
				timeInState = 0
			else:
				timeInState += 1
			#lookup timeout values					
			GTRCTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GTRCTO")
			if timeInState >= int(GTRCTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GTRCTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)

		#call cleanPosition
		if state == 14:
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
			
		#confirm cleanPosition done
		if state == 15:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"ready")
				GTRPSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRPS")
				system.tag.writeBlocking(GTRPSPath, 4) #TRC, done
				state += 1

		#wait for TCD
		if state == 16:
			GTCDPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTCD")
			if system.tag.readBlocking(GTCDPath)[0].value == 1:
#				GTRPSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRPS")
#				system.tag.writeBlocking(GTRPSPath, 5) #TCD, Ack
				state += 1
				timeInState = 0
			else:
				timeInState += 1
			#lookup timeout values					
			GTCDTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GTCDTO")
			if timeInState >= int(GTCDTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GTCDTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)
	
		#call cleanComplete
		if state == 17:
			#check if there is a child instrument
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			#logger.infof("nextStepID = %d", nextStepID)
			if childID != None:
				#if child instrument is available call cleanComplete
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "ready":
					seDestType = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/Instrument_Type")[0].value
					project.InstrumentModules.MiscFunctions.funcDict(seDestType + "cleanComplete",childID,SID,ChildStep)
				if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/ActiveFunction")[0].value == "cleanComplete":
					state += 1
			else: #no child instrument found
				state = 0

		#confirm cleanComplete done
		if state == 18:
			childID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone")[0].value == 1:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/FunctionDone", 0)
				system.tag.writeBlocking('[]HMI/INSTRUMENTS/FUNC_TAGS/' + str(childID) + '/ActiveFunction',"standby")
#				#check if there is a child instrument
				childID = system.db.runScalarQuery("SELECT childInstruments_id FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,ChildStep))
#				logger.infof("state 17 childID/ChildStep: %d/%d", (childID,ChildStep))
				if childID != None: #Child instrument found
#					logger.infof("ChildStep var: %d", ChildStep)
					system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStep", ChildStep + 1) #increment NextStep tag

				else:
					system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStep", -1) #reset NextStep tag

				GTRPSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRPS")
				system.tag.writeBlocking(GTRPSPath, 5) #TCD, Ack
				
				state += 1

		if state == 19: #maybe update this to send "WAIT" if TRQ received
			#wait for response to TCD received (this should be TRQ checking for any more ports)
			#wait for TCD indicator false
#			logger.info("Gilson nextTier state 18 entered")
			GTCDPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTCD")
			if system.tag.readBlocking(GTCDPath)[0].value == 0:
				GTRPSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRPS")
				system.tag.writeBlocking(GTRPSPath, 0) #standby
#				logger.info("GTRPSPath = 0 tagwrite")
				state += 1
				timeInState = 0
			else:
				timeInState += 1
			#lookup timeout values					
			GTCDRTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GTCDRTO")
			if timeInState >= int(GTCDRTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GTCDRTO",Instruments_ID)
				state += 1
				timeInState = 0
#				logger.info("Gilson nextTier state 18 timed out")
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)

		if state == 20:
			#wait for ChildStepUpdated true then reset to false to.  Keeps state machine here until update complete
			ChildStepUpdated = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStepUpdated")[0].value
#			logger.infof("ChildStepUpdated step 20: %d", ChildStepUpdated)

			if  ChildStepUpdated == 1: #indicates tag has changed

#					system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStepUpdated",3) #indicates this gate has checked it.
#				else:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStepUpdated",2) #indicates this gate has checked it.
				ChildStep = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStep")[0].value #update runtime variable
#				system.tag.writeBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/ReadyForTRQ",1)
				state += 1
				timeInState = 0
			else:
				timeInState += 1
			#lookup timeout values					
			GCSUTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GCSUTO")
			if timeInState >= int(GCSUTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GCSUTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)			
		
		if state == 21:
#			logger.infof("ChildStep step 21: %d", ChildStep)
			ChildStepRead = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStep")[0].value
#			logger.infof("ChildStepRead step 21: %d", ChildStepRead)
			if ChildStepRead != -1: #Child instrument found
				state = 4 #Loop through again with next step
			else: #No Child instrument found
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierActive", 0)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReady", 1)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierPending", 0)
				system.tag.writeBlocking("PLC/GDS_TRQ_AVAIL","WAIT,0") #reset tag at end of sample

#				GTRPSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRPS")
#				system.tag.writeBlocking(GTRPSPath, 0) #TCD, reset (should this be set to 6 here)
				state = 0
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierTimeInState", timeInState)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def cleanComplete(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name

	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
		
		logger = system.util.getLogger("Reset")
			
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
		
		if state == 1:
			GDSCPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSC")
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_RNS_IND",0) #set simulator tag
			GDSSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSS")			
			system.tag.writeBlocking(GDSSPath, 7) #RNS, Done
			state += 1
		
		if state == 2:
			#wait for Response to RNS received
			#wait for rinse command indicator false
			GRNSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GRNS")
			if system.tag.readBlocking(GRNSPath)[0].value == 0:
				state += 1
				timeInState = 0
			#increment time in state tag
			else:
				timeInState += 1
			#lookup timeout values					
			GRNSRTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GRNSRTO")
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(GRNSRTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("GRNSRTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule GILSON",SID)
		
		if state == 3:
			GDSSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GDSS")
			system.tag.writeBlocking(GDSSPath, 0)
			#project.InstrumentModules.MiscFunctions.tagWriteDiag(GDSSPath,0)
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_SLN_IND",0) #set simulator tag
			system.tag.writeBlocking("HMI/INSTRUMENTS/OPC_TAGS/9/Simulator/GCMD_GSI_IND",1) #set simulator tag
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
			state += 1

		#this state added for testing injects a delay to make clean complete take longer
#		if state == 4:
#			if timeInState > 280:
#				state += 1
#				timeInState = 0
#			else:
#				timeInState += 1	
	
		if state == 4:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 1)
			state = 0
	
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
	
def checkAvail(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("Gilson checkAvail")
	
	try:

		GGSIPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GGSI") #GSI indicator
		GCLAPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GCLA") #comm alarm
	
		if system.tag.readBlocking("HMI/SIMULATOR_MODE")[0].value == 1:
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
			else:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 0)
		else:
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReady")[0].value == 1 and system.tag.readBlocking(GGSIPath)[0].value == 1 and system.tag.readBlocking(GCLAPath)[0].value == 0 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
				if system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail")[0].value == 0:
					system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
					system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
			else:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 0)
				TimeSinceAvail = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail")[0].value
				GLATOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"GLATO")
#				logger.infof("TimeSinceAvail type = %s", type(TimeSinceAvail))
#				logger.infof("GLATOValue type = %s", type(GLATOValue))
#				logger.infof("Instruments_ID = %d", Instruments_ID)
#				logger.infof("GLATOValue = %s", GLATOValue)
#				logger.infof("matches = %b", TimeSinceAvail == GLATOValue)
				if TimeSinceAvail == GLATOValue:
					project.InstrumentModules.MiscFunctions.setAlarm("GLATO",Instruments_ID)
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", TimeSinceAvail + 1)
						
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierActive")[0].value == 1:
			childID = system.db.runScalarQuery("SELECT childInstruments_id FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step))
			#logger.infof("nextStepID = %s", nextStepID)
			if childID != None: #Child instrument found
				#logger.info("TesttesT")
				childStep = system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStep")[0].value #sticky: how does childStep get reset back to 1
				project.InstrumentModules.GILSON.nextTier(Instruments_ID,SID,step,childStep) #call this instruments nextTier function

		#check if This instrument is ready for handoff from upstream instrument	
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction")[0].value == "ready" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/PreviousFunction")[0].value == "preSample" and system.tag.readBlocking(GCLAPath)[0].value == 0 and system.tag.readBlocking(GGSIPath)[0].value == 1 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 1)
		else:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 0)
		
		## TRQ check if downstream instrument available
		GTRQGETPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"GTRQGET")		
		if system.tag.readBlocking(GTRQGETPath)[0].value == "GET":
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStepUpdated")[0].value == 2: #2 indicates gate has checked that tag updated				
		#				TRQTrue = 0
				childID = -1
				childStep = system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ChildStep")[0].value
				
				logger.infof("TRQ Gilson ChildStepis: %s",str(childStep))		
				if childStep != -1:
					sql = ("SELECT dcmd.Destinations_Number, stepNumber,dcmd.Instruments_id,dcnfg.y "
						"FROM DestinationCommands dcmd "
						"JOIN DestinationConfiguration dcnfg on dcnfg.Instruments_id = dcmd.Instruments_id "
						"WHERE SampleCommands_id = %d and stepNumber = %d " %(SID,childStep))
					destCmd = system.db.runQuery(sql)
		
					portNumber = destCmd.getValueAt(0,"y")
					childID = destCmd.getValueAt(0,"Instruments_id")
					logger.info("Checking Next Tier Ready Handoff")
					logger.infof("TRT Port Number = %d", portNumber)
					logger.infof("TRT ChildID = %d", childID)
					tempNextTier = system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/NextTierReadyHandOff")[0].value
					logger.infof("Next Tier Ready Handoff of Child Inst is: %s", tempNextTier)
					if system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(childID) + "/NextTierReadyHandOff")[0].value == 1:
						logger.infof("Setting GDS_TRQ_AVAIL to TRUE, %d", portNumber)
						system.tag.writeBlocking("[]PLC/GDS_TRQ_AVAIL", "TRUE" + "," + str(portNumber))
					else:			
						logger.infof("Setting GDS_TRQ_AVAIL to FALSE, %d", portNumber)
						system.tag.writeBlocking("[]PLC/GDS_TRQ_AVAIL", "FALSE,0")
				else:			
		#				if TRQTrue == 0:
					logger.info("TRQ ChildStep is -1")
					system.tag.writeBlocking("[]PLC/GDS_TRQ_AVAIL", "FALSE,0")
					logger.infof("childStep currrentValue: %d", childStep)

	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())
	
def resetTags(Instrument_id,SID,step):
	system.tag.writeBlocking('PLC/GDS_STATE', 0) #sticky: temporary in case sample is cleared so gilson doesn't get stuck.  Find a better more modular way to do this for any instruments that need to be reset
	system.tag.writeBlocking('PLC/TRP_STATE', 0) #sticky: cannot use writeSynchronous here because it is called from a gui button.  Investigate possible issues from not using writeSynchronous
	system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instrument_id) + "/NextTierPending", 0)
	system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instrument_id) + "/ChildStep", -2)
	system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instrument_id) + "/ChildStepUpdated", 0)
	system.tag.writeBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instrument_id) + "/ReadyForTRQ", 0)