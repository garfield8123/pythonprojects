def gettemperature(location):
	longitude, latitude = getlocation(location)
	import openmeteo_requests

	import requests_cache
	from retry_requests import retry

	# Setup the Open-Meteo API client with cache and retry on error
	cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
	retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
	openmeteo = openmeteo_requests.Client(session = retry_session)

	# Make sure all required weather variables are listed here
	# The order of variables in hourly or daily is important to assign them correctly below
	url = "https://api.open-meteo.com/v1/forecast"
	params = {
		"latitude": latitude,
		"longitude": longitude,
		"hourly": "temperature_2m",
		"current": "temperature_2m",
		"start_date": "2026-03-14",
		"end_date": "2026-03-28",
	}
	responses = openmeteo.weather_api(url, params = params)

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]
	#print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")

	# Process current data. The order of variables needs to be the same as requested.
	current = response.Current()
	current_temperature_2m = (current.Variables(0).Value() *1.8) + 32
	if current_temperature_2m < 80:
		return "Open Window Current temperature: " + str(int(current_temperature_2m))
	else:
		return "Close Window Current temperature: " + str(int(current_temperature_2m))

def getlocation(location):
	from geopy.geocoders import Nominatim
	geolocator = Nominatim(user_agent="python geopy")
	location = geolocator.geocode(location)
	return location.longitude,location.latitude

if __name__ == "__main__":
	print(gettemperature("1448 Freeman lane"))