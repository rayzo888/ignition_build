def getData():
	headers = {
	    'homeboy-app-platform': 'android',
	    'homeboy-app-version': '4.0.12',
	    'homeboy-app-platform-version': '12',
	    'homeboy-app-id': 'afc41e9816b1f0d7',
	    'homeboy-app-brand': 'google',
	    'homeboy-app-device': 'sdk_gphone64_x86_64',
	    'cache-control': 'max-age=0',
	    'homeboy-app': 'com.kidde.android.monitor1',
	    'user-agent': 'com.kidde.android.monitor1/4.0.12',
	    'homeboy-auth': 'de63d27099d9a2ecfd5711701eac0a70aa73bed8',
	    'content-type': 'application/json; charset=UTF-8',
	}
	
	json_data = {
	    'email': 'rayzo98008@gmail.com',
	    'password': '12345Wawdlp!',
	    'timezone': 'America/New_York',
	}
	username=json_data['email']
	password=json_data['password']
	
	response = system.net.httpGet(url="https://api.homesafe.kidde.com/api/v4/location/341315/device", username=username, password=password, headerValues=headers)
	return response