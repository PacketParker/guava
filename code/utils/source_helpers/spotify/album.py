import datetime
import discord
import requests
from typing import Tuple, Optional
from requests.exceptions import JSONDecodeError

from utils.config import BOT_COLOR, LOG


async def load(
    headers: dict,
    query: str,
    user: discord.User,
) -> Tuple[Optional[dict], Optional[discord.Embed]]:
    """
    Get the album info from the Spotify API
    """
    album_id = query.split("/album/")[1]

    try:
        # Get the album info
        response = requests.get(
            f"https://api.spotify.com/v1/albums/{album_id}",
            headers=headers,
        )

        if response.status_code == 404:
            embed = discord.Embed(
                title="Album Not Found",
                description=(
                    "The album could not be found as the provided link is"
                    " invalid. Please try again."
                ),
                color=BOT_COLOR,
            )
            return None, embed

        if response.status_code == 401:
            LOG.error(
                "Could not authorize with Spotify API. Likely need to"
                " restart the bot."
            )
            return None, None

        response.raise_for_status()
        # Unpack the album info
        album = response.json()
        name = album["name"]
        artist = album["artists"][0]["name"]
        num_tracks = len(album["tracks"]["items"])
        artwork_url = album["images"][0]["url"]
    except IndexError:
        LOG.error("Failed unpacking Spotify album info")
        return None, None
    except (JSONDecodeError, requests.HTTPError):
        LOG.error("Failed making request to Spotify API")
        return None, None

    embed = discord.Embed(
        title="Album Queued",
        description=(
            f"**{name}** by **{artist}**\n"
            f"` {num_tracks} ` tracks\n\n"
            f"Queued by: {user.mention}"
        ),
        color=BOT_COLOR,
    )
    embed.set_thumbnail(url=artwork_url)
    embed.set_footer(
        text=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") + " UTC"
    )

    return album, embed
