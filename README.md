# NWS-Daily
## Example Outputs

![Embed Example 1](https://github.com/ibrahimmudassar/NWS-Daily/assets/22484328/8b21920a-06f9-465d-b4ed-a26478d89877)

![Embed Example 2](https://github.com/ibrahimmudassar/NWS-Daily/assets/22484328/9bf50e0c-f58c-459f-87ae-30cdad2030dd)


## Overview

This project has expanded from just the radar collection to precipitation graphing as well.

For the [main file](/main.py) I scrape from the NWS webpage and use their textual API as well for added info.

For [pressure graphing](/pressure.py) I get data from [Open-Meteo](https://open-meteo.com/) and then graph it over time with python plotly. 

## Self-hosting

If you want to run this yourself you're going to need atleast 1 discord webhook url. If you're not going the webhook route you can fork and use requests to send a post request of your choice or display the products otherwise.
