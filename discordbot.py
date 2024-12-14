# -*- coding: utf-8 -*-
import typing
import discord
import os

DISCORD_TOKEN_ENV = "DISCORD_TOKEN"
COUNTING_CHANNEL_ENV = "COUNTING_CHANNEL"
COUNTING_CHANNEL_CHAT_ENV = "COUNTING_CHANNEL_CHAT"


class Client(discord.Client):
    def __init__(
        self,
        counting_channel_id: int,
        counting_channel_chat_id: int,
        *,
        intents: discord.Intents,
    ):
        super().__init__(intents=intents)
        self.locked = False
        self._seen_numbers: set[int] = set()

        self._counting_channel_id = counting_channel_id
        self._counting_channel_chat_id = counting_channel_chat_id
        self._next_expected_number = None
        self._last_sender = None

    async def on_ready(self):
        print(f"Logged in as {self.user}")

        self._counting_channel = await self._get_text_channel_or_assert(
            self._counting_channel_id
        )

        self._counting_channel_chat = await self._get_text_channel_or_assert(
            self._counting_channel_chat_id
        )

        await self._reset()

    async def _reset(self):
        async for message in self._counting_channel.history(limit=None):
            try:
                number = int(message.content)
            except ValueError:
                continue

            self._seen_numbers.add(number)

        async for message in self._counting_channel.history(limit=1):
            self._last_sender = message.author

        expected_numbers = set(range(1, max(self._seen_numbers) + 1))

        assert (expected_numbers == self._seen_numbers) or (
            len(self._seen_numbers) == 0
        ), "COUNTING CHANNEL IS FUCKED"

        self._next_expected_number = max(self._seen_numbers) + 1

        print(
            f"CURRENT NUMBER: { self._next_expected_number}, LAST SENDER {self._last_sender}"
        )

    async def _get_text_channel_or_assert(
        self, channel_id: int
    ) -> discord.TextChannel | typing.NoReturn:
        channel = self.get_channel(channel_id)
        assert isinstance(channel, discord.TextChannel)
        return channel

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return

        if self._last_sender is None:
            return

        if message.channel.id == self._counting_channel_id:
            print("===============================================")
            print(
                f"Author: {message.author.name:<30} | Expected: {self._next_expected_number:<15} | Last Sender: {self._last_sender.name:<30}"
            )
            guild_name = message.guild
            assert guild_name is not None

            counting_channel_chat = self.get_channel(self._counting_channel_chat_id)

            assert isinstance(counting_channel_chat, discord.TextChannel)

            guild = await self.fetch_guild(guild_name.id)
            member = await guild.fetch_member(message.author.id)

            sender_name = member.nick if member.nick is not None else member.name

            try:
                number = int(message.content)
                if message.content.startswith("+"):
                    raise ValueError()
            except ValueError:
                print("Not a number")
                await counting_channel_chat.send(
                    f"{sender_name}... you stupid idiot, learn how to fucking count, dumb piece of shit. That isn't even a number..."
                )
                await counting_channel_chat.send(
                    "https://tenor.com/view/give-a-damn-cat-damn-do-i-give-a-damn-do-i-give-a-damn-cat-gif-25163635"
                )
                await message.delete()
                return

            print(f"Rx'd {number:<20}")

            if message.author == self._last_sender:
                print("Duplicate Sender")
                await counting_channel_chat.send(
                    f"{sender_name.upper()} YOU COUNTED AN EXTRA TIME SO IT DOESNT COUNT"
                )
                await message.delete()

            elif number in self._seen_numbers:
                print("Duplicate Number")
                await counting_channel_chat.send(
                    f"{sender_name.upper()} POSTED A DUPLICATE {number}. LAUGH AT THEM"
                )

                try:
                    await message.delete()
                except discord.errors.Forbidden:
                    print("Could not delete message")

            elif number != self._next_expected_number:
                print("Wrong Number")
                await counting_channel_chat.send(
                    f"{sender_name.upper()} DOESNT KNOW HOW TO COUNT"
                )

                try:
                    await message.delete()
                except discord.errors.Forbidden:
                    print("Could not delete message")
            else:
                print("Correct Number")
                assert self._next_expected_number
                self._last_sender = message.author
                self._seen_numbers.add(number)
                self._next_expected_number += 1


def main():

    DISCORD_TOKEN = os.getenv(DISCORD_TOKEN_ENV)
    COUNTING_CHANNEL = os.getenv(COUNTING_CHANNEL_ENV)
    COUNTING_CHANNEL_CHAT = os.getenv(COUNTING_CHANNEL_CHAT_ENV)

    assert DISCORD_TOKEN is not None

    assert COUNTING_CHANNEL is not None

    counting_channel_id = int(COUNTING_CHANNEL)

    assert COUNTING_CHANNEL_CHAT is not None

    counting_channel_chat_id = int(COUNTING_CHANNEL_CHAT)

    intents = discord.Intents.default()
    intents.message_content = True
    client = Client(counting_channel_id, counting_channel_chat_id, intents=intents)
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
