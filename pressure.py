import requests
from environs import Env  # For environment variables
from datetime import datetime
import plotly.graph_objects as go
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
import pytz

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists

data = requests.get(
    "https://api.openweathermap.org/data/2.5/onecall?lat=40.57&lon=-74.32&units=metric&exclude=minutely,daily&appid=" + env('API_KEY')).json()

# get the current hour
current_hour = datetime.now(pytz.timezone('US/Eastern'))
# finds the hours between now and midnight
time_differential = 24 - current_hour.hour

# this is a list of hour objects that have data sorted by their pressure
list_of_hours = sorted([data['hourly'][k] for k in range(
    0, time_differential + 1)], key=lambda x: x['pressure'])

low = list_of_hours[0]
high = list_of_hours[-1]


# baseline to measure the difference in on the graph in hPa
STANDARD_PRESSURE = 1013.25

fig = go.Figure()

fig.add_trace(go.Scatter(
              x=[i for i in range(0, time_differential + 1)],
              y=[data['hourly'][i]['pressure'] -
                 STANDARD_PRESSURE for i in range(0, time_differential + 1)],
              fill='tozeroy',
              mode='lines'
              ))

fig.update_yaxes(ticklabelstep=2)

# Labels
fig.update_layout(title={'text': 'Pressure vs. Time', 'x': 0.5, 'xanchor': 'center'},
                  yaxis_zeroline=True,
                  xaxis_zeroline=True,
                  xaxis_title="Time (In Hours Since)",
                  yaxis_title="Difference from STP (In hPa)")

# Attribution
fig.add_annotation(text="By: Ibrahim Mudassar",
                   xref="paper", yref="paper",
                   x=1, y=-0.14,
                   showarrow=False,
                   align="center",
                   font=dict(size=9))


fig.write_image("fig1.png")


high_time_absolute = pytz.timezone(
    'UTC').localize(datetime.fromtimestamp(high['dt']))  # takes the UTC Time and makes it timezone aware
high_time_relative = high_time_absolute - current_hour
# rounded to the nearest hour
high_time_relative = round(high_time_relative.total_seconds() / 3600)


low_time_absolute = pytz.timezone(
    'UTC').localize(datetime.fromtimestamp(low['dt']))  # takes the UTC Time and makes it timezone aware
low_time_relative = low_time_absolute - current_hour
# rounded to the nearest hour
low_time_relative = round(low_time_relative.total_seconds() / 3600)


def embed_to_discord():
    # Webhooks to send to
    webhook = DiscordWebhook(url=env.list("WEBHOOKS"))

    # create embed object for webhook
    embed = DiscordEmbed(title="Pressure Today", color="242491")

    # Low
    embed.add_embed_field(
        name="Low", value=f"""{low['pressure'] - STANDARD_PRESSURE} hPa In {low_time_relative} hours""", inline=False)

    # High

    embed.add_embed_field(
        name="High", value=f"""{high['pressure'] - STANDARD_PRESSURE} hPa In {high_time_relative} hours""", inline=False)

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
