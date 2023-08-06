import hashlib
import json
import logging
import os
import re
from datetime import datetime
from ipaddress import ip_address as ip_address_obj
from math import radians, cos, sin, asin, sqrt

import requests
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2
from django.core.cache import cache
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404
from suntime import Sun
from timezonefinder import TimezoneFinder

from . import models

logger = logging.getLogger('django_tasker_geobase')


class Geobase:
    def __init__(self, model: models.Geobase = None):
        self.object = model

    def type(self):
        return self.object.type

    def suntime(self) -> dict:
        sun = Sun(self.object.latitude, self.object.longitude)
        return {
            'sunrise': sun.get_sunrise_time(),
            'sunset': sun.get_sunset_time(),
        }

    def weather(self, units="metric", lang="en") -> dict:

        # openweathermap download
        openweathermap_key = getattr(
            settings, 'GEOBASE_OPENWEATHERMAP_KEY',
            os.environ.get('GEOBASE_OPENWEATHERMAP_KEY')
        )

        if openweathermap_key:
            proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
            if proxies:
                proxies = {'http': proxies, 'https': proxies}

                response = requests.get(
                    url='https://api.openweathermap.org/data/2.5/weather/',
                    params={
                        'lat': self.object.latitude,
                        'lon': self.object.longitude,
                        'appid': openweathermap_key,
                        'units': units,
                        'lang': lang,
                    },
                    timeout=10,
                    proxies=proxies
                )

                if response.status_code == 200:
                    openweather_result = response.json()
                    return {
                        'temperature': openweather_result.get('main').get('temp'),
                        'temperature_min': openweather_result.get('main').get('temp_min'),
                        'temperature_max': openweather_result.get('main').get('temp_max'),
                        'pressure': openweather_result.get('main').get('pressure'),
                        'humidity': openweather_result.get('main').get('humidity'),
                        'visibility': openweather_result.get('visibility'),
                        'wind_speed': openweather_result.get('wind').get('speed'),
                        'wind_degrees': openweather_result.get('wind').get('deg'),
                        'clouds': openweather_result.get('clouds').get('all'),
                    }
                else:
                    return {
                        'temperature': None,
                        'temperature_min': None,
                        'temperature_max': None,
                        'pressure': None,
                        'humidity': None,
                        'visibility': None,
                        'wind_speed': None,
                        'wind_degrees': None,
                        'clouds': None,
                    }


def geo(query: str) -> models.Geobase:
    """
    Calculates geolocation by string address or coordinates.

    :param query: string address or coordinates
    :returns: models.Geobase
    """
    cache_key = hashlib.sha256()
    cache_key.update(query.encode('utf-8'))

    cache_geocoder = cache.get("{name}-{hash}".format(name=__name__, hash=cache_key.hexdigest()))
    if not getattr(settings, 'TESTING', None) and cache_geocoder:
        logger.info("get cache geo object {query}".format(query=query))
        return get_object_or_404(models.Geobase, id=cache_geocoder)

    data = _search(query=query)
    if not data:
        return

    strict = data.get('strict')
    if strict.get('country'):
        geobase_country = models.Geobase.objects.filter(
            ru=strict.get('country').get('ru'),
            type=strict.get('country').get('type_model'),
        )[:1]

        if geobase_country.exists():
            geobase_country = geobase_country.get()
        else:
            geobase_country = models.Geobase.objects.create(
                en=strict.get('country').get('en'),
                ru=strict.get('country').get('ru'),
                type=strict.get('country').get('type_model'),
            )

            logger.info('create object country {name_en}, {name_ru}'.format(
                name_ru=strict.get('country').get('ru'),
                name_en=strict.get('country').get('en'))
            )

        geobase = geobase_country

        if strict.get('province'):
            geobase_province = models.Geobase.objects.filter(
                ru=strict.get('province').get('ru'),
                parent=geobase_country,
                type=strict.get('type_model'),
            )[:1]

            if geobase_province.exists():
                geobase_province = geobase_province.get()
            else:
                geobase_province = models.Geobase.objects.create(
                    en=strict.get('province').get('en'),
                    ru=strict.get('province').get('ru'),
                    type=strict.get('province').get('type_model'),
                    parent=geobase_country,
                )

            geobase = geobase_province

            if strict.get('locality'):
                geobase_locality = models.Geobase.objects.filter(
                    ru=strict.get('locality').get('ru'),
                    parent=geobase_province,
                    type=strict.get('type_model'),
                )[:1]

                if geobase_locality.exists():
                    geobase_locality = geobase_locality.get()
                else:
                    locality_data = _search_yandex(
                        query="{country}, {city}".format(
                            country=strict.get('country').get('ru'),
                            city=strict.get('locality').get('ru'),
                        ),
                        language='ru'
                    )

                    # Save db
                    geobase_locality = models.Geobase.objects.create(
                        en=strict.get('locality').get('en'),
                        ru=strict.get('locality').get('ru'),
                        type=strict.get('locality').get('type_model'),
                        parent=geobase_province,
                        latitude=locality_data.get('latitude'),
                        longitude=locality_data.get('longitude'),
                        timezone=data.get('timezone')
                    )

                    # openweathermap
                    openweathermap_key = getattr(
                        settings, 'GEOBASE_OPENWEATHERMAP_KEY',
                        os.environ.get('GEOBASE_OPENWEATHERMAP_KEY')
                    )

                    if openweathermap_key:
                        proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
                        if proxies:
                            proxies = {'http': proxies, 'https': proxies}

                        response = requests.get(
                            url='https://api.openweathermap.org/data/2.5/weather/',
                            params={
                                'lat': locality_data.get('latitude'),
                                'lon': locality_data.get('longitude'),
                                'appid': openweathermap_key,
                                'units': 'metric',
                                'lang': 'en',
                            },
                            timeout=5,
                            proxies=proxies
                        )

                        if response.status_code == 200:
                            openweather_result = response.json()
                            geobase_locality.openweathermap = openweather_result.get('id')
                            geobase_locality.save()

                geobase = geobase_locality

                if strict.get('street'):
                    geobase_street = models.Geobase.objects.filter(
                        ru=strict.get('street').get('ru'),
                        parent=geobase_locality,
                        type=strict.get('type_model'),
                    )[:1]

                    if geobase_street.exists():
                        geobase_street = geobase_street.get()
                    else:
                        geobase_street = models.Geobase.objects.create(
                            en=strict.get('street').get('en'),
                            ru=strict.get('street').get('ru'),
                            type=strict.get('street').get('type_model'),
                            parent=geobase_locality,
                            timezone=data.get('timezone'),
                        )
                    geobase = geobase_street

                    if strict.get('house'):
                        geobase_house = models.Geobase.objects.filter(
                            ru=strict.get('house').get('ru'),
                            parent=geobase_street,
                            type=strict.get('type_model'),
                        )[:1]

                        if geobase_house.exists():
                            geobase_house = geobase_house.get()
                        else:
                            geobase_house = models.Geobase.objects.create(
                                en=strict.get('house').get('en'),
                                ru=strict.get('house').get('ru'),
                                type=strict.get('house').get('type_model'),
                                parent=geobase_street,
                                timezone=data.get('timezone'),
                                zipcode=data.get('zipcode'),
                                latitude=data.get('latitude'),
                                longitude=data.get('longitude'),
                            )
                        geobase = geobase_house

                        if strict.get('apartment'):
                            geobase_apartment = models.Geobase.objects.filter(
                                ru=strict.get('apartment').get('ru'),
                                parent=geobase_house,
                                type=strict.get('type_model'),
                            )[:1]

                            if geobase_apartment.exists():
                                geobase_apartment = geobase_apartment.get()
                            else:
                                geobase_apartment = models.Geobase.objects.create(
                                    en=strict.get('apartment').get('en'),
                                    ru=strict.get('apartment').get('ru'),
                                    type=strict.get('apartment').get('type_model'),
                                    parent=geobase_house,
                                    timezone=data.get('timezone'),
                                    zipcode=data.get('zipcode'),
                                    latitude=data.get('latitude'),
                                    longitude=data.get('longitude'),
                                )
                            geobase = geobase_apartment

        cache_timeout = getattr(settings, 'GEOBASE_CACHE_TIMEOUT', 60 * 60 * 24 * 30)
        cache.set("{name}-{hash}".format(name=__name__, hash=cache_key.hexdigest()), geobase.id, cache_timeout)
        return geobase

    #
    # geobase = None
    # country = None
    #
    # for i in data.get('components'):
    #     geobase, created = models.Geobase.objects.get_or_create(
    #         en=i.get('en'),
    #         ru=i.get('ru'),
    #         parent=geobase,
    #         type=i.get('type_model'),
    #     )
    #
    #     if i.get('type') == 'country':
    #         country = i.get('ru')
    #
    #     if i.get('type') in ['house', 'apartment']:
    #         geobase.timezone = data.get('timezone')
    #         geobase.zipcode = data.get('zipcode')
    #         geobase.latitude = data.get('latitude')
    #         geobase.longitude = data.get('longitude')
    #         geobase.save()
    #     elif i.get('type') == 'locality':
    #         if data.get('formatted') and created:
    #             locality_data = _search_yandex(
    #                 query="{country}, {city}".format(
    #                     country=country,
    #                     city=i.get('ru'),
    #                 ),
    #                 language='ru'
    #             )
    #             geobase.latitude = locality_data.get('latitude')
    #             geobase.longitude = locality_data.get('longitude')
    #
    #             # openweathermap
    #             openweathermap_key = getattr(
    #                 settings, 'GEOBASE_OPENWEATHERMAP_KEY',
    #                 os.environ.get('GEOBASE_OPENWEATHERMAP_KEY')
    #             )
    #
    #             if openweathermap_key:
    #                 proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
    #                 if proxies:
    #                     proxies = {'http': proxies, 'https': proxies}
    #
    #                 response = requests.get(
    #                     url='https://api.openweathermap.org/data/2.5/weather/',
    #                     params={
    #                         'lat': locality_data.get('latitude'),
    #                         'lon': locality_data.get('longitude'),
    #                         'appid': openweathermap_key,
    #                         'units': 'metric',
    #                         'lang': 'en',
    #                     },
    #                     timeout=5,
    #                     proxies=proxies
    #                 )
    #
    #                 if response.status_code == 200:
    #                     openweather_result = response.json()
    #                     geobase.openweathermap = openweather_result.get('id')
    #
    #         geobase.timezone = data.get('timezone')
    #         geobase.save()
    #     elif i.get('type') in ['street', 'route', 'hydro']:
    #         geobase.timezone = data.get('timezone')
    #         geobase.save()
    #     elif i.get('type') in ['vegetation', 'other', 'metro', 'airport', 'metro', 'railway']:
    #         geobase.timezone = data.get('timezone')
    #         geobase.latitude = data.get('latitude')
    #         geobase.longitude = data.get('longitude')
    #         geobase.save()

    # if geobase:
    #     geobase.save()
    #     cache_timeout = getattr(settings, 'GEOBASE_CACHE_TIMEOUT', 60 * 60 * 24 * 30)
    #     cache.set("{name}-{hash}".format(name=__name__, hash=cache_key.hexdigest()), geobase.id, cache_timeout)
    # return geobase


def wifi(mac_address: str) -> models.Geobase:
    """
    Detect geolocation by MAC address.

    :param mac_address: MAC address
    :returns: models.Geobase
    """

    mac_address = mac_address.strip().replace(":", "")

    cache_key = hashlib.sha256()
    cache_key.update(mac_address.encode('utf-8'))

    cache_geocoder = cache.get("{name}-{hash}".format(name=__name__, hash=cache_key.hexdigest()))
    if cache_geocoder:
        return get_object_or_404(models.Geobase, id=cache_geocoder)

    proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
    if proxies:
        proxies = {'http': proxies, 'https': proxies}

    yandex_locator_key = getattr(settings, 'GEOBASE_YANDEX_LOCATOR_KEY', os.environ.get('GEOBASE_YANDEX_LOCATOR_KEY'))
    if not yandex_locator_key:
        raise Exception("Invalid yandex locator key")

    json_params = json.dumps({
        "common": {
            "version": "1.0",
            "api_key": yandex_locator_key
        },
        "wifi_networks": [{
            "mac": str(mac_address)
        }],
    })

    response = requests.post(
        url='https://api.lbs.yandex.net/geolocation',
        data={
            'json': json_params
        },
        timeout=5,
        proxies=proxies
    )

    locator_result = response.json()
    if locator_result.get('position'):
        if locator_result.get('position').get('latitude') and locator_result.get('position').get('longitude'):

            latitude = locator_result.get('position').get('latitude')
            longitude = locator_result.get('position').get('longitude')
            geobase = geo(query="{longitude}, {latitude}".format(latitude=latitude, longitude=longitude))

            if geobase:
                cache_timeout = getattr(settings, 'GEOBASE_CACHE_TIMEOUT', 60 * 60 * 24 * 30)
                cache.set("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__), geobase.id, cache_timeout)
            return geobase


def ip(request: WSGIRequest = None, ip_address: str = None) -> models.Geobase:
    """
    Calculates geolocation by IP address.

    :param request: WSGIRequest object
    :param ip_address: ip address IPv4 or IPv6.
    :returns: models.Geobase
    """

    if request and isinstance(request, WSGIRequest):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')

    if not ip_address:
        raise Exception("Invalid ip_address")

    proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
    if proxies:
        proxies = {'http': proxies, 'https': proxies}

    yandex_locator_key = getattr(settings, 'GEOBASE_YANDEX_LOCATOR_KEY', os.environ.get('GEOBASE_YANDEX_LOCATOR_KEY'))

    cache_key = hashlib.sha256()
    cache_key.update(ip_address.encode('utf-8'))

    cache_geocoder = cache.get("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__))
    if cache_geocoder:
        return Geobase(model=get_object_or_404(models.Geobase, id=cache_geocoder))

    ip_address = ip_address_obj(address=ip_address)
    longitude, latitude = 0, 0
    if ip_address.version == 4 and ip_address.is_global and yandex_locator_key:
        json_params = json.dumps({
            "common": {
                "version": "1.0",
                "api_key": yandex_locator_key
            },
            "ip": {
                "address_v4": str(ip_address)
            }
        })
        response = requests.post(
            url='https://api.lbs.yandex.net/geolocation',
            data={'json': json_params},
            timeout=5,
            proxies=proxies
        )
        locator_result = response.json()
        if response.status_code == 200:
            if locator_result.get('position').get('latitude') and locator_result.get('position').get('longitude'):
                latitude = locator_result.get('position').get('latitude')
                longitude = locator_result.get('position').get('longitude')

    elif ip_address.version == 4 and ip_address.is_global:
        g = GeoIP2()
        geoip = g.city(str(ip))
        latitude = geoip.get('latitude')
        longitude = geoip.get('longitude')
    elif ip_address.version == 6 and ip_address.is_global:
        g = GeoIP2()
        geoip = g.city(str(ip))
        latitude = geoip.get('latitude')
        longitude = geoip.get('longitude')
    else:
        latitude = 51.478186
        longitude = -0.015424

    geobase = geo(query="{longitude}, {latitude}".format(latitude=latitude, longitude=longitude))
    if geobase:
        # geobase.refresh_from_db()
        cache_timeout = getattr(settings, 'GEOBASE_CACHE_TIMEOUT', 60 * 60 * 24 * 30)
        cache.set("{name}-{hash}".format(hash=cache_key.hexdigest(), name=__name__), geobase.id, cache_timeout)

    return geobase


def haversine(latitude1: float, longitude1: float, latitude2: float, longitude2: float) -> float:
    """
    Calculates the distance in kilometers between two points, given the circumference of the Earth.
    https://en.wikipedia.org/wiki/Haversine_formula

    :param latitude1: latitude1
    :param latitude2: latitude2
    :param longitude1: longitude1
    :param longitude2: longitude2
    :returns: models.GeoTree
    """

    # convert decimal degrees to radians
    longitude1, latitude1, longitude2, latitude2 = map(radians, (longitude1, latitude1, longitude2, latitude2))

    # haversine formula
    dlon = longitude2 - longitude1
    dlat = latitude2 - latitude1
    a = sin(dlat / 2) ** 2 + cos(latitude1) * cos(latitude2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    return 6367 * c * 1000


def zipcode(zipcode: str) -> Geobase:
    zipcode_post_office = models.ZipcodePostOffice.objects.filter(zipcode=zipcode)
    if zipcode_post_office.exists():
        return Geobase(model=zipcode_post_office.last().geobase)

    proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
    if proxies:
        proxies = {'http': proxies, 'https': proxies}

    dt = datetime.today()

    json_params = json.dumps({
        "postalCode": str(zipcode),
        "limit": 1,
        "radius": 100,
        "offset": 0,
        "filters": ["NOT_CLOSED", "NOT_PRIVATE", "NOT_TEMPORARY_CLOSED", "ONLY_ATI"],
        "currentDateTime": dt.strftime('%Y-%m-%dT%H:%M:%S')
    })

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
    }

    response = requests.post(
        url='https://www.pochta.ru/suggestions/v2/postoffice.find-nearest-by-postalcode-raw-filters',
        data=json_params,
        timeout=5,
        proxies=proxies,
        headers=headers,
    )

    result_json = response.json()
    if result_json:
        result_json = result_json.pop()

        geobase = geo(
            query="{longitude}, {latitude}".format(
                latitude=result_json.get('latitude'),
                longitude=result_json.get('longitude')
            )
        )
        zipcode_post_office = models.ZipcodePostOffice(zipcode=zipcode, geobase=geobase)
        zipcode_post_office.save()
        return zipcode_post_office.geobase


def _search(query: str) -> dict:
    ru = _search_yandex(query=query, language='ru')
    en = _search_yandex(
        query="{longitude}, {latitude}".format(longitude=ru.get('longitude'), latitude=ru.get('latitude')),
        language='en',
    )

    d = []
    s = {}
    for item in ru.get('components'):
        en_name = item.get('value')
        for item_en in en.get('components'):
            if item.get('type') == item_en.get('type'):
                en_name = item_en.get('value')

            s.update({
                item.get('type'): {
                    'en': en_name,
                    'ru': item.get('value'),
                    'type_model': item.get('type_model'),
                    'type': item.get('type'),
                }
            })

        d.append({
            'type': item.get('type'),
            'type_model': item.get('type_model'),
            'ru': item.get('value'),
            'en': en_name
        })

    d.reverse()
    ru['components'] = d
    ru['strict'] = s
    ru['formatted'] = ru.get('formatted')

    if ru.get('latitude') and ru.get('longitude'):
        tf = TimezoneFinder()
        ru['timezone'] = tf.timezone_at(lng=ru.get('longitude'), lat=ru.get('latitude'))

    return ru


def _search_yandex(query: str, language='en') -> dict:
    # Get proxy
    proxies = getattr(settings, 'GEOBASE_SOCKS5_PROXY', os.environ.get('GEOBASE_SOCKS5_PROXY'))
    if proxies:
        proxies = {'http': proxies, 'https': proxies}

    params = {
        "apikey": getattr(settings, 'GEOBASE_YANDEX_MAP_KEY', os.environ.get('GEOBASE_YANDEX_MAP_KEY')),
        "format": "json",
        "geocode": query,
    }

    headers = {
        'Content-Type': 'application/json;charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100',
        'Accept': '*/*',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
    }

    if language == 'ru':
        params['lang'] = 'ru_RU'
    else:
        params['lang'] = 'en_RU'

    try:
        response = requests.get(
            url='https://geocode-maps.yandex.ru/1.x/',
            params=params,
            timeout=5,
            proxies=proxies,
            headers=headers,
        )
        logger.debug("get url: {url}".format(url=response.url))

    except requests.exceptions.RequestException as error:
        logger.error(error)
        return {}

    data = {'components': []}
    json_yandex_map = response.json()
    geoobject = json_yandex_map.get('response').get('GeoObjectCollection').get('featureMember')

    for item in geoobject:
        item = item.get('GeoObject')

        if 'Point' in item:
            pos = item.get('Point').get('pos')
            pos = pos.split(" ")
            data['longitude'] = float(pos[0])
            data['latitude'] = float(pos[1])

        if 'postal_code' in item.get('metaDataProperty').get('GeocoderMetaData').get('Address'):
            data['zipcode'] = item.get('metaDataProperty').get('GeocoderMetaData').get('Address').get('postal_code')

        if 'country_code' in item.get('metaDataProperty').get('GeocoderMetaData').get('Address'):
            country_code = item.get('metaDataProperty').get('GeocoderMetaData').get('Address').get('country_code')
            data['country_code'] = country_code

        if 'formatted' in item.get('metaDataProperty').get('GeocoderMetaData').get('Address'):
            data['formatted'] = item.get('metaDataProperty').get('GeocoderMetaData').get('Address').get('formatted')

        item.get('metaDataProperty').get('GeocoderMetaData').get('Address').get('Components').reverse()
        is_province = False
        for component in item.get('metaDataProperty').get('GeocoderMetaData').get('Address').get('Components'):

            if component.get('kind') == 'country':
                type_model = 1
            elif component.get('kind') == 'province':
                if is_province:
                    continue

                is_province = True
                type_model = 2
            elif component.get('kind') == 'area':
                # type_model = 3
                continue
            elif component.get('kind') == 'locality':
                type_model = 4
            elif component.get('kind') == 'district':
                type_model = 5
            elif component.get('kind') == 'street':
                type_model = 6
            elif component.get('kind') == 'house':
                type_model = 7
            elif component.get('kind') == 'hydro':
                type_model = 8
            elif component.get('kind') == 'railway':
                type_model = 9
            elif component.get('kind') == 'route':
                type_model = 10
            elif component.get('kind') == 'vegetation':
                type_model = 11
            elif component.get('kind') == 'airport':
                type_model = 12
            elif component.get('kind') == 'metro':
                type_model = 13
            else:
                type_model = 14

            data['components'].append({
                'type_model': type_model,
                'type': component.get('kind'),
                'value': component.get('name'),
            })
        break

    # We calculate the apartment or office
    apartment = re.search(r'(кв|квартира|офис|оф|а/я|app|apartment)\.*\s*(\w+)$', query)
    if apartment:
        for i in data['components']:
            if i.get('type') == 'house':
                data['components'].insert(0, {'type_model': 15, 'type': 'apartment', 'value': apartment.group(2)})
                break

    # We receive postal codes of Kazakhstan
    if data.get('country_code') == 'KZ':
        for i in data['components']:
            if i.get('type') == 'house':
                try:
                    url = 'https://api.post.kz/api/byAddress/{formatted}'.format(formatted=data['formatted'])
                    response = requests.get(url, timeout=5, proxies=proxies)
                except requests.exceptions.RequestException as error:
                    logger.error(error)
                else:
                    post_kz = response.json()
                    for item_post_kz in post_kz.get('data'):
                        data['zipcode'] = item_post_kz.get('postcode')
                        break
                break

    return data
