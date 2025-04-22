def doGet(request, session):
	tagFileFolder = request['params']['tagFileFolder']
	tagProvider = request['params']['tagProvider']
	res = utility.tagControl.exportTag(tagFileFolder, tagProvider)
	return {'response': res}