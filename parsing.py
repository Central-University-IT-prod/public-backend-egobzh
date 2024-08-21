import aiohttp
import asyncio
import json
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

class Parsing:
    async def gethotels(self, city, fromm, to):
        async with aiohttp.ClientSession() as session:
                try:
                    response = await session.get(url=f'https://engine.hotellook.com/api/v2/cache.json?location={city}&currency=rub&checkIn={fromm}&checkOut={to}&limit=2')
                    json_object = json.loads(await response.text(encoding='UTF-8'))
                    text = f'📍Отели в городе {city} на {fromm} - {to}:\n'
                    for i, a in enumerate(json_object):
                        text += f'#{i+1}\n'
                        name = json_object[i]['hotelName']
                        stars = json_object[i]['stars']
                        price = f'От {json_object[i]["pricePercentile"]["3"]}₽ до {json_object[i]["pricePercentile"]["99"]}₽'
                        text += f'Название: {name}\nКол-во звезд: {stars}\nСтоимость номеров: {price}\n'
                    if text == f'📍Отели в городе {city} на {fromm} - {to}:\n':
                        return ''
                    else:
                        return text
                except:
                    return ''

    async def getrestoraunce(self, citylist):
        text = 'Список кафе и ресторанов в путешествии:\n'
        for i in citylist:
            async with aiohttp.ClientSession() as session:
                response = await session.get(
                    f'https://nominatim.openstreetmap.org/search.php?q=restaurants+in+{i}&format=json')
                restaraunce = json.loads(await response.text(encoding='UTF-8'))[:5]
                if restaraunce:
                    text += f'📍{i}\n'
                for ind, att in enumerate(restaraunce):
                    text += f'#{ind + 1} {att["name"]} | {att["display_name"]}\n'
        if text == 'Список кафе и ресторанов в путешествии:\n':
            return 'Мне не удалось найти кафе и рестораны в данном путешествии:(('
        else:
            return text

    async def getinterestig(self, citylist):
        text = 'Список инетерсных мест в путешествии:\n'
        for i in citylist:
            async with aiohttp.ClientSession() as session:
                response = await session.get(f'https://nominatim.openstreetmap.org/search.php?q=attractions+in+{i}&format=json')
                attractions = json.loads(await response.text(encoding='UTF-8'))[:5]
                if attractions:
                    text += f'📍{i}\n'
                for ind, att in enumerate(attractions):
                    text += f'#{ind+1} {att["name"]} | {att["display_name"]}\n'
        if text == 'Список инетерсных мест в путешествии:\n':
            return 'Мне не удалось найти интересных мест в данном путешествии:(('
        else:
            return text

    async def gethospitals(self, citylist):
        text = 'Список больниц в путешествии:\n'
        for i in citylist:
            async with aiohttp.ClientSession() as session:
                response = await session.get(f'https://nominatim.openstreetmap.org/search.php?q=hospitals+in+{i}&format=json')
                hospitals = json.loads(await response.text(encoding='UTF-8'))[:2]
                if hospitals:
                    text += f'📍{i}\n'
                for ind, att in enumerate(hospitals):
                    text += f'#{ind+1} {att["name"]} | {att["display_name"]}\n'
        if text == 'Список больниц в путешествии:\n':
            return 'Мне не удалось найти больницы в данном путешествии:(('
        else:
            return text

    async def getmap(self, citylist):
        geolocator = Nominatim(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0", timeout=None)
        cities = ''
        for ind, city in enumerate(citylist):
            location = geolocator.geocode(city)
            if location is not None:
                latitude = location.latitude
                longitude = location.longitude
                cities += f'waypoint{ind}={latitude},{longitude}&'
            else:
                pass
        link = f'https://image.maps.ls.hereapi.com/mia/1.6/routing?apiKey=jb_bpT2WWGIKe6iiBZmXyKDDC7Vy216PbTeA8-_BFWY&{cities}lc=1652B4&w=600&h=400'
        async with aiohttp.ClientSession() as session:
            response = await session.get(link)
            filename = f'maps/{datetime.now().strftime("%d.%m.%Y%H.%M.%S.%m").replace(" ","")}.png'
            with open(filename, "wb") as file:
                file.write(await response.read())
        return filename

    async def getweather(self, citylist):
        text = 'Прогноз погоды на следующие 16 дней:\n'
        maxday = datetime.now() + timedelta(days=15)
        geolocator = Nominatim(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0", timeout=None)
        for city in citylist:
            location = city[1]
            loc = geolocator.geocode(city[1])
            if location is not None:
                latitude = loc.latitude
                longitude = loc.longitude
            else:
                continue
            fromm = datetime.strptime(city[2], "%Y-%m-%d")
            to = datetime.strptime(city[3], "%Y-%m-%d")

            if fromm <= maxday:
                if to <= maxday:
                    link = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m&start_date={city[2]}&end_date={city[3]}'
                else:
                    link = f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m&start_date={city[2]}&end_date={maxday.strftime("%Y-%m-%d")}'
                async with aiohttp.ClientSession() as session:
                    response = await session.get(link)
                    datas = json.loads(await response.text(encoding='UTF-8'))["hourly"]["time"]
                    temp = json.loads(await response.text(encoding='UTF-8'))["hourly"]["temperature_2m"]
                    text += f'📍{city[1]}\n'
                    for i in range(12, len(datas), 24):
                        text += f'🕒{datas[i]}, {str(temp[i]) + "°C"}\n'
            else:
                continue
        if text == 'Прогноз погоды на следующие 16 дней:\n':
            return 'Прогноз погоды пока недоступен, он станет доступен ближе к датам поездки(('
        else:
            return text
