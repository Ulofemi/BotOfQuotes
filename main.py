import discord
from discord.ext import commands
from discord.utils import get
import os
import time
import random
import typing
import logging
import json
import logging.config


############################
# Variables
############################
projectDir = '/home/pi/pipy_bot/'
quotesDir = 'quote'
seperator = '/'

TOKEN = 'TOPSECRET'
BOT_PREFIX = '"'
bot = commands.Bot(command_prefix=BOT_PREFIX)
############################
# Functions
############################
def getRandomList(lowLimit=0, highLimit=10, count=1):
    result = []

    for i in range(0, count):
        sw = False
        a = random.randint(lowLimit, highLimit)

        if a in result:
            sw = True
        else:
            result.append(a)

        while sw:
            a = random.randint(lowLimit, highLimit)
            if a in result:
                pass
            else:
                sw = False
                result.append(a)

    return result


def getSubdirs():
    subdirs = [x[0] for x in os.walk(projectDir + quotesDir)]

    genres = []
    for sdir in subdirs:
        genres.append(sdir.split(seperator)[-1])
    genres.remove(quotesDir)
    return genres


def getQuotes(sdir):
    #check if exist!!!

    listOfQuotes = []
    for root, dirs, files in os.walk(projectDir + quotesDir + seperator + sdir):
        for filename in files:
            listOfQuotes.append(projectDir + quotesDir + seperator + sdir + seperator + filename)

    return listOfQuotes


def setup_logging(
    default_path=projectDir + 'logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'
):
    """
    Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

setup_logging()

logger = logging.getLogger(__name__)
logger.info('Start Yo!')

############################
# bot Start
############################
@bot.event
async def on_ready():
    #print('Logged in as: ' + bot.user.name + '\n Simply type "help to get more Information about this awesome Bot')
    logger.info('Logged in as: ' + bot.user.name)


@bot.command(name='join', pass_context=True, aliases=['j', 'joi'], help='The Bot will join your Channel!')
async def join(ctx):
    logger.info('try to join a channel')
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()

    """
    await voice.disconnect()

    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        print(f"The bot has connected to {channel}\n")
    """
    await ctx.send(f"Joined {channel}")
    logger.info(f"Joined {channel}")


    voice = get(bot.voice_clients, guild=ctx.guild)

    voice.play(discord.FFmpegPCMAudio(projectDir + 'start.mp3'), after=lambda e: print("Quote done!"))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.volume = 0.7




@bot.command(name='leave', pass_context=True, aliases=['l', 'lea'], help='The Bot will leave his Channel :-(')
async def leave(ctx):
    logger.info('try to leave a channel')
    channel = ctx.message.author.voice.channel
    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_connected():
        await voice.disconnect()
        #print(f"The bot has left {channel}")
        await ctx.send(f"Left {channel}")
        logger.info(f"Left {channel}")
    else:
        #print("Bot was told to leave voice channel, but was not in one")
        await ctx.send("Don't think I am in a voice channel")
        logger.info("Don't think I am in a voice channel")


@bot.command(name='play', pass_context=True, aliases=['p', 'pla'], help='Play one Quote. \n You can specify the genre [{}] by typing >> "play [genre] <<'.format(getSubdirs()))
async def play(ctx, genre: typing.Optional[str] = 'random'):
    logger.info("Try to play a Quote")
    #print(genre)
    #getting List of genres
    genres = getSubdirs()
    #check genre...
    if genre.lower() in genres or genre is 'random':
        logger.debug('Genre: {}'.format(genre))
        #richtige Eingabe --> Zitat ausgeben
        if genre is 'random':
            genre = genres[random.randint(0, len(genres) - 1)]
            logger.debug('Genre random --> {}'.format(genre))
        #print(genre)

        quotes = getQuotes(genre.lower())
        quote = quotes[random.randint(0, len(quotes) - 1)]
        await ctx.send("Getting everything ready now 🚀")
        voice = get(bot.voice_clients, guild=ctx.guild)

        voice.play(discord.FFmpegPCMAudio(quote), after=lambda e: print("Quote done!"))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.7
        #print("playing\n")
    else:
        await ctx.send("{} gibt es noch nicht! Folgende Genres stehen zu verfügung {}".format(genre, genres))
        logger.debug('Wrong genre')



@bot.command(name='play_infinity', pass_context=True, aliases=['pi', 'inf'], help='Playing many Quotes... Actually it will never end! \n You can specify the genre [{}] by typing >> "play_infinity [genre] <<'.format(getSubdirs()))
async def play_infinity(ctx, genre: typing.Optional[str] = 'random'):
    logger.info("Try to play infinity Quotes")
    sw = False
    tmpQuotes = []

    def playAgain(count):
        counter = count
        #print(counter)
        if counter % 2 == 0:
            logger.debug('counter = {} --> get q quote'.format(counter))
            voice = get(bot.voice_clients, guild=ctx.guild)
            if len(quotes) == 0:
                logger.debug('quotes is empty... lets refill it')
                #print('test')
                for x in tmpQuotes:
                    quotes.append(x)
                tmpQuotes.clear()
                file = quotes[random.randint(0, len(quotes) - 1)]
                tmpQuotes.append(file)
                quotes.remove(file)
            else:
                file = quotes[random.randint(0, len(quotes))]
                tmpQuotes.append(file)
                quotes.remove(file)

            #print('ZitatListe länge: {}'.format(len(quotes)))
            #print('ZitatListe länge: {}'.format(len(tmpQuotes)))
            voice.play(discord.FFmpegPCMAudio(file), after=lambda e: playAgain(counter + 1))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.7
        else:
            logger.debug('counter = {} --> get silence'.format(counter))
            voice = get(bot.voice_clients, guild=ctx.guild)
            file = projectDir + 'silence_030.mp3'
            voice.play(discord.FFmpegPCMAudio(file), after=lambda e: playAgain(counter + 1))
            voice.source = discord.PCMVolumeTransformer(voice.source)
            voice.source.volume = 0.7


    # print(genre)
    # getting List of genres
    genres = getSubdirs()
    # check genre...
    if genre.lower() in genres or genre is 'random':
        # richtige Eingabe --> Zitat ausgeben
        if genre is 'random':
            genre = genres[random.randint(0, len(genres) - 1)]
            logger.debug('Genre random --> {}'.format(genre))
        #print(genre)

        quotes = getQuotes(genre.lower())
        quote = quotes[random.randint(0, len(quotes) - 1)]
        tmpQuotes.append(quote)
        quotes.remove(quote)
        await ctx.send("Getting everything ready 🚀🚀🚀".format(genre))
        voice = get(bot.voice_clients, guild=ctx.guild)

        voice.play(discord.FFmpegPCMAudio(quote), after=lambda e: playAgain(1))
        voice.source = discord.PCMVolumeTransformer(voice.source)
        voice.source.volume = 0.7
        #print("playing\n")
    else:
        await ctx.send("{} gibt es noch nicht! Folgende Genres stehen zu verfügung {}".format(genre, genres))
        logger.debug('Wrong genre')




@bot.command(name='pause', pass_context=True, aliases=['pa', 'pau'], help='Pause current Quote...')
async def pause(ctx):
    logger.info('Try to pause')

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        #print("Music paused")
        voice.pause()
        await ctx.send("Music paused")
        logger.debug('music paused')

    else:
        #print("Music not playing failed pause")
        await ctx.send("Music not playing failed pause")
        logger.debug('music not playing')


@bot.command(name='resume', pass_context=True, aliases=['r', 'res'], help='...resume current Quote.')
async def resume(ctx):
    logger.info('Try to resume')

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_paused():
        #print("Resumed music")
        voice.resume()
        await ctx.send("Resumed music")
        logger.debug('music resumed')
    else:
        #print("Music is not paused")
        await ctx.send("Music is not paused")
        logger.debug('music not paused')


@bot.command(name='skip', pass_context=True, aliases=['s', 'sk'], help='Skip current Quote.')
async def skip(ctx):
    logger.info('Try to skip')

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        #print("Playing next title!")
        voice.stop()
        await ctx.send("Playing next title!")
        logger.debug('music skipped')

    else:
        #print("No music playing failed to skip")
        await ctx.send("No music playing failed to skip")
        logger.debug('music not playing, failed to skip')


@bot.command(name='stop', pass_context=True, aliases=['st', 'sto'], help='Stop!')
async def stop(ctx):
    logger.info('Try to stop')

    voice = get(bot.voice_clients, guild=ctx.guild)

    if voice and voice.is_playing():
        await voice.disconnect()
        logger.debug('music stopped by disconnecting voice')

    else:
        #print("No music playing failed to Stop")
        await ctx.send("No music playing failed to Stop")
        logger.debug('No music playing')

"""
@bot.command(pass_context=True)
async def hlp(ctx):
    await ctx.send('''🚀🚀🚀 STROMBERG ZITATE 🚀🚀🚀
    \n Starte Den Befehl mit einem >> " << 
    \n join --> Der Bot kommt zu dir in den Sprachchannel
    \n leave --> Der Bot verlässt den Sprachchannel
    \n play --> Ein Zitat wird abgespielt 
    \n inf --> Alle Zitate werden abgespielt
    \n skip --> Nächstes Zitat
    \n pause --> Pausieren
    \n resume --> Weiter gehts''')
"""


############################
# bot End
############################
bot.run(TOKEN)
