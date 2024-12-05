from bakery_weather import get_weather

def count_sunny(latitude: float, longitude: float) -> int:
    forecast = get_forecast(latitude, longitude)  

    sunny_count = 0
    for report in forecast:
        if "Sunny" in report.status:
            sunny_count += 1
    
    return sunny_count


weather = get_weather(39.6782, -75.7616)
print(weather.current.temperature)
