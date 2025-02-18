from lavalink import LoadType
import re

from utils.config import AI_CLIENT, AI_MODEL


async def add_song_recommendations(
    bot_user, player, number, inputs, retries: int = 1
):
    input_list = [f'"{song} by {artist}"' for song, artist in inputs.items()]

    completion = (
        AI_CLIENT.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
                        Given an input list of songs formatted as ["song_name
                        by artist_name", "song_name by artist_name", ...], generate
                        a list of 5 new songs that the user may enjoy based on
                        the input.

                        Thoroughly analyze each song in the input list, considering
                        factors such as tempo, beat, mood, genre, lyrical themes,
                        instrumentation, and overall meaning. Use this analysis to
                        recommend 5 songs that closely align with the user's musical
                        preferences.

                        The output must be formatted in the exact same way:
                        ["song_name by artist_name", "song_name by artist_name", ...].

                        If you are unable to find 5 new songs or encounter any issues,
                        return the following list instead: ["NOTHING_FOUND"]. Do
                        not return partial results—either provide 5 songs or return
                        ["NOTHING_FOUND"]. Ensure accuracy in song and artist names.

                        DO NOT include any additional information or text in the
                        output, it should STRICTLY be either a list of the songs
                        or ["NOTHING_FOUND"].
                    """,
                },
                {
                    "role": "user",
                    "content": f"""
                        {input_list}
                    """,
                },
            ],
            model=AI_MODEL,
        )
        .choices[0]
        .message.content.strip()
        .strip('"')
    )

    # Sometimes ChatGPT will return `["NOTHING FOUND"]` even if it should
    # have found something, so we check each prompt up to 3 times before
    # giving up.
    if completion == '["NOTHING FOUND"]':
        if retries <= 3:
            await add_song_recommendations(
                bot_user, player, number, inputs, retries + 1
            )
        else:
            return False

    else:
        # Clean up the completion string to remove any potential issues
        # with the eval function (e.g. OUTPUT: prefix, escaped quotes, etc.)
        completion = re.sub(r"[\\\'\[\]\n]+|OUTPUT: ", "", completion)

        for entry in eval(completion):
            song, artist = entry.split(" by ")
            ytsearch = f"ytsearch:{song} by {artist} audio"
            results = await player.node.get_tracks(ytsearch)

            if (
                not results
                or not results.tracks
                or not results.load_type
                or results.load_type
                in (
                    LoadType.EMPTY,
                    LoadType.ERROR,
                )
            ):
                dzsearch = f"dzsearch:{song}"
                results = await player.node.get_tracks(dzsearch)

                if (
                    not results
                    or not results.tracks
                    or not results.load_type
                    or results.load_type
                    in (
                        LoadType.EMPTY,
                        LoadType.ERROR,
                    )
                ):
                    continue

            track = results.tracks[0]
            player.add(requester=bot_user, track=track)

        return True
