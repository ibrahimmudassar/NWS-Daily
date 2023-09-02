from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import requests
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables

env = Env()
env.read_env()  # read .env file, if it exists


def embed_to_discord():
    # create embed object for webhook
    embed = DiscordEmbed(title="Precipitation Today!", color="242491")

    # Elevation
    embed.add_embed_field(name='⛰️ Elevation', value=f"{data['elevation']} m")

    # Precip Total but only if precipitation_sum > 0
    if any(elem != 0 for elem in df['precipitation']):
        embed.add_embed_field(
            name='🌧️ Total', value=f"{data['daily']['precipitation_sum'][0]} {data['daily_units']['precipitation_sum']}")

    # Pressure High
    surface_pressure_high = df.loc[df["surface_pressure"].idxmax()]
    surface_pressure_high_time = datetime.fromisoformat(
        surface_pressure_high["time"]).strftime("%H:%M")
    embed.add_embed_field(name='☁️ Pressure ⬆️ High',
                          value=f"{surface_pressure_high['surface_pressure']} hPa at {surface_pressure_high_time}", inline=True)

    # Pressure Low
    surface_pressure_low = df.loc[df["surface_pressure"].idxmin()]
    surface_pressure_low_time = datetime.fromisoformat(
        surface_pressure_low["time"]).strftime("%H:%M")
    embed.add_embed_field(name='☁️ Pressure ⬇️ Low',
                          value=f"{surface_pressure_low['surface_pressure']} hPa at {surface_pressure_low_time}", inline=True)

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

# baseline to measure the difference in on the graph in hPa
STANDARD_PRESSURE = 1013.25

data = requests.get(
    f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={long}&daily=precipitation_sum&hourly=surface_pressure,precipitation&models=best_match&forecast_days=1&timezone=EST").json()

all_categories = {}
for categories in data["hourly"]:
    all_categories[categories] = data["hourly"][categories]
df = pd.DataFrame(all_categories)

fig = go.Figure()


fig.add_trace(go.Scatter(
    x=df['time'],
    y=df['surface_pressure'] - STANDARD_PRESSURE,
    name="Relative Pressure (STP)",
    fill='tozeroy',
))

if any(elem != 0 for elem in df['precipitation']):
    fig.add_trace(go.Scatter(
        x=df['time'],
        y=df['precipitation'],
        name="Precipitation",
        yaxis="y2"
    ))

# Create axis objects
fig.update_layout(
    yaxis=dict(
        title="yaxis title",
        titlefont=dict(
            color="#1f77b4"
        ),
        tickfont=dict(
            color="#1f77b4"
        )
    ),
    yaxis2=dict(
        title="yaxis2 title",
        titlefont=dict(
            color="#ff7f0e"
        ),
        tickfont=dict(
            color="#ff7f0e"
        ),
        anchor="x",
        overlaying="y",
        side="right",
    ),
)

# Labels
fig.update_layout(title={'text': 'Pressure vs. Time', 'x': 0.5, 'xanchor': 'center'},
                  yaxis2_zeroline=True,
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

embed_to_discord()
