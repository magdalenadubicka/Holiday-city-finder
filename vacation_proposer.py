from booking_getter import get_cheapest_hotels
from weather_getter import get_weather_data
import json

cities = ['Amsterdam', 'Athens', 'Baku', 'Belfast', 'Belgrade', 'Berlin', 'Bern', 'Bratislava', 'Brussels',
          'Bucharest', 'Budapest', 'Cardiff', 'Chișinău', 'Copenhagen', 'Dublin', 'Edinburgh', 'Helsinki', 'Kyiv', 'Lisbon',
          'Ljubljana', 'London', 'Madrid', 'Minsk', 'Monaco', 'Moscow', 'Oslo', 'Paris', 'Podgorica',
          'Prague', 'Pristina', 'Reykjavík', 'Riga', 'Rome', 'Sarajevo', 'Skopje', 'Sofia', 'Stockholm',
          'Tallinn', 'Tbilisi', 'Tirana', 'Vaduz', 'Valletta', 'Vienna', 'Vilnius', 'Warsaw', 'Zagreb', 'Milan',
          'Istanbul', 'Antalya', 'Barcelona', 'Venice', 'Florence', 'Munich', 'Heraklion', 'Cracow', 'Frankfurt', 'Nice',
          'Porto', 'Rhodes']
          
def get_best_cities(checkin, checkout, group_adults, group_children):
    cities_weather_data = {}
    avg_city_weather = {} 
    weather_city_scores = []
    
    with open('geo_positions.json') as pos_file:
        cities_geo_positions = json.load(pos_file)
    
    for city in cities:
        weather_data = get_weather_data(city, checkin, checkout, cities_geo_positions)
        cities_weather_data[city] = weather_data
        total_weather_score = 0
        for weather_day_data in weather_data:
            total_weather_score += weather_day_data['weather_score']

        avg_weather_score = total_weather_score/len(weather_data)
        avg_city_weather[city] = avg_weather_score

    top_weather_cities = [city for city, score in sorted(avg_city_weather.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    city_score_list = []
    cities_hotels_data = {}
    for city in top_weather_cities:
        print('2', city)
        booking_score_list = []
        cheapest_hotels = get_cheapest_hotels(city, checkin, checkout, group_adults, group_children)
        cities_hotels_data[city] = cheapest_hotels

        for hotel in cheapest_hotels:
            booking_score_list.append(hotel['booking_score'])

        max_booking_score = max(booking_score_list)
        max_booking_score = round(max_booking_score, 2)

        city_score = avg_city_weather[city] * max_booking_score/100
        city_score = round(city_score, 2)
        city_score_dict = {}
        city_score_dict[city] = city_score
        city_score_list.append(city_score_dict)
    
    sorted_city_score = sorted(city_score_list, key=lambda x: list(x.values())[0], reverse=True)
    
    top_3_cities = [list(d.keys())[0] for d in sorted_city_score[:3]]
    
    best_cities_dict = {}
    for city in top_3_cities:
        city_info_dict = {}
        city_info_dict['hotels'] = cities_hotels_data[city]
        city_info_dict['weather_score'] = avg_city_weather[city]
        best_cities_dict[city] = city_info_dict
        
    extended_cities_dict = {}
    for city in top_weather_cities:
        city_info_dict = {}
        city_info_dict['hotels'] = cities_hotels_data[city]
        city_info_dict['weather_score'] = avg_city_weather[city]
        extended_cities_dict[city] = city_info_dict
    
            
    return {'best': best_cities_dict, 'extended': extended_cities_dict}