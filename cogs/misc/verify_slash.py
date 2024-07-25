#narukami/cogs/misc/verify_slash.py | Кодил: резвоф | Открытый исходный код. Telegram channel: https://t.me/rezvof | GitHub: https://github.com/rezvoff

import discord
from discord.ext import commands
from discord import app_commands, ui

class VerificationView(ui.View):
    def __init__(self, user: discord.Member, author: discord.Member):
        super().__init__(timeout=30)
        self.user = user
        self.author = author
        self.message = None

    @ui.button(label="♂️ Мальчик", style=discord.ButtonStyle.blurple) 
    async def boy_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.process_button(interaction, "boy")

    @ui.button(label="♀️ Девочка", style=discord.ButtonStyle.red)  
    async def girl_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.process_button(interaction, "girl")

    @ui.button(label="⛔ Недопуск", style=discord.ButtonStyle.gray)  
    async def denied_button(self, interaction: discord.Interaction, button: ui.Button):
        await self.process_button(interaction, "недопуск")

    async def process_button(self, interaction: discord.Interaction, role_name: str): 
        if interaction.user.id != self.author.id:
            await interaction.response.send_message("Эта кнопка не для тебя.", ephemeral=True)
            return

        if role_name.lower() == "недопуск":
            await self.assign_role(interaction, "недопуск")
        else:  
            await self.assign_role(interaction, role_name)
        await self.disable_buttons(interaction)

    async def assign_role(self, interaction: discord.Interaction, role_name: str):
        guild = interaction.guild
        role_to_assign = discord.utils.get(guild.roles, name=role_name)
        unverify_role = discord.utils.get(guild.roles, name="unverify")

        if not role_to_assign:
            await interaction.response.send_message(f"Роль '{role_name}' не найдена на сервере.", ephemeral=True)
            return

        if unverify_role in self.user.roles:
            await self.user.remove_roles(unverify_role)

        await self.user.add_roles(role_to_assign)

        if role_name.lower() == "недопуск":
            await interaction.response.send_message(f"Верификация {self.user.mention} отклонена. Выдана роль '{role_name}'.", ephemeral=False)
        else:
            await interaction.response.send_message(f"Пользователю {self.user.mention} выдана роль {role_to_assign.mention}. Пользователь верифнут.", ephemeral=False)

    async def disable_buttons(self, interaction: discord.Interaction):
        for item in self.children:
            item.disabled = True
        await interaction.message.edit(view=self)

    async def on_timeout(self):
        if self.message: 
            await self.message.edit(view=None)

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="verify", description="Верификация гендерной роли")
    @app_commands.describe(user="Пользователь для верификации")
    @commands.has_permissions(administrator=True)
    async def verify(self, interaction: discord.Interaction, user: discord.Member):
        emoji_dot = discord.utils.get(interaction.guild.emojis, name="dot")
        embed = discord.Embed(title="Верификация", 
                              description=f"Выберите гендерную роль для пользователя {user.mention}:", 
                              color=discord.Color.blue())
        embed.add_field(name="Правила верификации:", 
                        value=f"""
                        {emoji_dot} Не забывай проверять возраст пользователя!
                        {emoji_dot} Обращай внимание на адекватность пользователя!
                        {emoji_dot} Будь вежлив и терпелив!
                        {emoji_dot} Не забывай об основных правилах саппортов!
                        """, inline=False)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1257429797441638603/1257768110233092107/00d66ad0c3d1767a3b40431509250869.gif?ex=66961615&is=6694c495&hm=e545185a974ee3a83ce16229a8acc28a56a2cb21c7acc23691c845ec4a0eea64&")
        embed.set_footer(text=f"Верифицирует: {interaction.user}", icon_url=interaction.user.display_avatar.url)

        view = VerificationView(user, interaction.user)
        view.message = await interaction.response.send_message(embed=embed, view=view, ephemeral=False)


async def setup(bot):
    await bot.add_cog(Verification(bot))