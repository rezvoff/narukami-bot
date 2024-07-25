#narukami/cogs/misc/nabor.py | Кодил: резвоф | Открытый исходный код. Telegram channel: https://t.me/rezvof | GitHub: https://github.com/rezvoff

import discord
from discord.ext import commands
from discord import app_commands

class ApplicationModal(discord.ui.Modal, title="Форма заявки"):
    def __init__(self, chosen_role: str):
        super().__init__()
        self.chosen_role = chosen_role

        self.add_item(discord.ui.TextInput(
            label="Ваше имя",
            style=discord.TextStyle.short,
            placeholder="Введите ваше имя...",
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="Ваш возраст",
            style=discord.TextStyle.short,
            placeholder="Введите ваш возраст (14+)...",
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="Почему вы хотите эту должность?",
            style=discord.TextStyle.long,
            placeholder="Напишите почему...",
            required=True
        ))
        self.add_item(discord.ui.TextInput(
            label="Ваши навыки и опыт",
            style=discord.TextStyle.long,
            placeholder="Опишите ваши навыки...",
            required=True
        ))

    async def on_submit(self, interaction: discord.Interaction):
        name = self.children[0].value
        age = self.children[1].value
        reason = self.children[2].value
        skills = self.children[3].value

        embed = discord.Embed(title=f"Новая заявка на роль {self.chosen_role}!", color=discord.Color.green())
        embed.add_field(name="Пользователь:", value=interaction.user.mention, inline=False)
        embed.add_field(name="Имя:", value=name, inline=False)
        embed.add_field(name="Возраст:", value=age, inline=False)
        embed.add_field(name="Причина:", value=reason, inline=False)
        embed.add_field(name="Навыки:", value=skills, inline=False)
        embed.set_footer(text=f"ID: {interaction.user.id} | Роль: {interaction.user.top_role.name}")

        application_channel = interaction.guild.get_channel(1263368024329682985)
        if application_channel:
            await application_channel.send(embed=embed)
        await interaction.response.send_message(content="Ваша заявка успешно отправлена! Ожидайте связи с администрацией.", ephemeral=True)

class RoleSelectionView(discord.ui.View):
    @discord.ui.select(
        placeholder="Выберите роль...",
        options=[
            discord.SelectOption(label="Moderator", value="Moderator", description="Модерация сервера"),
            discord.SelectOption(label="TribuneMod", value="Broadcaster", description="Организация трибун"),
            discord.SelectOption(label="Creative", value="Creative", description="Отвечают за творческий раздел"),
            discord.SelectOption(label="Eventsmod", value="Eventsmod", description="Организация мероприятий"),
            discord.SelectOption(label="Support", value="Support", description="Верификация и помощь пользователям"),
            discord.SelectOption(label="Editors", value="Editors", description="Монтаж видео и пиар сервера"),
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        chosen_role = select.values[0]
        modal = ApplicationModal(chosen_role)
        await interaction.response.send_modal(modal)

class Applications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="набор", description="Подать заявку на роль в команде.")
    @commands.has_permissions(administrator=True)
    async def набор(self, ctx):
        embed = discord.Embed(
            title="Набор Staff",
            description=(
                "Ты проводишь время на нашем сервере и хочешь стать **частью нашей команды?**\n"
                "Тогда можешь попробовать себя на ролях ниже:\n\n"
                "<@&1256668545962475632> — **Модерация** сервера\n"
                "<@&1256671691871096996> — **Организация трибун**\n"
                "<@&1256672481083789452> — **Организация мероприятий**\n"
                "<@&1256671320687644724> — Отвечают за **творческий раздел**\n"
                "<@&1256672473903272067> — **Верификация и помощь** пользователям\n"
                "<@&1256684141844369458> — Монтаж **видео и пиар** сервера\n\n"
                "Для того, чтобы подать свою заявку, просто **выбери** нужную роль ниже и **заполни** анкету!"
            ),
            color=discord.Color.blue()
        )

        view = RoleSelectionView()
        await ctx.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Applications(bot))