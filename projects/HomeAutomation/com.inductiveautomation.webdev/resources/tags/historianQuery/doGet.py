def doGet(request, session):
	startDateMillis = request['params']['startDateMillis']
	endDateMillis = request['params']['endDateMillis']
	startDate = system.date.fromMillis(startDateMillis)
	endDate = system.date.fromMillis(endDateMillis)
	paths = []
	columnNames = []
	ds = system.tag.queryTagHistory(paths=paths, startDate=startDate, endDate=endDate, aggregationMode='Average', columnNames=columnNames,ignoreBadQuality=True)
	return {'html': '<html><body>%s</body></html>'%ds}