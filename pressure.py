import requests
from environs import Env  # For environment variables
import datetime
import plotly.express as px
from discord_webhook import DiscordEmbed, DiscordWebhook  # Connect to discord
import pytz


# get the current hour
current_hour = datetime.datetime.now(pytz.timezone('US/Eastern')).hour
# finds the hours between now and midnight
time_differential = 24 - current_hour

# Setting up environment variables
env = Env()
env.read_env()  # read .env file, if it exists

data = requests.get(
    "https://api.openweathermap.org/data/2.5/onecall?lat=40.57&lon=-74.32&units=metric&exclude=minutely,daily&appid=" + env('API_KEY')).json()

# this is a list of hour objects that have data sorted by their pressure
list_of_hours = sorted([data['hourly'][k] for k in range(
    0, time_differential + 1)], key=lambda x: x['pressure'])

low = list_of_hours[0]
high = list_of_hours[-1]


# baseline to measure the difference in on the graph
STANDARD_PRESSURE = 1013.25
margin = 0.25  # margin above and below the highest and lowest values to give some space

# defines the graph
fig = px.line(x=[i for i in range(0, time_differential + 1)],
              y=[data['hourly'][i]['pressure'] -
                  STANDARD_PRESSURE for i in range(0, time_differential + 1)],
              title="Pressure vs. Time",
              labels=dict(x="Time (Now to End of Day in Hours)", y="Difference from STP"))

fig.update_layout(title_x=0.5)  # centers title

# redefines the y axis to include 0 if it doesn't already
if not (high['pressure'] - STANDARD_PRESSURE > 0 and low['pressure'] - STANDARD_PRESSURE < 0):
    if high['pressure'] - STANDARD_PRESSURE < 0:
        fig.update_yaxes(
            range=[(low['pressure'] - STANDARD_PRESSURE) + margin, 0])
    elif low['pressure'] - STANDARD_PRESSURE > 0:
        fig.update_yaxes(
            range=[0, (high['pressure'] - STANDARD_PRESSURE) + margin])

fig.write_image("fig1.png")


def embed_to_discord():
    # Webhooks to send to
    webhook = DiscordWebhook(url=env.list("WEBHOOKS"))

    # create embed object for webhook
    embed = DiscordEmbed(title="Pressure Today", color="242491")

    # Low
    embed.add_embed_field(
        name="Low", value=f"""{low['pressure'] - STANDARD_PRESSURE} hPa In {datetime.datetime.fromtimestamp(low['dt']).hour - current_hour} hours""", inline=False)

    # High
    embed.add_embed_field(
        name="High", value=f"""{high['pressure'] - STANDARD_PRESSURE} hPa In {datetime.datetime.fromtimestamp(high['dt']).hour - current_hour} hours""", inline=False)

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
