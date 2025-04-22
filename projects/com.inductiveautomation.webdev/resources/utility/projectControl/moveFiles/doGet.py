def doGet(request, session):
	project = request['params']['project']
	dstFolder = request['params']['dstFolder']
#	return {'response': 'hello-world'}	
#	project="MAST_Connect"
#	dstFolder="C:\Users\sadm-X276512\Documents\MAST\SourceCode\sandbox\projects"
	res = utility.projectControl.moveProjectFiles(project, dstFolder)
	return {'response': res}