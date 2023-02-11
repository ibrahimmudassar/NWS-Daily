from datetime import datetime, timedelta

import plotly.graph_objects as go
import pytz
import requests
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
from environs import Env  # For environment variables

env = Env()
env.read_env()  # read .env file, if it exists

data = requests.get(
    "https://api.openweathermap.org/data/2.5/onecall?lat=40.57&lon=-74.32&units=metric&exclude=minutely,daily&appid=" + env("API_KEY")).json()

now = datetime.now(pytz.timezone('US/Eastern'))


# baseline to measure the difference in on the graph in hPa
STANDARD_PRESSURE = 1013.25

# get the current hour
pressure_all_day = {}

for weather_by_hour in data['hourly']:
    hour = datetime.fromtimestamp(weather_by_hour['dt'])
    if hour.date() == now.date():
        print(hour)
        pressure_all_day[hour] = weather_by_hour['pressure'] - \
            STANDARD_PRESSURE

# for weather_by_hour in data['hourly']:
#     hour = pytz.timezone(tz_string).localize(
#         datetime.fromtimestamp(weather_by_hour['dt']))
#     print(hour)
#     if hour.date() < tomorrow.date():
#         pressure_all_day[hour] = weather_by_hour['pressure'] - \
#             STANDARD_PRESSURE

hi = max(pressure_all_day, key=lambda x: pressure_all_day[x])
lo = min(pressure_all_day, key=lambda x: pressure_all_day[x])


fig = go.Figure()

fig.add_trace(go.Scatter(
              x=list(pressure_all_day.keys()),
              y=list(pressure_all_day.values()),
              fill='tozeroy',
              mode='lines'
              ))

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

fig.write_image("fig1.png")


def embed_to_discord():
    # Webhooks to send to
    webhook = DiscordWebhook(url=env.list("WEBHOOKS"))

    # create embed object for webhook
    embed = DiscordEmbed(title="Pressure Today", color="242491")

    # High
    embed.add_embed_field(
        name="High", value=f"""{pressure_all_day[hi]} hPa at {hi.strftime("%H:%M")}""", inline=False)

    # Low
    embed.add_embed_field(
        name="Low", value=f"""{pressure_all_day[lo]} hPa at {lo.strftime("%H:%M")}""", inline=False)

    # set image
    with open("fig1.png", "rb") as f:
        webhook.add_file(file=f.read(), filename='fig1.png')
    embed.set_image(url='attachment://fig1.png')

    # set thumbnail
    embed.set_thumbnail(
        url='http://openweathermap.org/img/wn/' + data['current']['weather'][0]['icon'] + '@4x.png')

    # set footer
    embed.set_footer(text='Made By Ibrahim Mudassar')

    # add embed object to webhook(s)
    webhook.add_embed(embed)
    webhook.execute()


embed_to_discord()
