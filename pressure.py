import requests
from environs import Env  # For environment variables
import datetime
import plotly.express as px
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord


# get the current hour
current_hour = datetime.datetime.now().hour
# finds the hours between now and midnight
time_differential = 24 - current_hour

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists

data = requests.get(
    "https://api.openweathermap.org/data/2.5/onecall?lat=40.57&lon=-74.32&units=metric&exclude=minutely,daily&appid=" + env('API_KEY')).json()

# find the highest pressure point (takes the object so i can extract the time at that pressure)
high = data['hourly'][0]
for i in range(0, time_differential + 1):
    if data['hourly'][i]['pressure'] > high['pressure']:
        high = data['hourly'][i]


# find the lowest pressure point (takes the object so i can extract the time at that pressure)
low = data['hourly'][0]
for i in range(0, time_differential + 1):
    if data['hourly'][i]['pressure'] < low['pressure']:
        low = data['hourly'][i]

# defines the graph
fig = px.line(x=[i for i in range(0, time_differential + 1)],
              y=[data['hourly'][i]['pressure'] -
                  1013.25 for i in range(0, time_differential + 1)],
              title="Pressure vs. Time",
              labels=dict(x="Time (In Hours Since)", y="Difference from STP"))

# redefnes the y axis to include 0 if it doesn't already
if not (high['pressure'] - 1013.25 > 0 and low['pressure'] - 1013.25 < 0):
    if high['pressure'] - 1013.25 < 0:
        fig.update_yaxes(range=[low['pressure'] - 1013.25, 0])
    elif low['pressure'] - 1013.25 > 0:
        fig.update_yaxes(range=[0, high['pressure'] - 1013.25])

fig.write_image("fig1.png")


def embed_to_discord():
    # Webhooks to send to
    webhook = DiscordWebhook(url=env.list("WEBHOOKS"))

    # create embed object for webhook
    embed = DiscordEmbed(title="Pressure Today", color="242491")

    # Low
    embed.add_embed_field(
        name="Low", value=f"""{low['pressure'] - 1013.25} hPa In {datetime.datetime.fromtimestamp(low['dt']).hour - current_hour} hours""", inline=False)

    # High
    embed.add_embed_field(
        name="High", value=f"""{high['pressure'] - 1013.25} hPa In {datetime.datetime.fromtimestamp(high['dt']).hour - current_hour} hours""", inline=False)

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
