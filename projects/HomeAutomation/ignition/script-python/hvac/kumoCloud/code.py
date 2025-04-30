apiUrl = "https://app-prod.kumocloud.com" # main HTTP URL

# Create the JythonHttpClient.
client = system.net.httpClient()

#Secrets
USERNAME = "rayzo98008@gmail.com"
PASSWORD = "Lsloong88-"

#Variables
tpAccessToken = "[default]sensors/kumoCloud/accessToken"
tpRefreshToken = "[default]sensors/kumoCloud/refreshToken"

# All endpoints
epLogin = "/v3/login"
epRefresh = "/v3/refresh"
epAcc = "/v3/accounts/me"
epSites = "/v3/sites"
epTransferPending = "/v3/sites/transfers/pending"
epNotificationUC = "/v3/notifications/unseen-count"
epSiteInfo = "/v3/sites"
epKumoStation = "/kumo-station"
epZones = "/zones"
epGroups = "/groups"
epZoneInfo = "/v3/zones"
epDeviceInfo = "/v3/devices"
epDeviceProfile = "/profile"
epDeviceStatus = "/status"
epDeviceInitialSettings = "/initial-settings"
epDeviceKumoProp = "/kumo-properties"

# Methods
def login():
	url = apiUrl + epLogin
	headersValues =	{
		"x-app-version": "3.0.3"
		}
		
	dataValues = {
		"username": USERNAME
		, "password": PASSWORD
		, "appVersion": "3.0.3"
		}
		
	# Sent a POST request.
	response = client.post(url = url, headers=headersValues, data=dataValues)
	if response.good:
		respDataJson = response.json
		token = respDataJson['token']
		
		#record access & refresh token value
		tagPaths = [tpAccessToken, tpRefreshToken]
		values = [token['access'], token['refresh']]
		system.tag.writeBlocking(tagPaths, values)
		return respDataJson
	
	return response.json

def refreshToken():
	url = apiUrl + epRefresh
	refreshToken = system.tag.readBlocking(tpRefreshToken)[0].value #get refresh token for refresh access/refresh token
	
	headersValues =	{
		"x-app-version": "3.0.3"
		}
		
	dataValues = {
		"refresh": refreshToken
		}
		
	# Sent a POST request.
	response = client.post(url = url, headers=headersValues, data=dataValues)
	if response.good:
		respDataJson = response.json
		token = respDataJson
		
		#record access & refresh token value
		tagPaths = [tpAccessToken, tpRefreshToken]
		values = [token['access'], token['refresh']]
		system.tag.writeBlocking(tagPaths, values)
		return values
	else:
		return response.json

def getAccountInfo():
	url = apiUrl + epAcc
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}

	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json:
		return response.json
	else:
		return response.json

def getSitesInfo():
	url = apiUrl + epSites
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}
	
	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json:
		system.tag.writeBlocking("[default]sensors/kumoCloud/allSitesInfo", response.json)
		return response.json
	else:
		return response.json

def getSiteInfoSingle(siteId):
	url = apiUrl + epSiteInfo + "/%s"%siteId
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}
	
	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json:
		system.tag.writeBlocking("[default]sensors/kumoCloud/sites/00/genInfo", response.json)
		return response.json
	else:
		return response.json

def getSiteKumoStation(siteId):
	url = apiUrl + epSiteInfo + "/%s"%siteId + epKumoStation
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}
	
	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json:
		system.tag.writeBlocking("[default]sensors/kumoCloud/sites/00/kumoStation", response.json)
		return response.json
	else:
		return response.json

def getSiteZones(siteId):
	url = apiUrl + epSiteInfo + "/%s"%siteId + epZones
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}
	
	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json:
		system.tag.writeBlocking("[default]sensors/kumoCloud/sites/00/zones", response.json)
		return response.json
	else:
		return response.json

def getSiteGroups(siteId):
	url = apiUrl + epSiteInfo + "/%s"%siteId + epGroups
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}
	
	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json:
		system.tag.writeBlocking("[default]sensors/kumoCloud/sites/00/groups", response.json)
		return response.json
	else:
		return response.json

def getDeviceInfo(deviceId):
	url = apiUrl + epDeviceInfo + "/%s"%deviceId
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}
	
	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json:
		system.tag.writeBlocking("[default]sensors/kumoCloud/sites/00/devices/00/info", response.json)
		return response.json
	else:
		return response.json

def getDeviceProfile(deviceId):
	url = apiUrl + epDeviceInfo + "/%s"%deviceId + epDeviceProfile
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}
	
	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json:
		system.tag.writeBlocking("[default]sensors/kumoCloud/sites/00/devices/00/profile", response.json)
		return response.json
	else:
		return response.json

def getDeviceStatus(deviceId):
	url = apiUrl + epDeviceInfo + "/%s"%deviceId + epDeviceStatus
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}
	
	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json:
		system.tag.writeBlocking("[default]sensors/kumoCloud/sites/00/devices/00/status", response.json)
		return response.json
	else:
		return response.json

def getDeviceInitialSettings(deviceId):
	url = apiUrl + epDeviceInfo + "/%s"%deviceId + epDeviceInitialSettings
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}
	
	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json and type(response.json) == dict:
		system.tag.writeBlocking("[default]sensors/kumoCloud/sites/00/devices/00/initial-settings", response.json)
		return response.json
	elif response.json and type(response.json) == list:
		system.tag.writeBlocking("[default]sensors/kumoCloud/sites/00/devices/00/initial-settings", {"object": response.json})
		return response.json
	else:
		return response.json

def getDeviceKumoProp(deviceId):
	url = apiUrl + epDeviceInfo + "/%s"%deviceId + epDeviceKumoProp
	accessToken = system.tag.readBlocking(tpAccessToken)[0].value #get access token for getting site-info
	
	headersValues =	{
		"x-app-version": "3.0.3"
		, "Authorization": "Bearer " + accessToken
		}
	
	# Sent a GET request.
	response = client.get(url = url, headers=headersValues)
	if response.json:
		system.tag.writeBlocking("[default]sensors/kumoCloud/sites/00/devices/00/kumo-properties", response.json)
		return response.json
	else:
		return response.json