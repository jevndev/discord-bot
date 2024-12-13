# -*- coding: utf-8 -*-
import discord
import os

DISCORD_TOKEN_ENV = "DISCORD_TOKEN"
COUNTING_CHANNEL_ENV = "COUNTING_CHANNEL"
COUNTING_CHANNEL_CHAT_ENV = "COUNTING_CHANNEL_CHAT"

class Client(discord.Client):
    def __init__(self, counting_channel_id: int, counting_channel_chat_id: int,  *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.locked = False
        self.seen_numbers: set[int] = set()

        self.counting_channel_id = counting_channel_id
        self.counting_channel_chat_id = counting_channel_chat_id


    async def on_ready(self):
        print(f"Logged in as {self.user}")

        # load all numbers already seen in counting channel
        counting_channel = self.get_channel(self.counting_channel_id)
        assert isinstance(counting_channel, discord.TextChannel)
        async for message in counting_channel.history(limit=None):
            try:
                number = int(message.content)
            except ValueError:
                continue

            self.seen_numbers.add(number)

        print("SEEN messages: ", self.seen_numbers)

    async def on_message(self, message: discord.Message) -> None:
        if message.author == self.user:
            return

        print(f"New message from {message.author}: {message.channel.id}")

        if message.channel.id == self.counting_channel_id:
            guild_name = message.guild
            assert guild_name is not None

            counting_channel_chat = self.get_channel(self.counting_channel_chat_id)

            assert isinstance(counting_channel_chat, discord.TextChannel)

            guild = await self.fetch_guild(guild_name.id)
            member = await guild.fetch_member(message.author.id)

            sender_name = member.nick if member.nick is not None else member.name

            try:
                number = int(message.content)
            except ValueError:
                await counting_channel_chat.send(f"{sender_name}... you stupid idiot, learn how to fucking count, dumb piece of shit...")
                await counting_channel_chat.send("https://tenor.com/view/give-a-damn-cat-damn-do-i-give-a-damn-do-i-give-a-damn-cat-gif-25163635")
                await message.delete()
                return

            if number in self.seen_numbers:
                await counting_channel_chat.send(f"{sender_name.upper()} POSTED A DUPLICATE {number}. LAUGH AT THEM")

                try:
                    await message.delete()
                except discord.errors.Forbidden:
                    print("Could not delete message")

            self.seen_numbers.add(number)





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
