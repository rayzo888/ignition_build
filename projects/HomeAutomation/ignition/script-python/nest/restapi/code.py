projectUrl = "https://smartdevicemanagement.googleapis.com/v1/enterprises/a56fcd55-db15-4d7e-8bd0-48f3bee215c4"
accessToken = "ya29.a0AeDClZBN3wopp8wQN1fozFVuFarlGnzGetIqR4WTZIDaoWwHPKroYVut6P3CH1m-3U4rrp8BBIBlzccuh-AIHvGuD5ftOxJ9d5iGsPN3W_pX13rSgqUwNOkvePGCDNR2BfmBcuZXXSQ6OmmCP022OnJHWQxaPhPXogy2eZv7aCgYKAWYSARASFQHGX2MiEbu7ThowSX1SWWXlZkgk5Q0175"

def getStructure():

	url = projectUrl + "/structures"
	data = {
		'Content-Type': 'application/json'
		, 'Authorization': 'Bearer %s'%accessToken
		}
	httpClient = system.net.httpClient()
	response = httpClient.get(url = url, headers = data)
	
	return response.json
	
def getDevices():

	url = projectUrl + "/devices"
	data = {
		'Content-Type': 'application/json'
		, 'Authorization': 'Bearer %s'%accessToken
		}
	httpClient = system.net.httpClient()
	response = httpClient.get(url = url, headers = data)
	
	return response.json