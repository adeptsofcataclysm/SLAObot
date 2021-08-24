import discord

client = discord.Client()


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run('ODczMjE2MDU3MDc3Mjg5MDQw.YQ1L0w.IWJ0mm1W9jJtpKLHawrE1hlz5Zc')
