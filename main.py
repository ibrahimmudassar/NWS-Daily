import glob

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables
from PIL import Image

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists

def uv_index_to_color(uv_index: float) -> str:
    if uv_index > 10:
        return ":purple_square:"
    elif uv_index > 7:
        return ":red_square:"
    elif uv_index > 5:
        return ":orange_square:"
    elif uv_index > 2:
        return ":yellow_square:"
    else:
        return ":green_square:"

def embed_to_discord(data):
    # create embed object for webhook
    embed = DiscordEmbed(title="NWS Daily", color="242491")

    weather_forecast = f""":thermometer: {data['daily']['apparent_temperature_max'][0]}/{data['daily']['apparent_temperature_min'][0]} {data['daily_units']['apparent_temperature_max']}
    :dash: {data['daily']['wind_speed_10m_max'][0]} {data['daily_units']['wind_speed_10m_max']}
    :sun_with_face: {data['daily']['uv_index_max'][0]} {uv_index_to_color(data['daily']['uv_index_max'][0])}
    :cloud_rain: {data['daily']['precipitation_sum'][0]} {data['daily_units']['precipitation_sum'][0]}"""

    # Captioning the image
    embed.add_embed_field(
        name="Weather", value=weather_forecast, inline=False)

    embed.set_image(url='attachment://precip_final.gif')

    # set thumbnail
    embed.set_thumbnail(
        url='https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/US-NationalWeatherService-Logo.svg/720px-US-NationalWeatherService-Logo.svg.png')

    # set footer
    embed.set_footer(text='Made By Ibrahim Mudassar',
                     icon_url='https://avatars.githubusercontent.com/u/22484328?v=4')

    # set timestamp (default is now) accepted types are int, float and datetime
    embed.set_timestamp()

    # add embed object to webhook(s)
    for webhook_url in env.list("WEBHOOKS"):
        webhook = DiscordWebhook(url=webhook_url)

        # set image
        with open("precip_final.gif", "rb") as f:
            webhook.add_file(file=f.read(), filename='precip_final.gif')

        webhook.add_embed(embed)
        webhook.execute()


# the range numbers should change if the time of day changes
for i in range(3, 8):
    r = requests.get(
        "https://graphical.weather.gov/images/northeast/Wx" + str(i) + "_northeast.png")

    with open("precip_" + str(i) + ".png", "wb") as f:
        f.write(r.content)

# filepaths
fp_in = "precip_*.png"
fp_out = "precip_final.gif"

# https://pillow.readthedocs.io/en/stable/handbook/image-file-formats.html#gif
img, *imgs = [Image.open(f) for f in sorted(glob.glob(fp_in))]
img.save(fp=fp_out, format='GIF', append_images=imgs,
         save_all=True, duration=800, loop=0)

lat = env('LATITUDE')
long = env('LONGITUDE')

# This is to obtain other weather information from openmeteo
r = requests.get(
    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=apparent_temperature_max,apparent_temperature_min,uv_index_max,precipitation_sum,wind_speed_10m_max&forecast_days=1&timezone=EST").json()

embed_to_discord(r)
