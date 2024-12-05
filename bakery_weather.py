"""
Bakery Helper Library - Weather Requests
Version: 0.0.4
Author: acbart@udel.edu

Changelog:
* 10/28/2022 at 3:21pm - Initial version finished
* 10/28/2022 at 3:49pm - Fixed misordered forecast fields, renamed image url field
* 10/30/2022 at 12:44pm - Fixed missing attributes for WeatherReport
* 10/30/2022 at 2:00pm - Rename cache file
"""

from dataclasses import dataclass
import requests

try:
    import requests_cache
    requests_cache.install_cache('bakery_cache')
except ImportError:
    print("Warning! Please install requests-cache using the Tools menu (Manage Packages)")

@dataclass
class ReportLocation:
    """
    Metadata about the location of a given weather report.

    Attributes:
        latitude: The latitude (up-down) of this location.
        longitude: The longitude (left-right) of this location.
        elevation: The height above sea-level (in feet).
        name: The city and state that this location is in.
    """
    latitude: float
    longitude: float
    elevation: int
    name: str
    
@dataclass
class WeatherData:
    """
    The current weather information, which is more extensive than
    what can be forecasted.
    
    Attributes:
        temperature: The current temperature (in Fahrenheit).
        dewpoint: The current dewpoint temperature (in Fahrenheit).
        humidity: The current relative humidity (as the whole number part of a percentage).
        wind_speed: The current wind speed (in miles-per-hour).
        wind_direction: The current wind direction (in degrees).
        description: A human-readable description of the current weather.
        url: A url pointing to a picture that describes the weather.
        visibility: How far you can see (in miles).
        wind_chill: The perceived temperature (in Fahrenheit).
        pressure: The barometric pressure (in inches).
    """
    temperature: int
    dewpoint: int
    humidity: int
    wind_speed: int
    wind_direction: int
    description: str
    url: str
    visibility: float
    wind_chill: int
    pressure: float
    
@dataclass
class Forecast:
    """
    The weather predictions for a given time period.
    
    Attributes:
        when: A human-readable name for this time period (e.g. Tonight or Saturday).
        is_high: Whether or not the predicted temperature is a daily high (True) or a daily low (False).
        temperature: The predicted temperature for this period (in Fahrenheit).
        precipitation: The probability of precipitation for this period (as the whole number part of a percentage).
        url: A url pointing to a picture that describes the predicted weather for this period.
        status: A human-readable description of the predicted weather for this period.
        description: A more-detailed, human-readable description of the predicted weather for this period.
    """
    when: str
    is_high: bool
    temperature: int
    precipitation: int
    url: str
    status: str
    description: str

@dataclass
class WeatherReport:
    """
    Main actual weather report class that contains the location of the result,
    the current weather, and the forecasted weather.
    
    Attributes:
        location: Metadata about the location this forecast comes from.
        current: The current weather data for this location.
        forecast: A list of future, predicted weather data.
    """
    location: ReportLocation
    current: WeatherData
    forecast: list[Forecast]
    
def get_weather(latitude: float, longitude: float) -> WeatherReport:
    """
    For a given latitude and longitude in the United States, retrieve the
    latest weather report.
    """
    request_arguments = dict(lat=latitude, lon=longitude, FcstType="json")
    r = requests.get("http://forecast.weather.gov/MapClick.php", request_arguments,
                     headers={'User-Agent': 'Bakery Weather library for educational purposes'})
    return create_report(r.json(), latitude, longitude)


#############################################################################
# Helper Functions

def create_report(raw: dict, latitude: float, longitude: float) -> WeatherReport:
    """
    Create a weather report from the raw dictionary data previously retrieved.
    """
    if 'time' not in raw:
        raise ValueError("Fields are unexpectedly missing from the response returned by the server. "
                         "Check your latitude and longitude, make sure it is in the United States!\n"
                         f" Latitude={latitude}, Longitude={longitude}")
    raw_location = raw.get('location', {})
    raw_current = raw.get('currentobservation', {})
    return WeatherReport(
        ReportLocation(parse_float(raw_location.get('latitude')),
                       parse_float(raw_location.get('longitude')),
                       parse_float(raw_location.get('elevation')),
                       raw_location.get('areaDescription', 'Unknown location')),
        WeatherData(parse_int(raw_current.get('Temp')),
                       parse_int(raw_current.get('Dewp')),
                       parse_int(raw_current.get('Relh')),
                       parse_int(raw_current.get('Winds')),
                       parse_int(raw_current.get('Windd')),
                       raw_current.get('Weather', ''),
                       "https://forecast.weather.gov/newimages/medium/"+raw_current.get('Weatherimage', ''),
                       parse_float(raw_current.get('Visibility')),
                       parse_int(raw_current.get('WindChill')),
                       parse_float(raw_current.get('SLP'))),
        list(map(Forecast,
                       raw['time']['startPeriodName'],
                       [label=='High' for label in raw['time']['tempLabel']],
                       map(parse_int, raw['data']['temperature']),
                       map(parse_int, raw['data']['pop']),
                       raw['data']['iconLink'],
                       raw['data']['weather'],
                       raw['data']['text']))
    )
    

def parse_int(value, default=0):
    """
    Attempt to cast *value* into an integer, returning *default* if it fails.
    """
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default

def parse_float(value, default=0.0):
    """
    Attempt to cast *value* into a float, returning *default* if it fails.
    """
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default

def parse_boolean(value, default=False):
    """
    Attempt to cast *value* into a bool, returning *default* if it fails.
    """
    if value is None:
        return default
    try:
        return bool(value)
    except ValueError:
        return default


if __name__ == '__main__':
    NEWARK_LATITUDE = 39.6782
    NEWARK_LONGITUDE = -75.7616
    print("Warning! You should not run this file directly. You should import it!")
    print(get_weather(NEWARK_LATITUDE, NEWARK_LONGITUDE).current.temperature)
