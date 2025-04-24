def updateTagFromFile(tagFileFolder):
	'''
	Completely changed tagProvider based on the filename of files listed at tagFileFolder. 
	(eg, if in the folder, you have default.json & RemoteMast.json, it will completely change default tagProvider and RemoteMast tagProvider to match the json file.
	
    Args:
	    tagFileFolder (str): 
	    	The path to the file that hold the exported tags.

    Returns: 
		str: filepath of where the file stored at.
	'''
	import os
	tagProviders = []
	# get tagProvider using filename list from file folder.
	for item in os.listdir(tagFileFolder):
		filename, extension = os.path.splitext(item)
		tagProviders.append(filename)
	
	#Perform the specified update on identified tagProvider.
	if len(tagProviders) > 0:
		for tagProvider in tagProviders:
			print('deleting tagProvider: [%s]...'%tagProvider)
			deleteTag(tagProvider)
			print('importing tagProvider: [%s]...'%tagProvider)
			importTag(tagFileFolder, tagProvider)
	res = 'Completed'
	return res

def exportTag(tagFileFolder, tagProvider):
	'''
	Exports tags to a file on the local file system.
	
    Args:
	    tagFileFolder (str): 
	    	The path to the file that hold the exported tags.
		tagProvider (str): 
			tagProvider to export from. Only allow one tagProvider at a time and exported file reflected to tagProvider name inputted. For example, if tagProvider is default, exported fileName is default.json.

    Returns: 
		str: filepath of where the file stored at.
	'''
	tagProviderStr = tagProvider if isinstance(tagProvider, str) else "%s"%(tagProvider)
	tagPath = "[" + tagProviderStr + "]"
	filePath = tagFileFolder + "/" +  tagProviderStr + ".json"
	tagPaths = [tagPath]
	res = system.tag.exportTags(filePath, tagPaths, recursive = True, exportType = 'json')
	return res

def importTag(tagFileFolder, tagProvider):
	'''
	Import tags from a file to tagProvider specified.
	
    Args:
	    tagFileFolder (str): 
	    	The path to the file that hold the exported tags.
		tagProvider (str): 
			tagProvider to import from. Only allow one tagProvider at a time.

    Returns: 
		list: results of the tags per tagpath that are imported.
	'''
	tagProviderStr = tagProvider if isinstance(tagProvider, str) else ord(tagProvider)
	tagPath = "[" + tagProviderStr + "]"
	filePath = tagFileFolder + "/" +  tagProviderStr + ".json"
	basePath = tagPath
	collisionPolicy = 'o' #only use overwrite
	res = system.tag.importTags(filePath, basePath, collisionPolicy)
	return res
	
def deleteTag(tagProvider):
	'''
	Delete tags in the tagProvider.
	
    Args:
		tagProvider (str): 
			tagProvider to delete.
	
    Returns
    	list: results of the tags per tagpath that are deleted.
	'''
	tagPaths = browseTag(tagProvider)
	res = system.tag.deleteTags(tagPaths)
	return res
	
def browseTag(tagProvider, recursive = False):
	'''
	Browse tags from tagProvider.
	
    Args:
		tagProvider (str): 
			tagProvider to browse from. Only allow tagFileFolder, one tagProvider at a time.

    Returns
    	list: tagpaths
	'''
	tagProviderStr = tagProvider if isinstance(tagProvider, str) else ord(tagProvider) #change to string
	tagPath = "[" + tagProviderStr + "]"
	returnedPaths = system.tag.browse(path = tagPath, filter = {"recursive": recursive})
	res = []
	
	#Extract the tag's fullpath from browsed tag list.
	for item in returnedPaths.getResults():
		tagPathString = item['fullPath'].toString()
		UDTTagPathString = '%s_types_'%tagPath
		if UDTTagPathString in tagPathString:
			res = res + [item['fullPath'].toString() for item in system.tag.browse(path = UDTTagPathString, filter = {"recursive": recursive}).getResults()]
		else:
			res.append(tagPathString)
	return res
	
	
	
	
	