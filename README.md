# RSS Newsfeed reader bot for Misskey

This Python bot fetches RSS feeds every 5 minutes. Then "cherry pics" a news at time, each minute. Choosing from the freshest to the older posted.

News and Notes flows are asyncronous, so that it can pick up always the fresher news an Note them as soon as possible.

Notes will not bloat your Misskey profile, because get deleted if older than a month.

## Setup

Please, follow this instructions once, before starting:

### Create an account on Misskey and get the APIKEY for your bot.

- Get inside your Misskey instance
- Create a new account
- Remember to set `isBot = True`
- Visit the page: `https://your.misskey.instance/settings/api`
- Create a new API-key having at minimum `notes:write` privilege.
- copy `.env-example` in `.env` file, fill in your configuration

### Prepare a Python virtual environment 

Please use python3. In latest GNU/Linux distros, it's already in as default. Otherwise you'll need `python3-venv` package with dependencies. 

1. `git clone` this repository, to get the source code, or download the zip file
2. `python -m venv .venv` Python sandboxed enviroment creation
3. `. .venv/bin/activate` Environment activation
4. `pip install -r requirements.txt` Dependencies installation

### Fill the bot with RSS feed

Edit file `sources.txt` and list a RSS url for every line.

## Run!

Inside your python environment:

`(env) $ python feed-bot.py`

It will setup if needed. Then will start three scheduled jobs.

- Fetch RSS every 5 minutes
- Post Notes every minute
- Delete Posted notes older than one month. Hourly.

### Service daemon configuration

You probably want to run it detached from the console by using `nohup` or running into a `screen` command. So that you can close the ssh shell without stopping.

The software has ability to avoid multiple concurrent runs.

## Stop! 

To stop it, just press `CTRL+C` in the console.

To exit the Python environment type: `deactivate`. You're aware of activation because of your shell starts with: (env)

## Upgrade

It's super easy, just Stop! Then `git pull` to check for updates. Then `pip-review -a` to update the libraries. Needs a restart to get things done.