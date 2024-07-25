#narukami/cogs/admin/admin_slash.py | Кодил: резвоф | Открытый исходный код. Telegram channel: https://t.me/rezvof | GitHub: https://github.com/rezvoff

import discord
from discord.ext import commands
from discord import app_commands
import re
import asyncio
import datetime
import json

class AdminSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.warnings = self.load_warnings()

    def load_warnings(self):
        try:
            with open("warnings.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_warnings(self):
        with open("warnings.json", "w") as f:
            json.dump(self.warnings, f, indent=4)

    @app_commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @app_commands.command(name="warn", description="Выдать предупреждение участнику.")
    @app_commands.describe(участник="Участник, которому нужно выдать предупреждение.", причина="Причина варна.")
    async def warn(self, interaction: discord.Interaction, участник: discord.Member, *, причина: str):

        emoji_checkbox = discord.utils.get(self.bot.emojis, name="checkbox")
        emoji_info = discord.utils.get(self.bot.emojis, name="info")
        emoji_warn = discord.utils.get(self.bot.emojis, name="warn")
        emoji_profile = discord.utils.get(self.bot.emojis, name="profile")

        guild_id = str(interaction.guild.id)
        user_id = str(участник.id)

        if user_id not in self.warnings:
            self.warnings[user_id] = []

        warn_data = {
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reason": причина,
            "moderator": interaction.user.id
        }

        self.warnings[user_id].append(warn_data)
        self.save_warnings()

        warning_count = len(self.warnings[user_id])

        embed = discord.Embed(title=f"{emoji_checkbox} | Успешно", color=discord.Color.blue())
        embed.description = f"{emoji_warn} Участник {участник.mention} получил варн {warning_count}/3"
        embed.add_field(name=f"{emoji_info} Причина:", value=причина, inline=False)
        embed.set_footer(text=f"Ответственный: {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

        if warning_count >= 3:
            await interaction.followup.send(f"{участник.mention} кикнут(а) за получение 3 варнов.")
            await участник.kick(reason="3 предупреждения")
            self.warnings[user_id] = []
            self.save_warnings()

    @app_commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @app_commands.command(name="unwarn", description="Снять предупреждение с участника.")
    @app_commands.describe(участник="Участник, с которого нужно снять предупреждение.", номер="Номер предупреждения для удаления.")
    async def unwarn(self, interaction: discord.Interaction, участник: discord.Member, номер: int):
        user_id = str(участник.id)

        if user_id in self.warnings:
            if 1 <= номер <= len(self.warnings[user_id]):
                del self.warnings[user_id][номер - 1]
                self.save_warnings()
                await interaction.response.send_message(f"Предупреждение №{номер} удалено у {участник.mention}.")
            else:
                await interaction.response.send_message("Неверный номер предупреждения.", delete_after=10)
        else:
            await interaction.response.send_message(f"У {участник.mention} нет предупреждений.", delete_after=10)

    @app_commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @app_commands.command(name="warninfo", description="Информация о предупреждениях участника.")
    @app_commands.describe(участник="Участник, информацию о варнах которого нужно получить.", номер="Номер варна (необязательно).")
    async def warninfo(self, interaction: discord.Interaction, участник: discord.Member, номер: int = None):


        emoji_admins = discord.utils.get(self.bot.emojis, name="admins")
        emoji_time = discord.utils.get(self.bot.emojis, name="time")
        emoji_reason = discord.utils.get(self.bot.emojis, name="reason")
        emoji_info = discord.utils.get(self.bot.emojis, name="info")
        user_id = str(участник.id)

        if user_id in self.warnings:
            if номер is not None:
                if 1 <= номер <= len(self.warnings[user_id]):
                    warn_data = self.warnings[user_id][номер - 1]
                    moderator = await self.bot.fetch_user(warn_data["moderator"])
                    embed = discord.Embed(title=f"{emoji_admins} | Варн №{номер} у {участник.display_name}", color=discord.Color.blue())
                    embed.add_field(name=f"{emoji_time} Время:", value=warn_data["time"], inline=False)
                    embed.add_field(name=f"{emoji_reason} Причина:", value=warn_data["reason"], inline=False)
                    embed.add_field(name=f"{emoji_info} Кем выдан:", value=moderator.mention, inline=False)
                    await interaction.response.send_message(embed=embed)
                else:
                    await interaction.response.send_message("Неверный номер предупреждения.", delete_after=10)
            else:
                embed = discord.Embed(title=f"Предупреждения {участник.display_name}", color=discord.Color.blue())
                for i, warn_data in enumerate(self.warnings[user_id]):
                    moderator = await self.bot.fetch_user(warn_data["moderator"])
                    embed.add_field(name=f"Варн №{i+1}", value=f"**Время:** {warn_data['time']}\n**Причина:** {warn_data['reason']}\n**Кем выдан:** {moderator.mention}", inline=False)
                await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"У {участник.mention} нет предупреждений.", delete_after=10)

    @app_commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @app_commands.command(name="kick", description="Кикнуть участника с сервера.")
    @app_commands.describe(участник="Участник, которого нужно кикнуть.", причина="Причина кика.")
    async def kick(self, interaction: discord.Interaction, участник: discord.Member, *, причина: str = "Причина не указана"):

        emoji_info = discord.utils.get(self.bot.emojis, name="info")
        emoji_checkbox = discord.utils.get(self.bot.emojis, name="checkbox")
        emoji_profile = discord.utils.get(self.bot.emojis, name="profile")

        try:
            kick_dm_embed = discord.Embed(title=f"{emoji_info} Вас кикнули", color=discord.Color.blue())
            kick_dm_embed.description = f"Вы были кикнуты с сервера **{interaction.guild.name}**."
            kick_dm_embed.add_field(name="Причина:", value=причина, inline=False)
            await участник.send(embed=kick_dm_embed)
        except discord.Forbidden:
            await interaction.response.send_message(f"Не удалось отправить личное сообщение {участник.mention}.", ephemeral=True)

        await участник.kick(reason=причина)
        embed = discord.Embed(title=f"{emoji_checkbox} | Успешно", description=f"Участник {участник.mention} был кикнут.", color=discord.Color.blue())
        embed.add_field(name=f"{emoji_info} Причина:", value=причина, inline=False)
        embed.set_footer(text=f"Ответственный: {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @app_commands.command(name="ban", description="Забанить участника на сервере.")
    @app_commands.describe(участник="Участник, которого нужно забанить.", причина="Причина бана.")
    async def ban(self, interaction: discord.Interaction, участник: discord.Member, *, причина: str = "Причина не указана"):

        emoji_info = discord.utils.get(self.bot.emojis, name="info")
        emoji_checkbox = discord.utils.get(self.bot.emojis, name="checkbox")
        emoji_profile = discord.utils.get(self.bot.emojis, name="profile")

        try:
            ban_dm_embed = discord.Embed(title="Вас забанили", color=discord.Color.blue())
            ban_dm_embed.description = f"Вы были забанены на сервере **{interaction.guild.name}**."
            ban_dm_embed.add_field(name="Причина:", value=причина, inline=False)
            await участник.send(embed=ban_dm_embed)
        except discord.Forbidden:
            await interaction.response.send_message(f"Не удалось отправить личное сообщение {участник.mention}.", ephemeral=True)

        await участник.ban(reason=причина)
        embed = discord.Embed(title=f"{emoji_checkbox} | Успешно", description=f"Участник {участник.mention} был забанен.", color=discord.Color.blue())
        embed.add_field(name=f"{emoji_info} Причина:", value=причина, inline=False)
        embed.set_footer(text=f"Ответственный: {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @app_commands.command(name="mute", description="Замутить участника.")
    @app_commands.describe(участник="Участник, которого нужно замутить.", 
                        время="Длительность мута (например, 10m, 1h, 1d).", 
                        причина="Причина мута (Обязательно)")
    async def mute(self, interaction: discord.Interaction, участник: discord.Member, время: str = None, *, причина: str = "Причина не указана."):

        emoji_info = discord.utils.get(self.bot.emojis, name="info")
        emoji_checkbox = discord.utils.get(self.bot.emojis, name="checkbox")
        emoji_profile = discord.utils.get(self.bot.emojis, name="profile")
        emoji_mute = discord.utils.get(self.bot.emojis, name="mute")

        muted_role = discord.utils.get(interaction.guild.roles, name="muted")
        if not muted_role:
            muted_role = await interaction.guild.create_role(name="muted")
            for channel in interaction.guild.channels:
                await channel.set_permissions(muted_role, send_messages=False)

        try:
            mute_dm_embed = discord.Embed(title="Вас замутили", color=discord.Color.blue())
            mute_dm_embed.description = f"Вы были замучены на сервере **{interaction.guild.name}**"
            if время:
                time_regex = re.compile(r'(\d+)([smhd])')
                match = time_regex.match(время)
                if match:
                    time_value = int(match.group(1))
                    time_unit = match.group(2)

                    if time_unit == 's':
                        time_description = f"{time_value} секунд"
                        seconds = time_value
                    elif time_unit == 'm':
                        time_description = f"{time_value} минут"
                        seconds = time_value * 60
                    elif time_unit == 'h':
                        time_description = f"{time_value} часов"
                        seconds = time_value * 60 * 60
                    elif time_unit == 'd':
                        time_description = f"{time_value} дней"
                        seconds = time_value * 60 * 60 * 24
                    else:
                        await interaction.followup.send("Неверный формат времени. Используйте 's', 'm', 'h', или 'd' для секунд, минут, часов и дней соответственно.", delete_after=10)
                        return

                    mute_dm_embed.add_field(name=f"Длительность:", value=time_description, inline=False)
            if причина:
                mute_dm_embed.add_field(name="Причина:", value=причина, inline=False)
            await участник.send(embed=mute_dm_embed)
        except discord.Forbidden:
            await interaction.response.send_message(f"Не удалось отправить личное сообщение {участник.mention}.", ephemeral=True)

        await участник.add_roles(muted_role, reason=причина)

        embed = discord.Embed(title=f"{emoji_checkbox} | Успешно", color=discord.Color.blue())
        if время:
            embed.description = f"{emoji_mute} Пользователю {участник.mention} выдан мут на {time_description}."
        else:
            embed.description = f"{emoji_mute} Пользователю {участник.mention} выдан мут навсегда. "
        embed.add_field(name=f"{emoji_info} Причина:", value=причина, inline=False)
        embed.set_footer(text=f"Ответственный: {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

        if время:
            await asyncio.sleep(seconds)
            await участник.remove_roles(muted_role)
            await interaction.followup.send(f"Пользователь {участник.mention} размучен, так как время мута истекло.")

    @app_commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @app_commands.command(name="unmute", description="Размутить участника.")
    @app_commands.describe(участник="Участник, которого нужно размутить.", причина="Причина размута.")
    async def unmute(self, interaction: discord.Interaction, участник: discord.Member, *, причина: str = "Не указана."):

        emoji_info = discord.utils.get(self.bot.emojis, name="info")
        emoji_checkbox = discord.utils.get(self.bot.emojis, name="checkbox")
        emoji_unmute = discord.utils.get(self.bot.emojis, name="unmute")
        emoji_profile = discord.utils.get(self.bot.emojis, name="profile")
        emoji_info = discord.utils.get(self.bot.emojis, name="info")

        muted_role = discord.utils.get(interaction.guild.roles, name="muted")
        if muted_role in участник.roles:
            await участник.remove_roles(muted_role, reason=причина)
            embed = discord.Embed(title=f"{emoji_checkbox} | Успешно", description=f"Пользователь {участник.mention} был размучен.", color=discord.Color.blue())
            embed.add_field(name=f"{emoji_info} Причина:", value=причина, inline=False)
            embed.set_footer(text=f"{emoji_profile} Ответственный: {interaction.user}", icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(f"{участник.mention} не замучен(а).", delete_after=7)

    @app_commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @app_commands.command(name="purge", description="Удаляет указанное количество сообщений в канале.")
    @app_commands.describe(канал="Канал, из которого нужно удалить сообщения.", количество="Количество сообщений для удаления.")
    async def purge(self, interaction: discord.Interaction, канал: discord.TextChannel, количество: int):
        if количество <= 0:
            await interaction.response.send_message("Количество сообщений должно быть больше 0.", ephemeral=True)
            return

        try:
            deleted = await канал.purge(limit=количество)

            embed = discord.Embed(title="Purge/Пурга сообщений", color=discord.Color.blue())
            embed.description = f"Удалено {len(deleted)} сообщений в канале {канал.mention}."
            embed.set_footer(text=f"Выполнил: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)

            await interaction.response.send_message(f"Удалено {len(deleted)} сообщений.", ephemeral=True)
            await канал.send(embed=embed, delete_after=13)  

        except discord.Forbidden:
            await interaction.response.send_message("У бота недостаточно прав для удаления сообщений.", ephemeral=True)
        except discord.HTTPException as e:
            await interaction.response.send_message(f"Произошла ошибка: {e}", ephemeral=True)



    @commands.has_permissions(administrator=True)
    @app_commands.command(name="юзер", description="Получить инфу о пользователе")
    async def юзер(self, interaction: discord.Interaction, пользователь: discord.Member = None):
        """
        Выводит информацию о пользователе на сервере.

        Аргументы:
          пользователь: Упоминание пользователя, о котором нужно получить информацию. 
                        Если не указан, будет использоваться автор команды.
        """
        
        пользователь = пользователь or interaction.author

        def format_datetime(dt):
            if dt is None:
                return "Неизвестно"
            return discord.utils.format_dt(dt, "F")

        статус = {
            discord.Status.online: "В сети",
            discord.Status.idle: "АФК",
            discord.Status.dnd: "Не беспокоить",
            discord.Status.offline: "Не в сети/В инвизе"
        }.get(пользователь.status, "Неизвестно") 

        embed = discord.Embed(title=f"Информация о пользователе {пользователь.name}", color=пользователь.color)
        embed.set_thumbnail(url=пользователь.avatar.url)
        embed.add_field(name="Имя на сервере", value=пользователь.display_name, inline=False)
        embed.add_field(name="ID пользователя", value=пользователь.id, inline=False)
        embed.add_field(name="Статус", value=статус, inline=True)

        if isinstance(пользователь.activity, discord.Game):
            embed.add_field(name="Играет", value=пользователь.activity.name, inline=True)
        
        embed.add_field(name="Присоединился к Discord", value=format_datetime(пользователь.created_at), inline=False)
        embed.add_field(name="Присоединился к серверу", value=format_datetime(пользователь.joined_at), inline=False)

        roles = [role.mention for role in пользователь.roles[1:]] 
        roles_str = ', '.join(roles) if roles else "Нет ролей"
        embed.add_field(name="Роли", value=roles_str, inline=False)

        if пользователь.banner:
            embed.set_image(url=пользователь.banner.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @commands.has_permissions(administrator=True)
    @app_commands.command(name="embed", description="Написать embed сообщение от имени бота.")
    @app_commands.describe(сообщение="Введи Сообщение.")
    async def embed(self, interaction: discord.Interaction, сообщение: str):
        embed = discord.Embed(description=сообщение, color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.guild_only()
    @commands.has_permissions(administrator=True)
    @app_commands.command(name="clear", description="Удаление ВСЕХ сообщений в канале.")
    @app_commands.describe(канал="Канал, в котором нужно удалить сообщения.")
    async def clear(self, interaction: discord.Interaction, канал: discord.TextChannel):

        emoji_checkbox = discord.utils.get(self.bot.emojis, name="checkbox")

        await канал.purge()
        embed = discord.Embed(title=f"{emoji_checkbox} | Успешно", description=f"Все сообщение в канале {канал.name} были удалены.", color=discord.Color.green())
        embed.set_footer(text=f"Выполнил: {interaction.user}", icon_url=interaction.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @kick.error
    @ban.error
    @warn.error
    @unwarn.error
    @warninfo.error
    @mute.error
    @unmute.error
    @purge.error
    @юзер.error
    @embed.error
    @clear.error
    async def admin_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="⛔ Недостаточно прав!", color=discord.Color.blue())
            embed.set_footer(text=f"Выполнил: {interaction.user.name}", icon_url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AdminSlash(bot))