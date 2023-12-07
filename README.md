# RSS Newsfeed reader bot for Misskey 😻

This Python bot posts RSS news from your chosen feeds. You can choose the frequency of posting (in minutes) and the amount of Notes to post each time.

Before posting it starts a **sentiment analysis** then flags with CW (Content Warning) and :NSFW: if sentiment is negative. (war, deaths, bad news)

News and Notes flows are asyncronous, so that it can pick up always the fresher news and Note as soon as possible.

Notes will not bloat your Misskey profile, because get deleted if older than a month.

![Artificial Image of a Cat Robot reading news](https://repository-images.githubusercontent.com/523881650/3c833d1a-a012-4414-9b94-aa6e7ec0f98a)

## Setup

Please, follow this instructions once, before starting:

### Create an account on Misskey and get the APIKEY for your bot.

- Get inside your Misskey instance
- Create a new account
- Remember to set `isBot = True`
- Visit the page: `https://your.misskey.instance/settings/api`
- Create a new API-key having at minimum `notes:write` privilege.

### Prepare a Python virtual environment

Please use python3. In latest GNU/Linux distros, it's already in as default. Otherwise you'll need `python3-venv` package with dependencies.

1. `git clone` this repository, to get the source code, or download the zip file
2. `python -m venv .venv` Python sandboxed enviroment creation
3. `. .venv/bin/activate` Environment activation
4. `pip install -r requirements.txt` Dependencies installation
5. `python -m spacy download en_core_web_lg` Gets sentiment analysis data (for NSFW posts)

## Configuration

Now you installed the software, you need a small amount of configuration.

### Fill the bot with RSS feed

First of all, put the RSS Feed source URLS into the file `sources.txt`, line by line.

### Environment variables

Now copy `.env-example` in `.env` file to fill in your personal configuration:

- **HOST** your Misskey domain
- **APIKEY** app's credentials created before
- **VISIBILITY** choose [in which Timeline to post](https://misskey-hub.net/en/docs/features/timeline.html).
- **LOCAL** boolean for federated Notes
- **EVERY_MINUTES** posting frequency
- **HOW_MANY** posted Notes amount

## Run!

Inside your python environment:

`(env) $ python feed_bot.py`

It will setup if needed. Then will start three scheduled jobs.

### Service daemon configuration

You probably want to run it detached from the console by using `nohup` or running into a `screen` command. So that you can close the ssh shell without stopping.

The software has ability to avoid multiple concurrent runs.

## Stop!

To stop it, just press `CTRL+C` in the console.

To exit the Python environment type: `deactivate`. You're aware of activation because of your shell starts with: (env)

## Upgrade

It's super easy, just Stop! Then `git pull` to check for updates. Then `pip-review -a` to update the libraries. Needs a restart to get things done.

## Development

If you plan to contribute, please run this command, after installation noted before.

```bash
pre-commmit install
```
