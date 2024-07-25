#narukami/bot.py | Кодил: резвоф | Открытый исходный код. Telegram channel: https://t.me/rezvof | GitHub: https://github.com/rezvoff

import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import dotenv
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True
bot = commands.Bot(command_prefix=',', intents=intents, help_command=None) #префикс

activities = [
    discord.Activity(type=discord.ActivityType.playing, name="/помощь - вопрос")
]

async def load_cogs_recursively(directory):
    for filename in os.listdir(directory):
        path = os.path.join(directory, filename)
        if filename.endswith('.py') and filename != 'management.py': #исключение модуля management
            await bot.load_extension(f'{path[:-3].replace(os.sep, ".")}')
        elif os.path.isdir(path):
            await load_cogs_recursively(path)

async def change_status():
    await bot.wait_until_ready()
    while not bot.is_closed():
        current_activity = random.choice(activities)
        await bot.change_presence(activity=current_activity)
        await asyncio.sleep(40)

@bot.event
async def on_member_join(member):
    UNVERIFY_ROLE_ID = 0000000000000000000 # роль неверифнутого / выдается автоматически
    unverify_role = member.guild.get_role(UNVERIFY_ROLE_ID)

    if unverify_role:
        await member.add_roles(unverify_role)
        print(f"Роль 'unverify' выдана пользователю {member.name}.")

        embed = discord.Embed(
            title=f"Добро пожаловать на {member.guild.name}!",
            description=f"Привет, {member.mention}! Рады видеть тебя у нас.\n\n"
                        "Пожалуйста, ознакомься с правилами сервера и пройди верификацию.",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=member.guild.icon.url)  
        try:
            await member.send(embed=embed)
        except discord.HTTPException:
            print(f"Не удалось отправить сообщение в ЛС пользователю {member.name}.")
    else:
        print(f"Роль 'unverify' не найдена на сервере.")

@bot.event
async def on_ready():
    print(f'Выполнен вход: {bot.user.name} ({bot.user.id})')
    print('[ЛОГИ] Логи будут ниже.')
    await load_cogs_recursively("cogs") 
    bot.loop.create_task(change_status())

    guild = discord.Object(id=0000000000000000000) # ID сервера, замените на свою гилду

    bot.tree.copy_global_to(guild=guild) 
    await bot.tree.sync(guild=guild)

    # rules - правила
    RULES_CHANNEL_ID = 0000000000000000000 # ID канала правил  
    rules_channel = bot.get_channel(RULES_CHANNEL_ID)

    rules = {
        1.1: {
            "title": "Пункт правил — 1.1",
            "description": "Запрещена реклама любых сторонних ресурсов, а также любая коммерческая деятельность без согласования с администрацией сервера.",
            "punishment": "Бан",
            "duration": "Навсегда"
        },
        1.2: {
            "title": "Пункт правил — 1.2",
            "description": "Если на усмотрение администрации, ваши действия могут идти во вред сервера или нанести какой-либо вред участникам, а также препятствовать их общению, то администрация вправе выдать вам наказание на своё усмотрение.",
            "punishment": "-",
            "duration": "-"
        },
        1.3: {
            "title": "Пункт правил — 1.3",
            "description": "Запрещены мошеннические действия в отношении участников сервера, а также распространение их личной информации.",
            "punishment": "Бан",
            "duration": "Навсегда"
        },
        1.4: {
            "title": "Пункт правил — 1.4",
            "description": "Запрещается трансляция/публикация шокирующего и порнографического контента, а также пропаганда наркотиков, терроризма, угрозы, расизма, нацизма и тому подобных действий.",
            "punishment": "Предупреждение/Бан",
            "duration": "От 7 до 14 дней"
        },
        1.5: {
            "title": "Пункт правил — 1.5",
            "description": "Запрещено использовать аватарки и баннеры, содержащие шокирующий или сексуальный контент.",
            "punishment": "Предупреждение/Бан",
            "duration": "От 7 до 14 дней"
        },
        1.6: {
            "title": "Пункт правил — 1.6",
            "description": "Запрещены нелицеприятные никнеймы, намеренное копирование профилей и ролей, а также никнеймы со оскорбительным или провокационным значением/статусами.",
            "punishment": "Предупреждение/Бан",
            "duration": "От 7 до 14 дней"
        },
        1.7: {
            "title": "Пункт правил — 1.7",
            "description": "Запрещено использование другой учетной записи, чтобы избежать наложенных на вас санкций или для фарма часов/валюты сервера.",
            "punishment": "Бан",
            "duration": "Навсегда"
        },
        1.8: {
            "title": "Пункт правил — 1.8",
            "description": "Запрещен капс, спам, флуд в любых его проявлениях, бессмысленное многократное упоминание участников и ролей, а также несоблюдение тематики чата.",
            "punishment": "Замечание/Мут",
            "duration": "До 4 часов"
        },
        1.9: {
            "title": "Пункт правил — 1.9",
            "description": "Запрещён SoundPad и его аналоги, громкие мешающие звуки, увеличение громкости микрофона, использование программ для изменения голоса.",
            "punishment": "Замечание/Мут",
            "duration": "До 4 часов"
        },
        2.0: {
            "title": "Пункт правил — 2.0",
            "description": "Запрещено неадекватное поведение в любом его виде: оскорбления, крики и тому подобные действия.",
            "punishment": "Замечание/Мут",
            "duration": "До 4 часов"
        },
    }

    async for message in rules_channel.history(limit=100):
        if message.author == bot.user:
            await message.delete()

    embed = discord.Embed(title="Правила сервера", color=discord.Color.darker_grey())
    
    for rule_num, rule_data in rules.items():
        embed.add_field(
            name=rule_data["title"],
            value=f"{rule_data['description']}\n**Наказание:** `{rule_data['punishment']}`\n**Длительность:** `{rule_data['duration']}`",
            inline=False
        )

    embed.set_footer(text="Не забываем соблюдать правила ToS Discord: https://discord.com/terms")
    await rules_channel.send(embed=embed)

    # info

    CHANNEL_ID = 0000000000000000000 # замените на ваш ID канала куда будут отправляться сообщения о прохождении верификации 
    channel = bot.get_channel(CHANNEL_ID)

    pass_channels = {
        1: 0000000000000000000, # замените на ваш ID проходок
        2: 0000000000000000000, 
        3: 0000000000000000000,  
        4: 0000000000000000000,  
        5: 0000000000000000000, 
    }

    async for message in channel.history(limit=100): 
        if message.author == bot.user:
            await message.delete()

    emoji_dot = discord.utils.get(bot.emojis, name="dot")
    emoji_hello = discord.utils.get(bot.emojis, name="hello")

    embed = discord.Embed(
        title=f"{emoji_hello} Добро пожаловать!",
        description="Для успешной верификации убедитесь, что:\n\n"
        f"{emoji_dot} Ваш аккаунт был создан более 5-ти дней назад.\n"
        f"{emoji_dot} У вас есть микрофон.\n"
        f"{emoji_dot} Вы готовы вести себя адекватно во время верификации.\n"
        f"{emoji_dot} Вы настроены отвечать на вопросы честно.\n\n"
        "**Пожалуйста, подключись к одной из комнат:**\n"
        f" <#{pass_channels[1]}>\n"
        f" <#{pass_channels[2]}>\n"
        f" <#{pass_channels[3]}>\n"
        f" <#{pass_channels[4]}>\n"
        f" <#{pass_channels[5]}>\n",
        color=discord.Color.blue(),
    )
    
    embed.set_image(url="https://media.discordapp.net/attachments/1171482318326726758/1176046941390520330/01-1.gif?ex=66864190&is=6684f010&hm=6fbfa49b72bd0b2fa14d8221d2160b358789ac3b2b9ebf30e6a3f9f3f3cc2f50&") # можете добавить свою картинку
    await channel.send(embed=embed)

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel and not after.channel and before.channel.category and before.channel.category.name == "ВАША КАТЕГОРИЯ": # замените на вашу категорию ID
        if len(before.channel.members) == 0:
            await before.channel.delete()
            print(f"Канал {before.channel.name} удален.")

@bot.event
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.errors.CommandNotFound):
        await interaction.response.send_message("Неизвестная команда! Используй `,help` для просмотра списка команд.", ephemeral=True)
    elif isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message("У вас недостаточно прав для выполнения этой команды.", ephemeral=True)
    elif isinstance(error, app_commands.errors.BotMissingPermissions):
        await interaction.response.send_message("У меня недостаточно прав для выполнения этой команды.", ephemeral=True)
    elif isinstance(error, app_commands.errors.NoPrivateMessage):
        await interaction.response.send_message("Эту команду можно использовать только в личных сообщениях.", ephemeral=True)
    elif isinstance(error, app_commands.errors.MissingRequiredApplicationArgument):
        await interaction.response.send_message("Недостаточно аргументов. Используй `,help` для просмотра списка команд.", ephemeral=True)
    else:
        print(f'Ошибка Slash Command: {error}')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Неизвестная команда! Используй `,help` для просмотра списка команд.") 
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Недостаточно аргументов! Используй `,help` для просмотра списка команд.")
    else:
        print(f'Ошибка: {error}')

bot.run(TOKEN) 