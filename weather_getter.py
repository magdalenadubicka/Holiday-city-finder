import requests
from datetime import datetime

def normalize_data(weather_data):
    for i in range(len(weather_data['hourly']['precipitation_probability'])):
        if weather_data['hourly']['precipitation_probability'][i] == None:
            weather_data['hourly']['precipitation_probability'][i] = 0

def get_api_weather(city, cities_geo_positions):

    latitude = cities_geo_positions[city]['latitude']
    longitude = cities_geo_positions[city]['longitude']

    hourly_params = ['temperature_2m', 'apparent_temperature', 'cloudcover', 'is_day', 'precipitation_probability']
    daily_params = ['temperature_2m_max', 'apparent_temperature_max', 'sunrise', 'sunset']

    hourly_params = ['hourly=' + el for el in hourly_params]
    hourly_params = '&'.join(hourly_params)

    daily_params = ['daily=' + el for el in daily_params]
    daily_params = '&'.join(daily_params)

    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&forecast_days=16&{hourly_params}&{daily_params}&timezone=auto"

    response = requests.get(url).json()
    
    return response

def get_day_length(sunrise, sunset):
    date_format = '%H:%M'
    sunrise = datetime.strptime(sunrise, date_format)
    sunset = datetime.strptime(sunset, date_format)
    day_length = sunset - sunrise
    day_length_minutes = day_length.seconds // 60
    return day_length_minutes

def get_weather_score(weather_data, hour_st_idx, max_feels_temp):
    score = 0
    for h in range(hour_st_idx + 8, hour_st_idx + 20):
        chance_of_rain = weather_data['hourly']['precipitation_probability'][h]/100
        chance_of_not_rain = 1 - chance_of_rain
        if weather_data['hourly']['is_day'][h] == 0:
            score += chance_of_not_rain * 20
        else:
            clouds = weather_data['hourly']['cloudcover'][h]/100
            chance_of_sun = 1 - clouds
            clouds *= chance_of_not_rain
            chance_of_sun *= chance_of_not_rain
            score += clouds * 60 + chance_of_sun * 100 + chance_of_rain * 5
    
    temp_mapping_under_25 = {(-300, 2,5): 0} | {(i*2.5, (i+1)*2.5): i for i in range(1, 10)}
    temp_mapping = {(25, 30): 10}
    temp_mapping_over_25 = {(i*2.5, (i+1)*2.5): 21-i for i in range(12, 21)} | {(52.5, 10000): 0}
    temp_mapping = temp_mapping_under_25 | temp_mapping | temp_mapping_over_25
    
    temp_score = 0
    for temp_range, temp_range_score in temp_mapping.items():
        if max_feels_temp >= temp_range[0] and max_feels_temp < temp_range[1]:
            temp_score = temp_range_score
            
    full_weather_score = int(score * temp_score)
    return full_weather_score

def get_weather_data(city, checkin, checkout, cities_geo_positions):
    weather_data = get_api_weather(city, cities_geo_positions)
    normalize_data(weather_data)
    dates1 = weather_data['daily']['time']
    for i, date in enumerate(weather_data['daily']['time']):
        if date == checkin:
            st_day = i
        if date == checkout:
            en_day = i

    result_list = []
    hour_st_idx = 24 * st_day
    for day_no in range(st_day, en_day + 1):
        daily_weather_data = {}
        daily_weather_data['max_temp'] = weather_data['daily']['temperature_2m_max'][day_no]
        daily_weather_data['max_feekslike_temp'] = weather_data['daily']['apparent_temperature_max'][day_no]
        
        sunrise = weather_data['daily']['sunrise'][day_no][-5:]
        sunset = weather_data['daily']['sunset'][day_no][-5:]
        daily_weather_data['day_length'] = get_day_length(sunrise, sunset)
        
        daily_weather_data['weather_score'] = get_weather_score(weather_data, hour_st_idx, daily_weather_data['max_feekslike_temp'])
        
        hour_st_idx += 24

        result_list.append(daily_weather_data)
        
    total_weather_score = 0
    for weather_day_data in result_list:
        total_weather_score += weather_day_data['weather_score']

    avg_weather_score = total_weather_score/len(weather_data)
        
    return result_list