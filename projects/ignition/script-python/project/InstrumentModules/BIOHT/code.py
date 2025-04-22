import os, sys
fileName = os.path.basename(__name__)

def preSample(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	
	try:
		state = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState")[0].value
		timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState")[0].value
		logger = system.util.getLogger("BioHT pre sample")

		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			state += 1
	
		if state == 1:
			
			#raise TypeError("BioHT test")
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
			state += 1

		#first attempt to check if in standby or sleeping and send wake up command if needed		
		if state == 2:
			if (system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value == "Standby" or system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value == "Sleeping"): 			
				socketAddress = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"BIOHTSA") #look up value
				HTTPMode = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/HTTPMode")[0].value
				myEndpoint = 'http://' + socketAddress + '/api/' + str(HTTPMode) + '/bioht/wakeup'
				try:
					jsonString = system.net.httpPost(myEndpoint, "application/json") #send wake up command
					logger.infof("BioHT wake up response: %s", jsonString)
				except:
					project.InstrumentModules.MiscFunctions.setAlarm("BIOHTHPF",Instruments_ID) #set alarm if start request fails
				state += 1
			else:
				state += 4

		#first attempt to wait for instrument to wake up
		if state == 3:
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value != "Standby" and system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value != "Sleeping": 			
				state += 3
				timeInState = 0
			else:
				timeInState += 1
			#lookup timeout setpoint
			BHTWUTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"BHTWUTO")
			if timeInState >= int(BHTWUTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("BHTWUTO",Instruments_ID)
				state += 1
				timeInState = 0
				#purposely excluded scEvent "CANCEL" here due to being followed by second attempt to wake up instrument
		
		#second attempt to check if in standby or sleeping and send wake up command if needed
		if state == 4:
			if (system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value == "Standby" or system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value == "Sleeping"): 			
				socketAddress = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"BIOHTSA") #look up value
				HTTPMode = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/HTTPMode")[0].value
				myEndpoint = 'http://' + socketAddress + '/api/' + str(HTTPMode) + '/bioht/wakeup'				
				try:
					jsonString = system.net.httpPost(myEndpoint, "application/json") #send wake up command
					logger.infof("BioHT wake up response: %s", jsonString)
				except:
					project.InstrumentModules.MiscFunctions.setAlarm("BIOHTHPF",Instruments_ID) #set alarm if start request fails
				state += 1
			else:
				state += 2

		#second attempt to wait for instrument to wake up
		if state == 5:
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value != "Standby" and system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value != "Sleeping": 			
				state += 1
				timeInState = 0
			else:
				timeInState += 1
			#lookup timeout setpoint
			BHTWUTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"BHTWUTO")
			if timeInState >= int(BHTWUTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("BHTWUTO",Instruments_ID)
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule BIOHT",SID)
		
		if state == 6:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/FunctionDone", 1)
			state = 0
		
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveState", state) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/SID", SID) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/step", step) #must be synchronous to allow write to complete before calling next function
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeInState", timeInState)
	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info()) 

def wastePosition(Instruments_ID,SID,step): #retest
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

def destinationPosition(Instruments_ID,SID,step): #retest
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
		logger = system.util.getLogger("BioHT processSample")
		
		if state == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMActive", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady", 0)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction", funcName())
			#check if there is a child before trying to pass sample
			nextStepID = system.db.runScalarQuery("SELECT Instruments_ID FROM DestinationCommands WHERE SampleCommands_id = %d AND stepNumber = %d" %(SID,step+1))
			if nextStepID == None: #sticky: need to add everywhere for end and cancel
				project.InstrumentModules.MiscFunctions.scEvent("END","From InstModule BIOHT",SID)
			state += 1
			
	
		#send start test command
		if state == 1:
			if step == 1:
				system.tag.writeBlocking("PLC/OPN_RCP_REQ",1) #open receptacle valve
			
			#send start run command to BioHT
			socketAddress = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"BIOHTSA") #look up value
			HTTPMode = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/HTTPMode")[0].value
			myEndpoint = 'http://' + socketAddress + '/api/' + HTTPMode + '/bioht/start'
			instrumentName = system.tag.readBlocking("HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/Instrument_Name")[0].value
			
			vars = ["instrumentName","testInfo"]	
			tags = ["HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/Instrument_Name","HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/testInfo"]
			

			TestInfo = system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/" + str(Instruments_ID) + "/BioHTTestInfo")[0].value
#			NumOfTests = [element.get('value', '') for element in TestInfo if element.get('name', '') == 'NumOfTests'] #removes all but NumOfTest using list comprehension 
#			TestInfo = [element for element in TestInfo if element.get('name', '') != 'NumOfTests'] #removes NumOfTest using list comprehension
#			TestInfo = ','.join(map(str, TestInfo)) #convert to string with commas
#			logger.infof("NumOfTests: %s", NumOfTests)
			logger.infof("TestInfo: %s", TestInfo)
						
			TagValues = system.tag.readBlocking(tags)
			
			conSID = project.InstrumentModules.MiscFunctions.getSampleID(SID)
			
			#look up sp #
			sql = ("select sp_number,sc_execBegan "
				"from vw_SampleCommands sc "
				"where sc_id = '%d' " %SID)
		
			SCData = system.db.runQuery(sql)
			seSP = SCData[0]['sp_number']
			sc_execBegan = SCData[0]['sc_execBegan']
			
			#expirement id
			expID = system.tag.readBlocking("HMI/SP" + str(seSP) + "/ExpmtID")[0].value

			#vessel id
			vesID = system.tag.readBlocking("HMI/SP" + str(seSP) + "/VesselID")[0].value
			
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/okToCleanLock",1) #set okToClean to 0 so we wait for the instrument.
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/okToClean",0) #set okToClean to 0 so we wait for the instrument.
			
			dict = {}
			for x in range(len(tags)):
				if dict == {}:
					dict = {vars[x]:str(TagValues[x].value)}
				else:
					dict[vars[x]] = str(TagValues[x].value)
			
#			pyDict = {"MAST_Sample_ID":str(conSID),"tests":str(TestInfo)}
#			bodyStr = '{' + '\n\t' + '\"MAST_Sample_ID\": \"' + conSID + '\",\n\t' + '\"tests\": ' + TestInfo + '\n}'
			bodyStr = '{\"MAST_Sample_ID\": \"' + conSID + '\",' + '\"tests\": ' + TestInfo + '}'
			
			logger.infof("myEndpoint: %s", myEndpoint)
			#logger.infof("pyDict: %s", pyDict)
			logger.infof("bodyStr: %s", bodyStr)
			
			try:
				jsonString = system.net.httpPost(myEndpoint, "application/json", bodyStr) #send start request
#				logger = system.util.getLogger("BioHT start run")
				logger.infof("Bioht startrun response: %s", jsonString)
			except:
				project.InstrumentModules.MiscFunctions.setAlarm("BIOHTHPF",Instruments_ID) #set alarm if start request fails
			
			state += 1

		#wait for ready to san response		
		if state == 2:
			logger.infof("state = 2")
			if system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/okToClean")[0].value == 1:
		#				if step == 1:
		#					system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve
				logger = system.util.getLogger("In If okToClean = 1") 			
				state += 1
				timeInState = 0
			else:
				system.tag.writeBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/okToCleanLock",0) #set okToClean to 0 so we wait for the instrument.
				timeInState += 1
				logger = system.util.getLogger("In else okToClean = 0")
			#lookup timeout setpoint
			BHTRTSTOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"BHTRTSTO")
			#logger = system.util.getLogger("GILSONpreSample")
			logger.infof("timeInState = %s", timeInState)
			#if timeout update instrument instance alarm tag display path and set alarm
			if timeInState >= int(BHTRTSTOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("BHTRTSTO",Instruments_ID)
				#lookup and tagpath and reset instrument tag	
				state += 1
				timeInState = 0
				project.InstrumentModules.MiscFunctions.scEvent("CANCEL","From InstModule BIOHT",SID)
		
		if state == 3:
			logger.infof("state = 3")
			iDelayToClean = 0
			iDelayToClean = system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/DelayToClean")[0].value
			timeInState = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/4/TimeInState")[0].value
			logger.infof("DelayToClean = %s", iDelayToClean)
			logger.infof("timeInState = %s", timeInState)
			
			if  timeInState > iDelayToClean:
				if step == 1:
					system.tag.writeBlocking("PLC/OPN_RCP_REQ",0) #close receptacle valve 					
				state += 1
				timeInState = 0
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

def cleanPosition(Instruments_ID,SID,step): #retest
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
	
def checkAvail(Instruments_ID,SID,step):
	import sys
	funcName = lambda n=0: sys._getframe(n + 1).f_code.co_name
	logger = system.util.getLogger("BioHT Check Avail")
	
	try:
		#dead line of code SEF 11/14/22
		#BHTRFSPath = project.InstrumentModules.MiscFunctions.lookupInstrConf("tagPath",Instruments_ID,"BHTRFS")
		
		# if BioHt running status
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value == "Standby" or system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value == "Sleeping" or (system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value == "Running" and (system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/orderStatus")[0].value == "not on board" or system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/orderStatus")[0].value == "no orders" or system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/orderStatus")[0].value == "calculated" or system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/orderStatus")[0].value == "Error not found")):
			BioHtRunning = 1
		else:
			BioHtRunning = 0
			
#		logger.infof("bioHtRunning is: %s",str(BioHtRunning))
		 
		# if DMReady AND BioHt = "running" AND not commloss AND not blocked.
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/DMReady")[0].value == 1 and BioHtRunning == 1  and system.tag.readBlocking("HMI/INSTRUMENTS/MEMORY_TAGS/4/comm_loss_alm")[0].value == 0 and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 1)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", 0)
		else:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/InstrumentAvail", 0)
			TimeSinceAvail = system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail")[0].value
			BIOHTLATOValue = project.InstrumentModules.MiscFunctions.lookupInstrConf("value",Instruments_ID,"BIOHTLATO")
#			logger.infof("TimeSinceAvail = %d", TimeSinceAvail)
#			logger.infof("BIOHTLATOValue = %d", int(BIOHTLATOValue))
#			logger.infof("matches = %b", TimeSinceAvail == int(BIOHTLATOValue))
			if TimeSinceAvail == int(BIOHTLATOValue):
				project.InstrumentModules.MiscFunctions.setAlarm("BIOHTLATO",Instruments_ID)
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/TimeSinceAvail", TimeSinceAvail + 1)

		#check if instrument is ready for handoff from upstream instrument	
		if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/ActiveFunction")[0].value == "ready" and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/PreviousFunction")[0].value == "preSample"  and system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/comm_loss_alm")[0].value == 0 and (system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/systemStatus")[0].value == "Running"  and (system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/orderStatus")[0].value == "Error not found" or system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/orderStatus")[0].value == "not on board" or system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/orderStatus")[0].value == "no orders" or system.tag.readBlocking("[]HMI/INSTRUMENTS/MEMORY_TAGS/4/orderStatus")[0].value == "calculated")) and system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/isBlocked")[0].value == 0:
			logger.infof("Setting BioHt NextTierReadyHandoff = 1")
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 1)
			
		else:
			system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(Instruments_ID) + "/NextTierReadyHandOff", 0)
			#logger.infof("Setting BioHt NextTierReadyHandoff = 0")

	except:
		project.InstrumentModules.MiscFunctions.logger(fileName,funcName(),sys.exc_info())

def resetTags(Instrument_id,SID,step):
	pass