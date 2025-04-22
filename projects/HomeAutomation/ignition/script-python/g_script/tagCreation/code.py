def configure(rootPath, value):
	'''
	This method mainly to create tags related to kidde sensors based on its API calls...
	'''
	# Define a base path to be used to write at.
	parentPath = rootPath
	
	# Initialize the configuration for system.tag.configure
	tagConfig = {}
	collisionPolicy = 'o'
	tagConfigList = []
	
	# Format the tag configuration
	for item in value.keys():
		itemType = g_script.probeScript.typeCheckForTagConfig(value[item])
		name = item
		
		if itemType in ['array', 'dict']:
			tagConfig["dataType"] = None
			tagConfig["tagType"] = 'Folder'
			tagConfig["name"] = name
			
			# Check if it is array
			if itemType == 'array':
				tagConfig['tags'] = []
				for idx in range(len(value[item])):
					itemType1 = g_script.probeScript.typeCheckForTagConfig(value[item][idx])
					name1 = value[item][idx]
					tagConfig['tags'].append({
										"dataType" :itemType1,
										"tagType" : 'AtomicTag',
										"name" : idx,
										"valueSource" : 'memory',
										"value": name1
										})
			# Check if it is dict
			elif itemType == 'dict':
				tagConfig['tags']=[]
				for item1 in value[item].keys():
					itemType1 = g_script.probeScript.typeCheckForTagConfig(value[item][item1])
					name1 = item1
					
					tagConfig['tags'].append({
										"dataType" :itemType1,
										"tagType" : 'AtomicTag',
										"name" : name1,
										"valueSource" : 'memory',
										"value": value[item][item1]
										})			
		elif itemType not in ['array', 'dict']:
			tagConfig["dataType"] = itemType
			tagConfig["tagType"] = 'AtomicTag'
			tagConfig["name"] = name
			tagConfig["valueSource"] = 'memory'
			tagConfig["value"] = value[item]
		
		tagConfigList.append(tagConfig)
		tagConfig = {}
	
	response = system.tag.configure(parentPath, tagConfigList, collisionPolicy)
	return response