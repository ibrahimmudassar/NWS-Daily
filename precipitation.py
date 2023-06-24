import requests
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables
import pandas as pd
import plotly.graph_objects as go


env = Env()
env.read_env()  # read .env file, if it exists


def embed_to_discord():
    # create embed object for webhook
    embed = DiscordEmbed(title="Precipitation Today!", color="242491")

    # Elevation
    embed.add_embed_field(name='⛰️ Elevation', value=f"{data['elevation']} m")

    # Precip Total
    embed.add_embed_field(
        name='🌧️ Total', value=f"{data['daily']['precipitation_sum'][0]} {data['daily_units']['precipitation_sum']}")

    # set image
    embed.set_image(url='attachment://fig1.png')

    # set footer
    embed.set_footer(
        text=f"Made By Ibrahim Mudassar in {round(data['generationtime_ms'], 2)} s")

    # add embed object to webhook(s)
    for webhook_url in env.list("WEBHOOKS"):
        webhook = DiscordWebhook(url=webhook_url)

        with open("fig1.png", "rb") as f:
            webhook.add_file(file=f.read(), filename='fig1.png')

        webhook.add_embed(embed)
        webhook.execute()


lat = env('LATITUDE')
long = env('LONGITUDE')

data = requests.get(
    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=precipitation_sum&hourly=rain,showers,snowfall&models=best_match&forecast_days=1&timezone=EST").json()

all_categories = {}
for categories in data["hourly"]:
    all_categories[categories] = data["hourly"][categories]
df = pd.DataFrame(all_categories)

if data["daily"]["precipitation_sum"][0] > 0:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["rain"],
        fill='tozeroy',
        mode='lines',
        name="rain"
    ))
    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["showers"],
        fill='tozeroy',
        mode='lines',
        name="showers"
    ))
    fig.add_trace(go.Scatter(
        x=df["time"],
        y=df["snowfall"],
        fill='tozeroy',
        mode='lines',
        name="snowfall"
    ))

    fig.update_yaxes(ticklabelstep=2)

    # Labels
    fig.update_layout(title={'text': 'Precipitation vs. Time', 'x': 0.5, 'xanchor': 'center'},
                      yaxis_zeroline=True,
                      xaxis_zeroline=True,
                      xaxis_title="Time",
                      yaxis_title="Millimeters of Precipitation")

    # Attribution
    fig.add_annotation(text="By: Ibrahim Mudassar",
                       xref="paper", yref="paper",
                       x=1, y=-0.14,
                       showarrow=False,
                       align="center",
                       font=dict(size=9))

    fig.write_image("fig1.png", width=1080, height=720)

    embed_to_discord()
