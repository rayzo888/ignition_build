def query_area(lamin, lomin, lamax, lomax):
	url = 'https://opensky-network.org/api/states/all?lamin=%d&lomin=%d&lamax=%d&lomax=%d'%(lamin, lomin, lamax, lomax)

	response = system.net.httpGet(url=url)
	return system.util.jsonDecode(response)