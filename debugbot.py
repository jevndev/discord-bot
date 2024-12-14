# -*- coding: utf-8 -*-
import os
import discord
from rich import print

DISCORD_TOKEN_ENV = "DISCORD_TOKEN"


class Client(discord.Client):
    def __init__(
        self,
        *,
        intents: discord.Intents,
    ):
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"Logged in as {self.user}")

    async def on_message(self, message: discord.Message):
        print(f"""{message}""")


def main():
    intents = discord.Intents.default()
    intents.message_content = True

    DISCORD_TOKEN = os.getenv(DISCORD_TOKEN_ENV)
    assert (
        DISCORD_TOKEN is not None
    ), f"Environment variable {DISCORD_TOKEN_ENV} is required"

    client = Client(intents=intents)
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
