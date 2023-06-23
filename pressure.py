from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import requests
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables

env = Env()
env.read_env()  # read .env file, if it exists

# baseline to measure the difference in on the graph in hPa
STANDARD_PRESSURE = 1013.25

lat = env('LATITUDE')
long = env('LONGITUDE')

data = requests.get(
    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=weathercode&hourly=pressure_msl,surface_pressure&forecast_days=1&timezone=EST").json()

df = pd.DataFrame(
    {'time': data["hourly"]["time"], 'surface_pressure': data["hourly"]["surface_pressure"], 'pressure_msl': data["hourly"]["pressure_msl"]})

df["relative_pressure_msl"] = df["pressure_msl"] - STANDARD_PRESSURE
df["relative_surface_pressure"] = df["surface_pressure"] - STANDARD_PRESSURE

fig = go.Figure()

fig.add_trace(go.Scatter(
              x=df["time"],
              y=df["relative_pressure_msl"],
              fill='tozeroy',
              mode='lines',
              name="relative_pressure_msl"
              ))
fig.add_trace(go.Scatter(
              x=df["time"],
              y=df["relative_surface_pressure"],
              fill='tozeroy',
              mode='lines',
              name="relative_surface_pressure"))


fig.update_yaxes(ticklabelstep=2)

# Labels
fig.update_layout(title={'text': 'Pressure vs. Time', 'x': 0.5, 'xanchor': 'center'},
                  yaxis_zeroline=True,
                  xaxis_zeroline=True,
                  xaxis_title="Time",
                  yaxis_title="Difference from STP (In hPa)")

# Attribution
fig.add_annotation(text="By: Ibrahim Mudassar",
                   xref="paper", yref="paper",
                   x=1, y=-0.14,
                   showarrow=False,
                   align="center",
                   font=dict(size=9))


fig.write_image("fig1.png", width=1080, height=720)


def embed_to_discord():
    # create embed object for webhook
    embed = DiscordEmbed(title="Pressure Today", color="242491")

    elevation_url = f"https://api.open-meteo.com/v1/elevation?latitude={lat}&longitude={long}"
    elevation = requests.get(elevation_url).json()["elevation"][0]

    # Elevation
    embed.add_embed_field(name='Elevation ⛰️', value=f"{elevation} m")

    # MSL High
    msl_high = df.loc[df["relative_pressure_msl"].idxmax()]
    msl_high_time = datetime.fromisoformat(msl_high["time"]).strftime("%H:%M")
    embed.add_embed_field(name='MSL High', value=f"{msl_high['relative_pressure_msl']} hPa at {msl_high_time}", inline=True)

    # MSL Low
    msl_low = df.loc[df["relative_pressure_msl"].idxmin()]
    msl_low_time = datetime.fromisoformat(msl_low["time"]).strftime("%H:%M")
    embed.add_embed_field(name='MSL Low', value=f"{msl_low['relative_pressure_msl']} hPa at {msl_low_time}", inline=True)

    # set image
    embed.set_image(url='attachment://fig1.png')

    # set footer
    embed.set_footer(text='Made By Ibrahim Mudassar')

    # add embed object to webhook(s)
    for webhook_url in env.list("WEBHOOKS"):
        webhook = DiscordWebhook(url=webhook_url)

        with open("fig1.png", "rb") as f:
            webhook.add_file(file=f.read(), filename='fig1.png')

        webhook.add_embed(embed)
        webhook.execute()


embed_to_discord()
