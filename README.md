# NWS-Daily
## Example Outputs

![Embed Example](https://media.discordapp.net/attachments/749403737730187328/1071541462262632638/nws-daily-example.png)


## Overview

This project has expanded from just the radar colelction to pressure graphing as well.

For the [main file](/main.py) I scrape from the NWS webpage and use their textual API as well for added info.

For [pressure graphing](/pressure.py) I get data from OpenWeatherMap and then graph it over time with python plotly. 

## Self-hosting

If you want to run this yourself you're going to need an OpenWeatherMap api key and atleast 1 discord webhook url. If you're not going the webhook route you can fork and use requests to send a post request of your choice.

## TODO
Theres a time conversion problem between UTC and when i print to est which I need to solve. fork and pr to contribute
