# ==================================================
# NOVA V5.3
# EXTRA TOOLS
# Weather / Currency / Units / Random
# ==================================================

import json
import random
import re
import urllib.parse
import urllib.request
from datetime import datetime


# ==================================================
# HTTP JSON
# ==================================================

def _get_json(url, timeout=10):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "NOVA-AI/5.3"
        }
    )

    with urllib.request.urlopen(
        request,
        timeout=timeout
    ) as response:

        data = response.read().decode(
            "utf-8"
        )

        return json.loads(data)


# ==================================================
# CLEAN CITY NAME
# ==================================================

def clean_city_name(city):
    if not city:
        return ""

    city = str(city).strip()

    # Remove Arabic punctuation
    city = re.sub(
        r"[؟?!،,:;.!]+$",
        "",
        city
    )

    # Normalize spaces
    city = re.sub(
        r"\s+",
        " ",
        city
    ).strip()


    # ------------------------------------------------
    # Common Arabic weather prefixes
    # ------------------------------------------------

    prefixes = [
        "في مدينة ",
        "في مدينه ",
        "بمدينة ",
        "بمدينه ",
        "مدينة ",
        "مدينه ",
        "في ",
        "ب "
    ]

    changed = True

    while changed:

        changed = False

        for prefix in prefixes:

            if city.startswith(prefix):

                city = city[
                    len(prefix):
                ].strip()

                changed = True
                break


    # ------------------------------------------------
    # Joined "ب" prefix
    # Example:
    # بطنجة -> طنجة
    # بلندن -> لندن
    # بطنجا -> طنجة
    # ------------------------------------------------

    if city.startswith("ب") and len(city) > 3:

        possible = city[1:].strip()

        known_starters = [
            "طنجة",
            "الرباط",
            "الدار البيضاء",
            "مراكش",
            "فاس",
            "مكناس",
            "أكادير",
            "وجدة",
            "تطوان",
            "لندن",
            "باريس",
            "مدريد",
            "روما",
            "نيويورك",
            "دبي",
            "القاهرة"
        ]

        if any(
            possible.startswith(item)
            for item in known_starters
        ):
            city = possible


    # ------------------------------------------------
    # Common Arabic typos / aliases
    # ------------------------------------------------

    aliases = {
        "بنلدن": "لندن",
        "بلدن": "لندن",
        "لند": "لندن",

        "طنجا": "طنجة",
        "طنجه": "طنجة",

        "رباط": "الرباط",

        "كازا": "الدار البيضاء",
        "كازابلانكا": "الدار البيضاء",

        "مراكش": "مراكش",

        "فاس": "فاس",

        "تطوان": "تطوان",

        "اغادير": "أكادير",
        "اكادير": "أكادير"
    }

    if city in aliases:
        city = aliases[city]


    return city.strip()


# ==================================================
# GEOCODING
# ==================================================

def _geocode(city):

    city = clean_city_name(city)

    if not city:
        return None


    # ------------------------------------------------
    # Special known cities
    # ------------------------------------------------

    known_cities = {
        "طنجة": (
            35.7595,
            -5.83395,
            "Tangier, Morocco"
        ),

        "طنجة المغرب": (
            35.7595,
            -5.83395,
            "Tangier, Morocco"
        ),

        "الرباط": (
            34.0209,
            -6.8416,
            "Rabat, Morocco"
        ),

        "الدار البيضاء": (
            33.5731,
            -7.5898,
            "Casablanca, Morocco"
        ),

        "مراكش": (
            31.6295,
            -7.9811,
            "Marrakesh, Morocco"
        ),

        "فاس": (
            34.0331,
            -5.0003,
            "Fez, Morocco"
        ),

        "مكناس": (
            33.8935,
            -5.5473,
            "Meknes, Morocco"
        ),

        "أكادير": (
            30.4278,
            -9.5981,
            "Agadir, Morocco"
        ),

        "وجدة": (
            34.6814,
            -1.9086,
            "Oujda, Morocco"
        ),

        "تطوان": (
            35.5889,
            -5.3626,
            "Tetouan, Morocco"
        ),

        "لندن": (
            51.5074,
            -0.1278,
            "London, United Kingdom"
        ),

        "باريس": (
            48.8566,
            2.3522,
            "Paris, France"
        ),

        "مدريد": (
            40.4168,
            -3.7038,
            "Madrid, Spain"
        ),

        "روما": (
            41.9028,
            12.4964,
            "Rome, Italy"
        ),

        "دبي": (
            25.2048,
            55.2708,
            "Dubai, United Arab Emirates"
        ),

        "القاهرة": (
            30.0444,
            31.2357,
            "Cairo, Egypt"
        )
    }


    if city in known_cities:

        latitude, longitude, name = (
            known_cities[city]
        )

        return {
            "latitude": latitude,
            "longitude": longitude,
            "name": name
        }


    # ------------------------------------------------
    # Open-Meteo Geocoding
    # ------------------------------------------------

    try:

        encoded = urllib.parse.quote(
            city
        )

        url = (
            "https://geocoding-api.open-meteo.com/"
            "v1/search"
            "?name="
            + encoded
            + "&count=5"
            + "&language=en"
            + "&format=json"
        )

        data = _get_json(url)

        results = data.get(
            "results",
            []
        )

        if not results:
            return None


        # Prefer populated places
        for result in results:

            latitude = result.get(
                "latitude"
            )

            longitude = result.get(
                "longitude"
            )

            name = result.get(
                "name"
            )

            if (
                latitude is not None
                and longitude is not None
                and name
            ):

                country = result.get(
                    "country",
                    ""
                )

                display_name = str(name)

                if country:
                    display_name += (
                        ", "
                        + str(country)
                    )

                return {
                    "latitude": latitude,
                    "longitude": longitude,
                    "name": display_name
                }


    except Exception:
        return None


    return None


# ==================================================
# WEATHER CODE
# ==================================================

def weather_condition(code):

    try:
        code = int(code)
    except Exception:
        return "غير معروف"


    conditions = {

        0: "صافي",

        1: "غالبًا صافي",
        2: "غائم جزئيًا",
        3: "غائم",

        45: "ضباب",
        48: "ضباب متجمد",

        51: "رذاذ خفيف",
        53: "رذاذ متوسط",
        55: "رذاذ كثيف",

        56: "رذاذ متجمد خفيف",
        57: "رذاذ متجمد كثيف",

        61: "مطر خفيف",
        63: "مطر متوسط",
        65: "مطر غزير",

        66: "مطر متجمد خفيف",
        67: "مطر متجمد غزير",

        71: "ثلج خفيف",
        73: "ثلج متوسط",
        75: "ثلج غزير",

        77: "حبيبات ثلج",

        80: "زخات مطر خفيفة",
        81: "زخات مطر متوسطة",
        82: "زخات مطر قوية",

        85: "زخات ثلج خفيفة",
        86: "زخات ثلج قوية",

        95: "عاصفة رعدية",
        96: "عاصفة رعدية مع برد",
        99: "عاصفة رعدية قوية مع برد"
    }

    return conditions.get(
        code,
        "غير معروف"
    )


# ==================================================
# WEATHER
# ==================================================

def weather(city, days=2):

    original_city = str(city).strip()

    city = clean_city_name(
        original_city
    )

    if not city:

        return {
            "ok": False,
            "error": "لم يتم تحديد المدينة."
        }


    location = _geocode(
        city
    )

    if not location:

        return {
            "ok": False,
            "error": (
                "لم أجد المدينة: "
                + city
            )
        }


    latitude = location[
        "latitude"
    ]

    longitude = location[
        "longitude"
    ]

    location_name = location[
        "name"
    ]


    # ------------------------------------------------
    # Forecast API
    # ------------------------------------------------

    try:

        url = (
            "https://api.open-meteo.com/"
            "v1/forecast"
            "?latitude="
            + str(latitude)
            + "&longitude="
            + str(longitude)

            + "&current="
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m"

            + "&daily="
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max"

            + "&forecast_days="
            + str(max(1, min(int(days), 7)))

            + "&timezone=auto"
        )


        data = _get_json(
            url
        )


        current_data = data.get(
            "current",
            {}
        )

        daily_data = data.get(
            "daily",
            {}
        )


        current = {

            "temperature":
                current_data.get(
                    "temperature_2m"
                ),

            "humidity":
                current_data.get(
                    "relative_humidity_2m"
                ),

            "apparent_temperature":
                current_data.get(
                    "apparent_temperature"
                ),

            "precipitation":
                current_data.get(
                    "precipitation"
                ),

            "wind_speed":
                current_data.get(
                    "wind_speed_10m"
                ),

            "condition":
                weather_condition(
                    current_data.get(
                        "weather_code"
                    )
                )
        }


        daily = []


        dates = daily_data.get(
            "time",
            []
        )

        codes = daily_data.get(
            "weather_code",
            []
        )

        maximums = daily_data.get(
            "temperature_2m_max",
            []
        )

        minimums = daily_data.get(
            "temperature_2m_min",
            []
        )

        precipitation = daily_data.get(
            "precipitation_probability_max",
            []
        )


        for i in range(
            min(
                len(dates),
                7
            )
        ):

            daily.append({

                "date":
                    dates[i],

                "condition":
                    weather_condition(
                        codes[i]
                        if i < len(codes)
                        else None
                    ),

                "max":
                    maximums[i]
                    if i < len(maximums)
                    else None,

                "min":
                    minimums[i]
                    if i < len(minimums)
                    else None,

                "precipitation_probability":
                    precipitation[i]
                    if i < len(precipitation)
                    else None
            })


        return {

            "ok": True,

            "location":
                location_name,

            "current":
                current,

            "daily":
                daily
        }


    except Exception as error:

        return {
            "ok": False,
            "error": (
                "حدث خطأ أثناء الحصول "
                "على الطقس: "
                + str(error)
            )
        }


# ==================================================
# CURRENCY
# ==================================================

def currency(
    amount,
    from_currency,
    to_currency
):

    try:

        amount = float(
            amount
        )

    except Exception:

        return {
            "ok": False,
            "error": "المبلغ غير صحيح."
        }


    from_currency = str(
        from_currency
    ).upper().strip()

    to_currency = str(
        to_currency
    ).upper().strip()


    if from_currency == to_currency:

        return {
            "ok": True,
            "amount": amount,
            "from": from_currency,
            "result": amount,
            "to": to_currency,
            "date": datetime.now().strftime(
                "%Y-%m-%d"
            )
        }


    try:

        url = (
            "https://api.frankfurter.app/"
            + str(amount)
            + "?from="
            + urllib.parse.quote(
                from_currency
            )
            + "&to="
            + urllib.parse.quote(
                to_currency
            )
        )


        data = _get_json(
            url
        )


        rates = data.get(
            "rates",
            {}
        )

        result = rates.get(
            to_currency
        )


        if result is None:

            return {
                "ok": False,
                "error": (
                    "لم أجد سعر الصرف "
                    "لهذه العملات."
                )
            }


        return {

            "ok": True,

            "amount":
                amount,

            "from":
                from_currency,

            "result":
                result,

            "to":
                to_currency,

            "date":
                data.get(
                    "date"
                )
        }


    except Exception as error:

        return {
            "ok": False,
            "error": (
                "تعذر الحصول على سعر الصرف: "
                + str(error)
            )
        }


# ==================================================
# UNIT CONVERSION
# ==================================================

def convert_units(
    value,
    from_unit,
    to_unit
):

    try:

        value = float(
            value
        )

    except Exception:

        return {
            "ok": False,
            "error": "القيمة غير صحيحة."
        }


    aliases = {

        "ملم": "mm",
        "مم": "mm",
        "millimeter": "mm",
        "millimeters": "mm",

        "سم": "cm",
        "سنتيمتر": "cm",
        "سنتيمترات": "cm",
        "centimeter": "cm",

        "م": "m",
        "متر": "m",
        "meters": "m",
        "meter": "m",

        "كم": "km",
        "كيلومتر": "km",
        "كيلومترات": "km",
        "kilometer": "km",

        "غ": "g",
        "جرام": "g",
        "غرام": "g",
        "gram": "g",

        "كغ": "kg",
        "kg": "kg",
        "كيلو": "kg",
        "كيلوغرام": "kg",
        "kilogram": "kg",

        "رطل": "lb",
        "رطلًا": "lb",
        "lb": "lb",
        "pound": "lb",

        "c": "c",
        "°c": "c",
        "سيليزي": "c",
        "مئوية": "c",

        "f": "f",
        "°f": "f",
        "فهرنهايت": "f"
    }


    from_unit = aliases.get(
        str(from_unit).lower().strip(),
        str(from_unit).lower().strip()
    )

    to_unit = aliases.get(
        str(to_unit).lower().strip(),
        str(to_unit).lower().strip()
    )


    # Same unit

    if from_unit == to_unit:

        return {
            "ok": True,
            "value": value,
            "from": from_unit,
            "result": value,
            "to": to_unit
        }


    # ------------------------------------------------
    # Length
    # ------------------------------------------------

    length = {

        "mm": 0.001,
        "cm": 0.01,
        "m": 1.0,
        "km": 1000.0
    }


    if (
        from_unit in length
        and to_unit in length
    ):

        meters = (
            value
            * length[from_unit]
        )

        result = (
            meters
            / length[to_unit]
        )

        return {

            "ok": True,

            "value":
                value,

            "from":
                from_unit,

            "result":
                result,

            "to":
                to_unit
        }


    # ------------------------------------------------
    # Mass
    # ------------------------------------------------

    mass = {

        "g": 0.001,
        "kg": 1.0,
        "lb": 0.45359237
    }


    if (
        from_unit in mass
        and to_unit in mass
    ):

        kilograms = (
            value
            * mass[from_unit]
        )

        result = (
            kilograms
            / mass[to_unit]
        )

        return {

            "ok": True,

            "value":
                value,

            "from":
                from_unit,

            "result":
                result,

            "to":
                to_unit
        }


    # ------------------------------------------------
    # Temperature
    # ------------------------------------------------

    if (
        from_unit in ["c", "f"]
        and to_unit in ["c", "f"]
    ):

        if from_unit == "c":

            result = (
                value * 9 / 5
            ) + 32

        else:

            result = (
                value - 32
            ) * 5 / 9


        return {

            "ok": True,

            "value":
                value,

            "from":
                from_unit,

            "result":
                result,

            "to":
                to_unit
        }


    return {
        "ok": False,
        "error": (
            "لا أستطيع التحويل بين "
            + str(from_unit)
            + " و "
            + str(to_unit)
        )
    }


# ==================================================
# RANDOM NUMBER
# ==================================================

def random_number(
    a=1,
    b=100
):

    try:

        a = int(a)
        b = int(b)

    except Exception:

        return {
            "ok": False,
            "error": "حدود الرقم غير صحيحة."
        }


    if a > b:

        a, b = b, a


    return {
        "ok": True,
        "result": random.randint(
            a,
            b
        )
    }


# ==================================================
# CURRENT DATETIME
# ==================================================

def current_datetime():

    now = datetime.now()

    return {

        "ok": True,

        "date":
            now.strftime(
                "%Y-%m-%d"
            ),

        "time":
            now.strftime(
                "%H:%M:%S"
            )
    }