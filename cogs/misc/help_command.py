#narukami/cogs/misc/help_command.py | Кодил: резвоф | Открытый исходный код. Telegram channel: https://t.me/rezvof | GitHub: https://github.com/rezvoff

import discord
from discord.ext import commands

class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", description="Показывает список доступных команд.")
    async def help(self, ctx):

        emoji_dot = discord.utils.get(ctx.guild.emojis, name="dot")
        emoji_info = discord.utils.get(self.bot.emojis, name="info")

        embed = discord.Embed(title=f"{emoji_info} | Список команд", color=discord.Color.blue())
        embed.description = "**Информация о командах:**"
        embed.add_field(name=f"{emoji_dot} `,help`", value="Показывает список доступных команд.", inline=False)    
        embed.add_field(name=f"{emoji_dot} `,balance (или ,bal)`", value="Показывает ваш баланс.", inline=False)
        embed.add_field(name=f"{emoji_dot} `,transfer <@user> <валюта> <количество>`", value="Переводит валюту другому пользователю.", inline=False)
        embed.add_field(name=f"{emoji_dot} `,convert <валюта1> <валюта2> <количество>`", value="Конвертация валют.", inline=False)
        embed.add_field(name=f"{emoji_dot} `,leaderboard (или ,top)`", value="Показывает топ 10 богачей по балансу.", inline=False)
        embed.add_field(name=f"{emoji_dot} `,work`", value="Стандартный заработок деняг. Проще говоря, будешь пахарем. Пахать можно раз в час.", inline=False)
        embed.add_field(name=f"{emoji_dot} `,reward`", value="Ежедневный подгон от бота в монетках.", inline=False)
        embed.add_field(name=f"{emoji_dot} `,lucky` (казик, не советую) Пример: `,lucky <монеты> <множитель>`", value="Чем выше множитель, тем выше выигрыш, но шанс меньше.", inline=False)
        embed.add_field(name=f"{emoji_dot} `,clan`", value="Клан сообщества.", inline=False)
        embed.add_field(name=f"{emoji_dot} `,обнять <@юзер>`", value="Обнять пользователя.", inline=False)
        embed.add_field(name=f"{emoji_dot} `,поцеловать <@юзер>`", value="Поцеловать пользователя.", inline=False)
        embed.add_field(name=f"{emoji_dot} `/профиль`", value="Показывает ваш профиль.", inline=False)
        embed.add_field(name=f"{emoji_dot} `/помощь <вопрос>`", value="Задать вопрос администрации сервера.", inline=False)
        embed.set_footer(text="Напишите ,help <команда> для получения подробной информации о команде.", icon_url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="ahelp", description="Показывает список доступных команд для администрации.")
    @commands.has_permissions(manage_messages=True)
    async def ahelp(self, ctx):
        embed = discord.Embed(title="Список команд", color=discord.Color.blue())
        embed.description = "**Информация о админ-командах:**"
        embed.add_field(name="/ban <@юзер> <причина>", value="Забанить пользователя.", inline=False)
        embed.add_field(name="/kick <@юзер> <причина>", value="Кикнуть пользователя.", inline=False)
        embed.add_field(name="/warn <@юзер> <причина>", value="Выдать предупреждение пользователю.", inline=False)
        embed.add_field(name="/unwarn <@юзер> <№ предупреждения>", value="Снять указанное предупреждение пользователя.", inline=False)
        embed.add_field(name="/mute <@юзер> <время> <причина>", value="Выдать мут пользователю.", inline=False)
        embed.add_field(name="/unmute <@юзер>", value="Снять мут пользователя.", inline=False)
        embed.add_field(name="/purge <канал> <количество>", value="Удалить сообщения в выбранном канале.", inline=False)
        embed.add_field(name="/юзер <@юзер>", value="Показывает информацию о юзере.", inline=False)
        embed.add_field(name=",набор", value="Начать набор в команду.", inline=False)
        embed.set_footer(text="Напишите ,ahelp <команда> для получения подробной информации о команде.", icon_url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

    @ahelp.error
    async def admin_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title="⛔ Недостаточно прав!", color=discord.Color.blue())
            await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(HelpCog(bot))