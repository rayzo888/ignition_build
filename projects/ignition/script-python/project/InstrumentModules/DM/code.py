def preSample(level,destFolder):
	pass

def wastePosition(destPath):
	pass

def destinationPosition(destPath):
	pass
	
def processSample(destPath):
	pass	

def cleanPosition(destPath):
	pass	
	
def cleanComplete():
	pass

def nextTier():
	pass
	
def checkAvail(instrumentInstance,SID,step):
	if system.tag.readBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(instrumentInstance) + "/DMReady")[0].value == 1:
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(instrumentInstance) + "/InstrumentAvail", 1)
	else:
		system.tag.writeBlocking("[]HMI/INSTRUMENTS/FUNC_TAGS/" + str(instrumentInstance) + "/InstrumentAvail", 0)

def resetTags(Instrument_id,SID,step):
	pass