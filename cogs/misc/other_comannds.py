#narukami/cogs/misc/other_comannds.py | Кодил: резвоф | Открытый исходный код. Telegram channel: https://t.me/rezvof | GitHub: https://github.com/rezvoff

import discord
import random
from discord.ext import commands
from discord import app_commands
import random
import re
import asyncio
from cogs.management import get_donate_balance, get_user_data, set_user_data, update_user_data

class OtherCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hug_gifs = [
            "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
            "https://media.giphy.com/media/lrr9rHuoJOE0w/giphy.gif",
            "https://media.giphy.com/media/sUIZWMnfd4Mb6/giphy.gif",
            "https://media.giphy.com/media/143v0Z4767T15e/giphy.gif",
            "https://media.giphy.com/media/BXrwTdoho6hkQ/giphy.gif"
        ]
        self.kiss_gifs = [
            "https://tenor.com/jRVsCzxMYlx.gif",
            "https://tenor.com/eYQnMPJpmBv.gif",
            "https://tenor.com/ssYm4SG8oLK.gif",
            "https://tenor.com/2Q4hZP5j7g6.gif",
            "https://tenor.com/b1Ds9.gif",
            "https://tenor.com/bYxTK.gif",
            "https://tenor.com/bAZMT.gif"
        ]
        self.choke_gifs = [
            "https://tenor.com/bThXg.gif",
            "https://tenor.com/bNiK4.gif"
        ]
        self.voice_time_tracker = {}

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        TRIGGER_CHANNEL_ID = 1259986306495414343  
        RANDOM_CATEGORY_ID = 1255925236956790857
        ACCESS_ROLE_ID = 1259989726954393661
        LOVEROOM_CHANNEL_ID = 1259987254626226206 
        PRIVATE_CATEGORY_ID = 1259990534483869857 # словарь ролей, подключаемых к приватным каналам

        if after.channel and after.channel.id == TRIGGER_CHANNEL_ID:
            random_category = self.bot.get_channel(RANDOM_CATEGORY_ID)

            available_channels = [channel for channel in random_category.voice_channels if len(channel.members) < channel.user_limit]

            if available_channels:
                random_channel = random.choice(available_channels)
                await member.move_to(random_channel)
                print(f"Пользователь {member.name} перемещён в канал {random_channel.name}.")
            else:
                await member.send("Все доступные каналы в этой категории полны. Пожалуйста, подождите.")
                print(f"Не удалось переместить пользователя {member.name} - все каналы полны.")

        if after.channel and after.channel.id == LOVEROOM_CHANNEL_ID:
            private_category = self.bot.get_channel(PRIVATE_CATEGORY_ID)
            private_channel = await private_category.create_voice_channel(
                name=f"💗 Лав Рума {member.name}",
                user_limit=2

            )
            access_role = member.guild.get_role(ACCESS_ROLE_ID)
            await private_channel.set_permissions(member.guild.default_role, connect=False)
            await private_channel.set_permissions(access_role, connect=True)
            await member.move_to(private_channel)
            print(f"Создан приватный канал {private_channel.name} для {member.name}.")

        user_id = str(member.id)
        
        # Пользователь подключился к голосовому каналу
        if after.channel is not None and before.channel is None:
            self.voice_time_tracker[user_id] = {
                "start_time": discord.utils.utcnow(),
                "task": self.bot.loop.create_task(self.track_voice_time(member))
            }

        # Пользователь отключился от голосового канала
        if before.channel is not None and after.channel is None:
            if user_id in self.voice_time_tracker:
                await self.stop_tracking_voice_time(user_id)

    async def track_voice_time(self, member):
        user_id = str(member.id)
        while True:
            await asyncio.sleep(60)  # Обновляем время каждую минуту
            if user_id not in self.voice_time_tracker:
                break

            # Проверяем, находится ли пользователь все еще в голосовом канале
            if member.voice and member.voice.channel:
                current_time = discord.utils.utcnow()
                start_time = self.voice_time_tracker[user_id]["start_time"]
                total_seconds = (current_time - start_time).total_seconds()

                # Обновляем общее время в user_data.json
                user_data = get_user_data(member.id)
                user_data["voice_time"] = user_data.get("voice_time", 0) + int(total_seconds)
                update_user_data(member.id, user_data)

                # Обновляем время начала отслеживания
                self.voice_time_tracker[user_id]["start_time"] = current_time
            else:
                await self.stop_tracking_voice_time(user_id)
                break

    async def stop_tracking_voice_time(self, user_id):
        if user_id in self.voice_time_tracker:
            self.voice_time_tracker[user_id]["task"].cancel()
            del self.voice_time_tracker[user_id]

    @app_commands.command(name="помощь", description="Задать вопрос администрации сервера.")
    async def помощь(self, interaction: discord.Interaction, *, вопрос: str):
        номер_вопроса = random.randint(123000, 999999)

        embed = discord.Embed(
            title="Ваш вопрос отправлен!",
            description=f"Ожидайте, пока с Вами свяжется администрация сервера.\n\n**Ваш уникальный номер вопроса:** #{номер_вопроса}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

        канал_для_админов = interaction.guild.get_channel(1263368024329682985) 
        if канал_для_админов:
            embed_админ = discord.Embed(
                title="Новый вопрос от пользователя!",
                description=f"**Пользователь:** {interaction.user.mention}\n**Вопрос (#{номер_вопроса}):** {вопрос}",
                color=discord.Color.blue()
            )
            await канал_для_админов.send(embed=embed_админ)

    @commands.hybrid_command(name="обнять", description="Обнять пользователя.")
    @app_commands.describe(юзер="Пользователь, которого нужно обнять.")
    async def обнять(self, ctx: commands.Context, юзер: discord.Member):
        random_gif = random.choice(self.hug_gifs)

        embed = discord.Embed(
            description=f"{ctx.author.mention} **обнимает** {юзер.mention}**!**",
            color=discord.Color.purple()
        )
        embed.set_image(url=random_gif)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="поцеловать", description="Поцеловать пользователя.")
    @app_commands.describe(юзер="Пользователь, которого нужно поцеловать.")
    async def поцеловать(self, ctx: commands.Context, юзер: discord.Member):
        random_gif = random.choice(self.kiss_gifs)

        embed = discord.Embed(
            description=f"{ctx.author.mention} **целует** {юзер.mention}**!**",
            color=discord.Color.purple()
        )
        embed.set_image(url=random_gif)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="тык", description="Тыкнуть в щечку.")
    @app_commands.describe(юзер="Пользователь, которому нужно тыкнуть.")
    async def тык(self, ctx: commands.Context, юзер: discord.Member):
        random_gif = random.choice(self.choke_gifs)

        embed = discord.Embed(
            description=f"{ctx.author.mention} **тыкает в щечку** {юзер.mention}**!**",
            color=discord.Color.purple()
        )
        embed.set_image(url=random_gif)

        await ctx.send(embed=embed)

    @commands.hybrid_command(name="пинг", description="Показывает пинг бота")
    async def ping(self, ctx: commands.Context):
        ping = round(self.bot.latency * 1000)
        await ctx.send(f'**Пинг:** `{ping}ms`')

    @commands.hybrid_command(name="сервер", description="Показывает информацию о сервере")
    async def сервер(self, ctx: commands.Context):

        emoji_checkbox = discord.utils.get(self.bot.emojis, name="checkbox")
        emoji_online = discord.utils.get(self.bot.emojis, name="online")
        emoji_info = discord.utils.get(self.bot.emojis, name="info")

        guild = ctx.guild

        creation_date = guild.created_at.strftime("%d.%m.%Y")
        total_members = guild.member_count
        online_members = sum(1 for member in guild.members if member.status != discord.Status.offline)


        embed = discord.Embed(title=f"{emoji_checkbox} | Информация о сервере {guild.name}", color=discord.Color.blue())
        embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name=f"{emoji_info} | Дата создания:", value=creation_date, inline=False)
        embed.add_field(name=f"{emoji_info} | Всего участников:", value=total_members, inline=False)
        embed.add_field(name=f"{emoji_online} | В сети:", value=online_members, inline=False)
        embed.add_field(name=f"{emoji_info} | Владелец:", value=guild.owner.mention, inline=False)
        embed.add_field(name=f"{emoji_info} | Описание:", value=guild.description, inline=False)
        embed.set_footer(text=f"Выполнил: {ctx.author}", icon_url=ctx.author.display_avatar.url)

        await ctx.send(embed=embed)



    @app_commands.command(name="профиль", description="Просмотреть профиль пользователя")
    @app_commands.describe(user="Пользователь, чей профиль нужно посмотреть")
    async def профиль(self, interaction: discord.Interaction, user: discord.Member = None):
        user = user or interaction.user

        emoji_profile = discord.utils.get(self.bot.emojis, name="profile")
        emoji_time = discord.utils.get(self.bot.emojis, name="time")
        emoji_telegram = discord.utils.get(self.bot.emojis, name="telegram")
        emoji_instagram = discord.utils.get(self.bot.emojis, name="instagram")
        emoji_vkontakte = discord.utils.get(self.bot.emojis, name="vkontakte")
        emoji_ruble = discord.utils.get(self.bot.emojis, name="ruble")
        emoji_info = discord.utils.get(self.bot.emojis, name="info")

        user_data = get_user_data(user.id)
        telegram = user_data.get("telegram", None)
        instagram = user_data.get("instagram", None)
        vkontakte = user_data.get("vkontakte", None)
        donate_balance = get_donate_balance(user.id)
        server_time = int((discord.utils.utcnow() - user.joined_at).days) 
        total_voice_seconds = user_data.get("voice_time", 0)
        hours, remainder = divmod(total_voice_seconds, 3600)
        minutes = remainder // 60

        if telegram and not re.match(r"^(https?://)?(www\.)?t\.me/.+$", telegram):
            telegram = "Неправильная ссылка на Telegram"
        if instagram and not re.match(r"^(https?://)?(www\.)?instagram\.com/.+$", instagram):
            instagram = "Неправильная ссылка на Instagram"
        if vkontakte and not re.match(r"^(https?://)?(www\.)?vk\.com/.+$", vkontakte):
            vkontakte = "Неправильная ссылка на ВКонтакте"

        embed = discord.Embed(
            description=f"{emoji_profile} | **Профиль участника** {user.mention}\n"
                        f"{emoji_telegram} **Telegram:** {telegram or 'Не указан'}\n"
                        f"{emoji_vkontakte} **ВКонтакте:** {vkontakte or 'Не указан'}\n"
                        f"{emoji_instagram} **Instagram:** {instagram or 'Не указан'}\n\n"
                        f"{emoji_ruble} **Рубли:** {donate_balance}₽\n\n"
                        f"{emoji_info} **На сервере:** {server_time} дней\n"
                        f"{emoji_time} **Проведенное время в войсе:** {hours} **часов** {minutes} **минут**",
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=user.avatar.url)

        view = discord.ui.View()
        view.add_item(discord.ui.Button(label="Изменить Telegram", style=discord.ButtonStyle.primary, custom_id="add_telegram"))
        view.add_item(discord.ui.Button(label="Изменить Instagram", style=discord.ButtonStyle.primary, custom_id="add_instagram"))
        view.add_item(discord.ui.Button(label="Изменить ВКонтакте", style=discord.ButtonStyle.primary, custom_id="add_vkontakte"))

        async def button_callback(interaction: discord.Interaction):
            if interaction.data["custom_id"] == "add_telegram":
                await interaction.response.send_modal(AddTelegramModal(user.id))
            elif interaction.data["custom_id"] == "add_instagram":
                await interaction.response.send_modal(AddInstagramModal(user.id))
            elif interaction.data["custom_id"] == "add_vkontakte":
                await interaction.response.send_modal(AddVkontakteModal(user.id))

        view.children[0].callback = button_callback
        view.children[1].callback = button_callback
        view.children[2].callback = button_callback

        await interaction.response.send_message(embed=embed, view=view)

class AddTelegramModal(discord.ui.Modal, title="Изменить Telegram"):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

        self.add_item(discord.ui.TextInput(
            label="Введите ссылку на Telegram",
            placeholder="https://t.me/username",
            style=discord.TextStyle.short,
            required=True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        telegram_link = self.children[0].value

        if not re.match(r"^(https?:\/\/)?(www\.)?t\.me\/[a-zA-Z0-9_]{5,}$", telegram_link):
            await interaction.response.send_message("Неправильная ссылка на Telegram. Попробуйте снова.", ephemeral=True)
            return

        update_user_data(self.user_id, {"telegram": telegram_link})

        await interaction.response.send_message("Ссылка на Telegram добавлена!", ephemeral=True)

class AddInstagramModal(discord.ui.Modal, title="Изменить Instagram"):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

        self.add_item(discord.ui.TextInput(
            label="Введите ссылку на Instagram",
            placeholder="https://instagram.com/username",
            style=discord.TextStyle.short,
            required=True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        instagram_link = self.children[0].value

        if not re.match(r"^(https?://)?(www\.)?instagram\.com/.+$", instagram_link):
            await interaction.response.send_message("Неправильная ссылка на Instagram. Попробуйте снова.", ephemeral=True)
            return

        update_user_data(self.user_id, {"instagram": instagram_link})

        await interaction.response.send_message("Ссылка на Instagram добавлена!", ephemeral=True)

class AddVkontakteModal(discord.ui.Modal, title="Изменить ВКонтакте"):
    def __init__(self, user_id: int):
        super().__init__()
        self.user_id = user_id

        self.add_item(discord.ui.TextInput(
            label="Введите ссылку на ВКонтакте",
            placeholder="https://vk.com/username",
            style=discord.TextStyle.short,
            required=True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        vkontakte_link = self.children[0].value

        if not re.match(r"^(https?://)?(www\.)?vk\.com/.+$", vkontakte_link):
            await interaction.response.send_message("Неправильная ссылка на ВКонтакте. Попробуйте снова.", ephemeral=True)
            return

        update_user_data(self.user_id, {"vkontakte": vkontakte_link})

        await interaction.response.send_message("Ссылка на ВКонтакте добавлена!", ephemeral=True)
    

async def setup(bot):
    await bot.add_cog(OtherCommands(bot))