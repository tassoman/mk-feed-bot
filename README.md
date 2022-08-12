# RSS Newsfeed reader bot for Misskey

mk-feed-bot is written in Python, based on _feedparser_ and _Misskey.py_ libs.

## Setup

Follow this instructions:

### Create an account and its APIKEY for your bot.

- Get inside your Misskey instance
- Create a new account
- Remember to set `isBot = True`
- Visit the page: `https://your.misskey.instance/settings/api`
- Create a new API-key having `notes:write` privilege.
- copy `.env-example` in `.env` file and put the key in

### Prepare a Python virtual environment 

Please use python3. In latest GNU/Linux distros, it's already in as default. Otherwise you'll need `python3-venv` package with dependencies. 

1. `python -m venv env` Python sandboxed enviroment creation
2. `. env/bin/activate` Python environment activation
3. `pip install -r requirements.txt` Dependencies installation
4. `cp feedbot.sqlite-EXAMPLE feedbot.sqlite` Database creation

To exit the environment type: `deactivate` . You're aware of activation because of your shell starts with: (env)

### Fill the bot with RSS feed

Edit the dictionary variable: `sourceList` inside `feed-bot.py`

## Run!

Inside your python environment:

`(env) $ python feed-bot.py`

### Service daemon configuration

You can run detached from the console using `nohup` or running into a `screen` command.

To stop it, just remove the pid file: `$ rm feedbot.pid` 
