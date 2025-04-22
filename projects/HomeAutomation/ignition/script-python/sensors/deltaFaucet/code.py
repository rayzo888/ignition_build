def getData():
	# Create the JythonHttpClient.
	client = system.net.httpClient()
	delta_device_id="426e6a39f76149249f45156186bdf8be"
	auth_token="ZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5Sm9kSFJ3T2k4dmMyTm9aVzFoY3k1NGJXeHpiMkZ3TG05eVp5OTNjeTh5TURBMUx6QTFMMmxrWlc1MGFYUjVMMk5zWVdsdGN5OXVZVzFsSWpvaVoyOXZaMnhsSWl3aWFIUjBjRG92TDNOamFHVnRZWE11ZUcxc2MyOWhjQzV2Y21jdmQzTXZNakF3TlM4d05TOXBaR1Z1ZEdsMGVTOWpiR0ZwYlhNdmJtRnRaV2xrWlc1MGFXWnBaWElpT2lJeE1EazBPVEl3T0RNMU16a3dNelV3TnpJM01UQWlMQ0pvZEhSd09pOHZjMk5vWlcxaGN5NTRiV3h6YjJGd0xtOXlaeTkzY3k4eU1EQTFMekExTDJsa1pXNTBhWFI1TDJOc1lXbHRjeTlsYldGcGJHRmtaSEpsYzNNaU9pSnlZWGw2YnprNE1EQTRRR2R0WVdsc0xtTnZiU0lzSW1GMVpDSTZJbVJsZG1salpTNWtaV3gwWVdaaGRXTmxkQzVqYjIwaUxDSmxlSEFpT2pFM01USTRPVE0wTlRJc0ltbHpjeUk2SW5SdmEyVnVMbVJsYkhSaFptRjFZMlYwTG1OdmJTSjkuaDBuSkFlWkZiZ2lQd19xajNoTUJKTjZzT0hZUlJNRENRelpfdkZOUTZUWQ=="
	url="https://device.legacy.deltafaucet.com/api/device/UsageReport"
		
	headers = {
		"Authorization": "Bearer %s"  %auth_token,
	}
	
	params = {
		"interval": 0,
	    "deviceId": delta_device_id
	}
	response=client.get(url,params=params,headers=headers)
	system_time=system.date.now()
	data= response.json
	headers=["time"]+data["retObject"]["labels"]
	values=[[system_time]+data["retObject"]["datasets"][0]["data"]]
	
	return headers, values
	
#def convertToMillis(value, unit):
#	unitToMillisMap = {
#				    name: "ounce",
#				    factor: 29.5735
#				}, {
#				    name: "ounces",
#				    factor: 29.5735
#				}, {
#				    name: "cup",
#				    factor: 236.588
#				}, {
#				    name: "cups",
#				    factor: 236.588
#				}, {
#				    name: "pint",
#				    factor: 473.176
#				}, {
#				    name: "pints",
#				    factor: 473.176
#				}, {
#				    name: "quart",
#				    factor: 946.352
#				}, {
#				    name: "quarts",
#				    factor: 946.352
#				}, {
#				    name: "gallon",
#				    factor: 3785.408
#				}, {
#				    name: "gallons",
#				    factor: 3785.408
#				}, {
#				    name: "liter",
#				    factor: 1e3
#				}, {
#				    name: "liters",
#				    factor: 1e3
#				}, {
#				    name: "centiliter",
#				    factor: 100
#				}, {
#				    name: "centiliters",
#				    factor: 100
#				}, {
#				    name: "deciliter",
#				    factor: 10
#				}, {
#				    name: "deciliters",
#				    factor: 10
#				}, {
#				    name: "milliliter",
#				    factor: 1
#				}, {
#				    name: "milliliters",
#				    factor: 1