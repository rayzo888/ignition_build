'''
This scripts consist methods related to tags.
'''

def formatTags(content):
	'''
	This methods takes contents of dict as top level and inspect each values to find out if it is dict or arrays.
	Return a format that tags can be used to write blocking
	'''
	formatTagList = []
	# Format the tag configuration
	for item in content.keys():
		itemType = g_script.probeScript.typeCheckForTagConfig(content[item])
			
		if itemType in ['array', 'dict']:
			# Check if it is array
			if itemType == 'array':
				for idx in range(len(content[item])):
					tagvalue = content[item][idx]
					formatTagList.append({'%s/%d'%(item,idx):tagvalue})
			# Check if it is dict
			elif itemType == 'dict':
				for item1 in content[item].keys():
					itemType1 = g_script.probeScript.typeCheckForTagConfig(content[item][item1])
					tagvalue = content[item][item1]
					formatTagList.append({'%s/%s'%(item,item1):tagvalue})
		elif itemType not in ['array', 'dict']:
			tagvalue = content[item]
			formatTagList.append({item:tagvalue})
	return formatTagList
	
def browseTag(tagPath):
	'''
	This methods browse contents of certain tag path and return what's inside.
	Return a pathlist of all the contents for that certain tag, in one list.
	'''
	retPaths = system.tag.browse(tagPath)
	pathList = []
	for path in retPaths:
		if path['hasChildren']:
			pathList += browseTag(str(path['fullPath']))
		else:
			pathList.append(str(path['fullPath']))
	return pathList

def browseHistoricalTags(path):
	'''
	This methods browse contents of certain tag path and return what's inside. (historical tagpaths only)
	Return a pathlist of all the contents for that certain tag, in one list.
	'''
	histPaths = []
	for result in system.tag.browseHistoricalTags(path).getResults():
		if result.hasChildren():
			histPaths += browseHistoricalTags(result.getPath())
		else:
			histPaths.append(result.getPath())
	return histPaths

def formatToWritableList(rootPath, returnData, browsedTagPath):
	'''
	This methods return path and values formatted for system.tag.writeBlocking functions
	'''
	writePathList = []
	writeValueList = []
	
	for itemData in returnData:
		if (rootPath + '/' + itemData.keys()[0]) in browsedTagPath:
			writePathList.append((rootPath + '/' + itemData.keys()[0]))	
			writeValueList.append(itemData.values()[0])
			
	return writePathList , writeValueList