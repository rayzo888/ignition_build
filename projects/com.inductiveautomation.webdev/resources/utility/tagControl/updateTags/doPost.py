def doPost(request, session):
	tagFileFolder = request['postData']['tagFileFolder']
	res = utility.tagControl.updateTagFromFile(tagFileFolder)
	return {'response': res}