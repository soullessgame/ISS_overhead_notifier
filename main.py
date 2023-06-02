import requests
from datetime import datetime
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import time

MY_LAT = 51.866402
MY_LNG = 4.661810
MY_EMAIL = "Lindablad12345@gmail.com"
PASSWORD = "efalvoewcjfxezrm"

def is_it_dark_enough(lat, long):
    parameters = {
        "lat": lat,
        "lng": long,
        "formatted": 0
    }

    response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
    response.raise_for_status()
    data = response.json()

    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

    time_now = datetime.now()
    time_hour_now = time_now.hour

    if time_hour_now < sunrise or time_hour_now >= sunset:
        return True
    else:
        return False

def iss_flies_nearby(lat_ref, lng_ref):
    response = requests.get("http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()
    lat_position_iss = float(data["iss_position"]["latitude"])
    lng_position_iss = float(data["iss_position"]["longitude"])

    # Convert coordinates from degrees to radians
    lat1 = radians(lat_ref)
    lon1 = radians(lng_ref)
    lat2 = radians(lat_position_iss)
    lon2 = radians(lng_position_iss)

    # Radius of the Earth in kilometers
    radius = 6371.0

    # Calculate the differences in coordinates
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Apply the Haversine formula to calculate the distance
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = radius * c

    if distance <= 200:
        return True
    else:
        return False

def weather_is_good(lat, long):
    time_now = datetime.now()
    start_time = time_now.strftime("%Y-%m-%d")

    parameters = {
        "lat": lat,
        "lng": long,
        "start_time": start_time,
        "forecast_days": 1,
        "timezone": "CET"
    }

    response = requests.get(f'https://api.open-meteo.com/v1/forecast?latitude={parameters["lat"]}&longitude={parameters["lng"]}&'
                            f'timezone={parameters["timezone"]}'
                            f'&hourly=cloudcover,precipitation&forecast_days=1')
    response.raise_for_status()
    data = response.json()

    df = pd.DataFrame(data["hourly"])
    formatted_time_df = time_now.strftime("%Y-%m-%dT%H:00")
    df_1_hour = df[df["time"] == formatted_time_df]
    print(df_1_hour)
    if (df_1_hour["cloudcover"].values < 15) and (df_1_hour["precipitation"].values == 0):
        return True


while True:
    time.sleep(360)
    if is_it_dark_enough(MY_LAT,MY_LNG) and iss_flies_nearby(MY_LAT, MY_LNG) and weather_is_good(MY_LAT,MY_LNG):
        # send email if it is dark enough, the ISS is close enough and weather is good
        message = "The ISS is flying near Alblasserdam. " \
                  "Weather conditions are good enough to potentially see the ISS in the sky during this night "
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=PASSWORD)
            connection.sendmail(from_addr=MY_EMAIL, to_addrs="twan.dekorte@gmail.com",
                                msg=message)