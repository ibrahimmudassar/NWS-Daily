import glob

import requests
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables
from PIL import Image

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists


def embed_to_discord(data):
    # create embed object for webhook
    embed = DiscordEmbed(title="NWS Daily", color="242491")

    weather_forecast = f""":thermometer: {data['temperature']}{data['temperatureUnit']}
    :dash: {data['windSpeed']}
    Forecast: {data['shortForecast']}"""

    # Captioning the image
    embed.add_embed_field(
        name="Weather", value=weather_forecast, inline=False)

    embed.set_image(url='attachment://precip_final.gif')

    # set thumbnail
    embed.set_thumbnail(
        url='https://upload.wikimedia.org/wikipedia/commons/thumb/f/ff/US-NationalWeatherService-Logo.svg/720px-US-NationalWeatherService-Logo.svg.png')

    # set footer
    embed.set_footer(text='Future Radar Reading')

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
         save_all=True, duration=700, loop=0)

# This is to obtain other weather information
# Visit https://www.weather.gov/documentation/services-web-api for more info to tailor this api request to your location
r = requests.get("https://api.weather.gov/gridpoints/PHI/74,107/forecast")
# I just want the first weather forecast (change the number for varying times)
weather_data = r.json()['properties']['periods'][0]


embed_to_discord(weather_data)
