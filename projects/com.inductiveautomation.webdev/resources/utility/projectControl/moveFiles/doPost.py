def doPost(request, session):
	project = request['postData']['project']
	dstFolder = request['postData']['dstFolder']
	res = utility.projectControl.moveProjectFiles(project, dstFolder)
	return {'response': res}