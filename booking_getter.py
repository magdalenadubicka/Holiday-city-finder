import requests
from bs4 import BeautifulSoup


def get_price(hotel_div):
    price = hotel_div.find('span', {'class': 'fcab3ed991 fbd1d3018c e729ed5ab6'}).text[2:]
    price = price.replace(' ', '')
    price = int(price)
    return price

def get_link(hotel_div):
    link = hotel_div.find('a', {'class': 'e13098a59f'}).get('href')
    return link

def has_rating(hotel_div):
    rating_divs = hotel_div.find_all('div', {'class': 'b5cd09854e d10a6220b4'})
    if len(rating_divs) >= 1:
        return True
    else:
        return False

def get_rating(hotel_div):
    rating = hotel_div.find('div', {'class': 'b5cd09854e d10a6220b4'}).text
    rating = rating.replace(',', '.')
    rating = float(rating)
    return rating
    
def get_name(hotel_div):
    name = hotel_div.find('div', {'class': 'fcab3ed991 a23c043802'}).text
    return name

def get_booking_score(hotel_div):
    booking_score = (1/get_price(hotel_div)) * get_rating(hotel_div)
    return booking_score

def get_booking_response(url):
    headers = {
    'authority': 'www.crunchbase.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',    
    'accept-language': 'en-US;en;q=0.9',
    'referer': f'https://www.google.com/',
    'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
    }
    
    
    response = requests.get(url, headers=headers)
    
    return response.content

def get_cheapest_hotels(city, checkin, checkout, group_adults, group_children = 0):
    url = f'https://www.booking.com/searchresults.pl.html?ss={city}&checkin={checkin}&checkout={checkout}&group_adults={group_adults}&group_children={group_children}&order=price&selected_currency=EUR&nflt=privacy_type%3D3%3Bprivacy_type_no_date%3D3'
    
    booking_response = get_booking_response(url)
    soup = BeautifulSoup(booking_response, 'html.parser')
    objects = soup.find_all('div', {'class': 'a826ba81c4 fe821aea6c fa2f36ad22 afd256fc79 d08f526e0d ed11e24d01 ef9845d4b3 da89aeb942'})
    
    cheapest_hotels_list = []
    for hotel_div in objects:
        cheapest_hotels_data = {}
        if has_rating(hotel_div) == False:
            continue
        cheapest_hotels_data['hotel_link'] = get_link(hotel_div)
        cheapest_hotels_data['hotel_price'] = get_price(hotel_div)
        cheapest_hotels_data['hotel_rating'] = get_rating(hotel_div)
        cheapest_hotels_data['name'] = get_name(hotel_div)
        cheapest_hotels_data['booking_score'] = get_booking_score(hotel_div)
        cheapest_hotels_list.append(cheapest_hotels_data)
        if len(cheapest_hotels_list) == 3:
            break

    return cheapest_hotels_list