import jsonschema
import re
import os
import yaml
import validators
import openai
import sys
import discord
import logging
import requests
from groq import Groq
from colorlog import ColoredFormatter

log_level = logging.DEBUG
log_format = (
    "  %(log_color)s%(levelname)-8s%(reset)s |"
    " %(log_color)s%(message)s%(reset)s"
)

logging.root.setLevel(log_level)
formatter = ColoredFormatter(log_format)

stream = logging.StreamHandler()
stream.setLevel(log_level)
stream.setFormatter(formatter)

LOG = logging.getLogger("pythonConfig")
LOG.setLevel(log_level)
LOG.addHandler(stream)

TOKEN = None
BOT_COLOR = None
BOT_INVITE_LINK = None
FEEDBACK_CHANNEL_ID = None
BUG_CHANNEL_ID = None
LOG_SONGS = False
YOUTUBE_SUPPORT = False
SPOTIFY_CLIENT_ID = None
SPOTIFY_CLIENT_SECRET = None
GENIUS_CLIENT_ID = None
GENIUS_CLIENT_SECRET = None
AI_CLIENT = None
AI_MODEL = None
LAVALINK_HOST = None
LAVALINK_PORT = None
LAVALINK_PASSWORD = None
YOUTUBE_BROKEN = False

schema = {
    "type": "object",
    "properties": {
        "bot_info": {
            "type": "object",
            "properties": {
                "token": {"type": "string"},
                "bot_color": {"type": "string"},
                "bot_invite_link": {"type": "string"},
                "feedback_channel_id": {"type": "integer"},
                "bug_channel_id": {"type": "integer"},
                "log_songs": {"type": "boolean"},
            },
            "required": ["token"],
        },
        "youtube": {
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean"},
            },
            "required": ["enabled"],
        },
        "spotify": {
            "type": "object",
            "properties": {
                "spotify_client_id": {"type": "string"},
                "spotify_client_secret": {"type": "string"},
            },
            "required": ["spotify_client_id", "spotify_client_secret"],
        },
        "genius": {
            "type": "object",
            "properties": {
                "genius_client_id": {"type": "string"},
                "genius_client_secret": {"type": "string"},
            },
            "required": ["genius_client_id", "genius_client_secret"],
        },
        "ai": {
            "type": "object",
            "properties": {
                "service": {"enum": ["openai", "groq"]},
                "api_key": {"type": "string"},
            },
            "required": ["service"],
        },
        "lavalink": {
            "type": "object",
            "properties": {
                "host": {"type": "string"},
                "port": {"type": "integer"},
                "password": {"type": "string"},
            },
            "required": ["host", "port", "password"],
        },
    },
    "required": ["bot_info", "lavalink"],
}


# Attempt to load the config file, otherwise create a new template
def load_config():
    if os.path.exists("/.dockerenv"):
        file_path = "/config/config.yaml"
    else:
        file_path = "config.yaml"

    try:
        with open(file_path, "r") as f:
            file_contents = f.read()
            validate_config(file_contents)

    except FileNotFoundError:
        # Create a new config.yaml file with the template
        with open(file_path, "w") as f:
            f.write(
                """
bot_info:
    token: 
    bot_color: 
    bot_invite_link: 
    feedback_channel_id: 
    bug_channel_id: 
    log_songs: true

lavalink:
    host: 
    port: 
    password: 

youtube:
    enabled: false

spotify:
    spotify_client_id: 
    spotify_client_secret: 

genius:
    genius_client_id: 
    genius_client_secret: 

ai:
    service: 
    api_key: """
            )

        sys.exit(
            LOG.critical(
                "Configuration file `config.yaml` has been generated. Please"
                " fill out all of the necessary information. Refer to the docs"
                " for information on what a specific configuration option is."
            )
        )


# Thouroughly validate all of the options in the config.yaml file
def validate_config(file_contents):
    global TOKEN, BOT_COLOR, BOT_INVITE_LINK, FEEDBACK_CHANNEL_ID, BUG_CHANNEL_ID, LOG_SONGS, YOUTUBE_SUPPORT, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, GENIUS_CLIENT_ID, GENIUS_CLIENT_SECRET, AI_CLIENT, AI_MODEL, LAVALINK_HOST, LAVALINK_PORT, LAVALINK_PASSWORD, YOUTUBE_BROKEN
    config = yaml.safe_load(file_contents)

    try:
        jsonschema.validate(config, schema)
    except jsonschema.ValidationError as e:
        sys.exit(LOG.critical(f"Error in config.yaml file: {e.message}"))

    #
    # Begin validation for optional BOT_INFO values
    #

    # If there is a "bot_invite_link" option, make sure it's a valid URL
    if "bot_invite_link" in config["bot_info"]:
        if not validators.url(config["bot_info"]["bot_invite_link"]):
            LOG.critical(
                "Error in config.yaml file: bot_invite_link is not a valid URL"
            )
        else:
            BOT_INVITE_LINK = config["bot_info"]["bot_invite_link"]

    # Make sure "bot_color" is a valid hex color
    hex_pattern_one = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    hex_pattern_two = "^([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"

    if "bot_color" in config["bot_info"]:
        if not bool(
            re.match(hex_pattern_one, config["bot_info"]["bot_color"])
        ) and not bool(
            re.match(hex_pattern_two, config["bot_info"]["bot_color"])
        ):
            LOG.critical(
                "Error in config.yaml file: bot_color is not a valid hex color"
            )
        else:
            BOT_COLOR = discord.Color(
                int((config["bot_info"]["bot_color"]).replace("#", ""), 16)
            )

    # Make sure "feedback_channel_id" and "bug_channel_id" are exactly 19 characters long
    if "feedback_channel_id" in config["bot_info"]:
        if len(str(config["bot_info"]["feedback_channel_id"])) != 0:
            if len(str(config["bot_info"]["feedback_channel_id"])) != 19:
                LOG.critical(
                    "Error in config.yaml file: feedback_channel_id is not a"
                    " valid Discord channel ID"
                )
            else:
                FEEDBACK_CHANNEL_ID = config["bot_info"]["feedback_channel_id"]

    if "bug_channel_id" in config["bot_info"]:
        if len(str(config["bot_info"]["bug_channel_id"])) != 0:
            if len(str(config["bot_info"]["bug_channel_id"])) != 19:
                LOG.critical(
                    "Error in config.yaml file: bug_channel_id is not a valid"
                    " Discord channel ID"
                )
            else:
                BUG_CHANNEL_ID = config["bot_info"]["bug_channel_id"]

    if "log_songs" in config["bot_info"]:
        LOG_SONGS = bool(config["bot_info"]["log_songs"])

    # Check for YouTube support
    if "youtube" in config:
        YOUTUBE_SUPPORT = bool(config["youtube"]["enabled"])

    #
    # If the SPOTIFY section is present, make sure the client ID and secret are valid
    #

    if "spotify" in config:
        auth_url = "https://accounts.spotify.com/api/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": config["spotify"]["spotify_client_id"],
            "client_secret": config["spotify"]["spotify_client_secret"],
        }
        response = requests.post(auth_url, data=data)
        if response.status_code == 200:
            SPOTIFY_CLIENT_ID = config["spotify"]["spotify_client_id"]
            SPOTIFY_CLIENT_SECRET = config["spotify"]["spotify_client_secret"]
        else:
            LOG.critical(
                "Error in config.yaml file: Spotify client ID or secret is"
                " invalid"
            )

    #
    # If the GENIUS section is present, make sure the client ID and secret are valid
    #

    if "genius" in config:
        auth_url = "https://api.genius.com/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": config["genius"]["genius_client_id"],
            "client_secret": config["genius"]["genius_client_secret"],
        }
        response = requests.post(auth_url, data=data)
        if response.status_code == 200:
            GENIUS_CLIENT_ID = config["genius"]["genius_client_id"]
            GENIUS_CLIENT_SECRET = config["genius"]["genius_client_secret"]
        else:
            LOG.critical(
                "Error in config.yaml file: Genius client ID or secret is"
                " invalid"
            )

    #
    # If the AI section is present, make sure the API key is valid
    #

    if "ai" in config:
        if config["ai"]["service"] == "openai":
            client = openai.OpenAI(api_key=config["ai"]["api_key"])
            model = "gpt-4o-mini"
        elif config["ai"]["service"] == "groq":
            client = Groq(api_key=config["ai"]["api_key"])
            model = "llama-3.3-70b-specdec"

        try:
            client.models.list()
            AI_CLIENT = client
            AI_MODEL = model
        except openai.AuthenticationError:
            LOG.critical(
                "Error in config.yaml file: OpenAI/Groq API key is invalid"
            )

    # Set appropriate values for all non-optional variables
    TOKEN = config["bot_info"]["token"]
    LAVALINK_HOST = config["lavalink"]["host"]
    LAVALINK_PORT = config["lavalink"]["port"]
    LAVALINK_PASSWORD = config["lavalink"]["password"]

    YOUTUBE_BROKEN = False


"""
Template for embeds
"""


def create_embed(
    title: str = None,
    description: str = None,
    color=None,
    footer=None,
    thumbnail=None,
):
    embed = discord.Embed(
        title=title,
        description=description,
        color=color if color else BOT_COLOR,
    )

    if footer:
        embed.set_footer(text=footer)
    # else:
    #     embed.set_footer(
    #         text=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    #     )

    if thumbnail:
        embed.set_thumbnail(url=thumbnail)

    return embed
