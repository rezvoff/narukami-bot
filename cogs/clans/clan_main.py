# narukami/cogs/clans/clan_main.py | Кодил: резвоф | Открытый исходный код. Telegram channel: https://t.me/rezvof | GitHub: https://github.com/rezvoff

import discord
import datetime
from datetime import datetime
from discord.ext import commands
from cogs.management import ClanManager, Economy

class Clan(commands.Cog):
    def __init__(self, bot, clan_manager, economy):
        self.bot = bot
        self.clan_manager = clan_manager
        self.economy = economy
        self.pending_applications = {}

    @commands.group(name="clan", invoke_without_command=True)
    async def clan(self, ctx):
        """
        Основная команда ,clan. 
        Выводит информацию о доступных подкомандах.
        """

        emoji_dot = discord.utils.get(ctx.guild.emojis, name="dot") 
        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")
        emoji_ruble = discord.utils.get(ctx.guild.emojis, name="ruble")

        if emoji_dot and emoji_clan:
            embed = discord.Embed(
                title="**Система Кланов**",
                description=f"{emoji_clan} Вступи в клан и стань лучше других, или создай свой собственный и выводи его в топы!",
                color=discord.Color.blue()
            )

        embed.add_field(name="**Как создать клан?**",
                        value=f"Используйте команду `,clan create <название>`, для создания клана тебе потребуется 250{emoji_ruble} в боте!",
                        inline=False)
        embed.add_field(name="**Как присоединиться к клану?**",
                        value=f"{emoji_dot} Используй команду `,clan join <название>`", inline=False)
        embed.add_field(name="**Как выйти из клана?**",
                        value=f"{emoji_dot} Используй команду `,clan leave <клан>`", inline=False)
        embed.add_field(name="**Как узнать информацию о своем клане?**",
                        value=f"{emoji_dot} Используй команду `,clan info`", inline=False)
        embed.add_field(name="**Как узнать список кланов?**",
                        value=f"{emoji_dot} Используй команду `,clan list`", inline=False)
        embed.add_field(name="**Топ 10 кланов по участникам**",
                        value=f"{emoji_dot} Используй команду `,clan top <members (участники) / points (очки) / levels (уровень)>`", inline=False)
        embed.add_field(name="**Изменить девиз клана [Владельцы]**",
                        value=f"{emoji_dot} Используй команду `,clan deviz <девиз>`",
                        inline=False)
        embed.add_field(name=f"**Посмотреть заявки в клане [Владельцы]**", 
                        value = f"{emoji_dot} Используй команду `,clan applications/apps <клан>`",
                        inline=False)
        embed.add_field(name=f"**Принять/Отклонить заявку в клан [Владельцы]**", 
                        value = f"{emoji_dot} Используй команду `,clan accept/reject <клан> <id заявки>`",
                        inline=False)

        embed.set_footer(text=f"Всего кланов: {len(self.clan_manager.clans)}", icon_url=self.bot.user.display_avatar.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1257429797441638603/1262115486334980117/fedf33cc28e1527bc75d7cf9782419e3.gif?ex=66956c24&is=66941aa4&hm=a9f6b1737275bea1c5595f137041339a9b0a482dc3efa6b549a70efc704c67e1&")
        await ctx.send(embed=embed)

    @clan.command(name="create")  
    async def clan_create(self, ctx, clan_name: str):
        creation_cost = 250

        emoji_ruble = discord.utils.get(ctx.guild.emojis, name="ruble")
        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")

        if not clan_name:
            embed = discord.Embed(title="Ошибка", description="Вы не ввели название клана.", color=discord.Color.red())
            await ctx.send(embed=embed)
            return 

        if self.clan_manager.create_clan(clan_name, ctx.author.id, datetime.now().strftime("%Y-%m-%d")):
            success = self.economy.remove_donate_currency(ctx.author.id, creation_cost)
            if success:
                self.clan_manager.clans[clan_name]["clan_members"] = 1  
                self.clan_manager.clans[clan_name]["clan_points"] = 0
                self.clan_manager.clans[clan_name]["clan_level"] = 1

                embed = discord.Embed(title="Создание клана", description=f"Клан **{clan_name}** успешно создан! Поздравляю!", color=discord.Color.green())
                embed.add_field(name="Стоимость", value=f"{creation_cost}{emoji_ruble}", inline=False)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title="Недостаточно средств", description=f"Недостаточно рублей для создания клана.", color=discord.Color.red())
                embed.add_field(name="Необходимо", value=f"{creation_cost}{emoji_ruble}", inline=False)
                await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title="Ошибка", description=f"Клан с названием **{clan_name}** {emoji_clan} уже существует.", color=discord.Color.red())
            await ctx.send(embed=embed)

    @clan.command(name="deviz")
    async def clan_set_description(self, ctx, *, new_description: str):

        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")
        user_id = ctx.author.id

        clan_name = None
        for name, clan_data in self.clan_manager.clans.items():
            for member_id in map(int, clan_data["members"].keys()):
                if user_id == member_id:
                    clan_name = name
                    break
            if clan_name: 
                break

        if clan_name:
            if self.clan_manager.change_clan_description(clan_name, user_id, new_description):
                await ctx.send(f"{emoji_clan} Девиз клана успешно изменен на: **{new_description}**")
            else:
                await ctx.send("Ошибка: Вы не являетесь владельцем этого клана.")
        else:
            await ctx.send("Ошибка: Вы не состоите в клане.")

    @clan.command(name="profile")
    async def clan_info(self, ctx):

        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")
        emoji_coin = discord.utils.get(ctx.guild.emojis, name="coin")
        emoji_settings = discord.utils.get(self.bot.emojis, name="settings")
        emoji_info = discord.utils.get(self.bot.emojis, name="info")
        emoji_time = discord.utils.get(self.bot.emojis, name="time")
        emoji_member = discord.utils.get(self.bot.emojis, name="profile")
        
        user_id = ctx.author.id

        clan_name = None
        for name, clan_data in self.clan_manager.clans.items():
            if user_id in clan_data["members"]:
                clan_name = name
            break


        if clan_name:
            clan_data = self.clan_manager.clans[clan_name]
            embed = discord.Embed(title=f"{emoji_clan} Информация о клане {clan_name}", color=discord.Color.blue())
            embed.add_field(name=f"{emoji_info} Владелец:", value=f"<@{clan_data['owner_id']}>", inline=False)
            embed.add_field(name=f"{emoji_time} Дата создания:", value=clan_data['creation_date'], inline=False)
            embed.add_field(name=f"{emoji_settings} Уровень:", value=clan_data['clan_level'], inline=False)
            embed.add_field(name=f"{emoji_coin} Очки:", value=clan_data['clan_points'], inline=False)
            embed.add_field(name=f"{emoji_info} Девиз:", value=clan_data['description'], inline=False)

            members_list = "\n".join([f"<@{member_id}> ({role})" for member_id, role in clan_data["members"].items()])
            embed.add_field(name=f"{emoji_member} Участники", value=members_list, inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send("Ошибка: Вы не состоите в клане.")

    @clan.command(name="join")
    async def clan_join(self, ctx, clan_name: str):

        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")

        user_id = ctx.author.id
        clan = self.clan_manager.clans.get(clan_name)

        if clan:
            if user_id in clan["members"]:
                await ctx.send("Ошибка: Вы уже состоите в этом клане.")
            elif clan_name in self.pending_applications and user_id in self.pending_applications[clan_name]:
                await ctx.send("Ошибка: Вы уже подали заявку в этот клан.")
            else:
                if clan_name not in self.pending_applications:
                    self.pending_applications[clan_name] = []
                self.pending_applications[clan_name].append(user_id)
                await ctx.send(f"{emoji_clan} Заявка на вступление в клан **{clan_name}** успешно отправлена!")

                owner_id = clan["owner_id"]
                owner = ctx.guild.get_member(owner_id)
                if owner:
                    embed = discord.Embed(title=f"{emoji_clan} Заявка в клан {clan_name}",
                                          description=f"Пользователь <@{user_id}> подал заявку на вступление в клан.",
                                          color=discord.Color.blue())
                    await owner.send(embed=embed)
        else:
            await ctx.send(f"Ошибка: Клан с названием **{clan_name}** не найден.")

    @clan.command(name="applications", aliases=["apps"])
    async def clan_applications(self, ctx):
        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")
        emoji_member = discord.utils.get(ctx.guild.emojis, name="member")

        user_id = ctx.author.id 
        found_clan = None

        for clan_name, clan_data in self.clan_manager.clans.items():
            if user_id in clan_data["members"]:  
                found_clan = clan_name
                break

        if found_clan:
            clan_data = self.clan_manager.clans[found_clan]
            if clan_data["owner_id"] == user_id:
                applications = self.pending_applications.get(found_clan, [])
                if applications:
                    embed = discord.Embed(title=f"{emoji_clan} Заявки в клан {found_clan}", color=discord.Color.blue())
                    for applicant_id in applications:
                        member = ctx.guild.get_member(applicant_id)
                        if member:
                            embed.add_field(name=member.mention, value="Ожидает рассмотрения", inline=False)
                        else:
                            embed.add_field(name=f"{emoji_member} Пользователь с ID {applicant_id}", value="Ожидает рассмотрения", inline=False)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"{emoji_clan} В клан **{found_clan}** нет активных заявок.")
            else:
                await ctx.send("Ошибка: Только владелец клана может просматривать заявки.")
        else:
            await ctx.send("Ошибка: Вы не состоите в клане.")


    @clan.command(name="accept")
    async def clan_accept(self, ctx, clan_name: str, member: discord.Member):

        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")
        emoji_member = discord.utils.get(self.bot.emojis, name="member")

        user_id = member.id
        if clan_name in self.pending_applications and user_id in self.pending_applications[clan_name]:
            clan = self.clan_manager.clans.get(clan_name)
            if clan and clan["owner_id"] == ctx.author.id:
                clan["members"][user_id] = "member" 

                if "clan_members" not in clan:
                    clan["clan_members"] = 1
                else:
                    clan["clan_members"] += 1 

                self.clan_manager.save_clans()
                self.clan_manager.load_clans()
                self.pending_applications[clan_name].remove(user_id)
                embed = discord.Embed(title=f"{emoji_clan} Заявка одобрена", 
                                      description=f"{emoji_member} Пользователь {member.mention} присоединился к клану **{clan_name}**", 
                                      color=0x00ff00)
                await ctx.send(embed=embed)

                embed = discord.Embed(title=f"{emoji_clan} Заявка одобрена",
                                      description=f"{emoji_member} Ваша заявка на вступление в клан **{clan_name}**, была одобрена.",
                                      color=0x00ff00)
                await member.send(embed=embed)
            else:
                await ctx.send("Ошибка: Вы не являетесь владельцем этого клана.")
        else:
            await ctx.send("Ошибка: Заявка не найдена.")

    @clan.command(name="reject")
    async def clan_reject(self, ctx, clan_name: str, member: discord.Member):

        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")
        emoji_member = discord.utils.get(self.bot.emojis, name="member")

        if clan_name in self.pending_applications and member in self.pending_applications[clan_name]:
            clan = self.clan_manager.clans.get(clan_name)
            if clan and clan["owner_id"] == ctx.author.id:
                self.pending_applications[clan_name].remove(member)
                embed = discord.Embed(title=f"{emoji_clan} Заявка отклонена", description=f"{emoji_member} Заявка пользователя {member.mention} отклонена.", color=discord.Color.red)
                await ctx.send(embed=embed)
                member = ctx.guild.get_member(member)
                if member:

                    embed = discord.Embed(title=f"{emoji_clan} Заявка отклонена", 
                                          description=f"{emoji_member} Ваша заявка на вступление в клан **{clan_name}**, была отклонена.",
                                          color=discord.Color.red)
                    await member.send(embed=embed)
            else:
                await ctx.send("Ошибка: Вы не являетесь владельцем этого клана.")
        else:
            await ctx.send("Ошибка: Заявка не найдена.")

    @clan.command(name="list")
    async def clan_list(self, ctx):
        if self.clan_manager.clans:
            embed = discord.Embed(title="Список кланов", color=discord.Color.blue())
            for clan_name, clan_data in self.clan_manager.clans.items():
                member_count = len(clan_data["members"])
                embed.add_field(name=clan_name, value=f"Участников: {member_count}", inline=False)
                embed.set_footer(text=f"Всего кланов: {len(self.clan_manager.clans)}")
            await ctx.send(embed=embed)
        else:
            await ctx.send("Кланов пока нет.")

    @clan.command(name="top")
    async def clan_top(self, ctx, category: str = "members"):
        """
        Выводит топ 10 кланов по указанной категории.
        
        Категории:
        - members: по количеству участников
        - rating: по количеству очков
        - levels: по уровню
        """

        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")

        if category not in ("members", "rating", "levels"): 
            await ctx.send("Ошибка: Неверная категория. Доступные категории: members, rating, levels")
            return

        sorted_clans = sorted(self.clan_manager.clans.items(), key=lambda item: item[1].get(f"clan_{category}", 0), reverse=True)

        embed = discord.Embed(title=f"{emoji_clan} Топ 10 кланов по {category}", color=discord.Color.blue())
        for i, (clan_name, clan_data) in enumerate(sorted_clans[:10]):
            value = f"{'Участников' if category == 'members' else category.capitalize()}: {clan_data.get(f'clan_{category}', 0)}"
            embed.add_field(name=f"{i+1}. {clan_name}", value=value, inline=False)
            embed.set_footer(text=f"Всего кланов: {len(self.clan_manager.clans)}")

        await ctx.send(embed=embed)

    @clan.command(name="top_members")
    async def clan_top_members(self, ctx):
        await self.clan_top(ctx, "участников")

    @clan.command(name="top_rating")
    async def clan_top_rating(self, ctx):
        await self.clan_top(ctx, "очки")

    @clan.command(name="top_level")
    async def clan_top_level(self, ctx):
        await self.clan_top(ctx, "уровень")

    @clan.command(name="kick")
    async def clan_kick(self, ctx, member: discord.Member):
        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")
        emoji_member = discord.utils.get(ctx.guild.emojis, name="member")

        user_id = ctx.author.id
        clan_name = None
        for name, clan_data in self.clan_manager.clans.items():
            if user_id in clan_data["members"]:
                clan_name = name
                break

        if clan_name:
            clan_data = self.clan_manager.clans[clan_name]
            user_role = clan_data["members"].get(user_id)

            if user_role in ("owner", "moderator"):
                member_id = member.id 
                if member_id in clan_data["members"]:
                    if self.clan_manager.kick_member(clan_name, user_id, member_id):
                        del clan_data["members"][member_id]
                        clan_data["clan_members"] -= 1
                        self.clan_manager.save_clans()
                        await ctx.send(f"{emoji_member} Участник {member.mention} был исключен из клана **{clan_name}** {emoji_clan}.")
                    else: 
                        await ctx.send("Ошибка при исключении участника.")
                else:
                    await ctx.send(f"Ошибка: Этот участник не состоит в клане **{clan_name}** {emoji_clan}.")
            else:
                await ctx.send("Ошибка: У вас недостаточно прав для исключения участников.")
        else:
            await ctx.send("Ошибка: Вы не состоите в клане.")

    @clan.command(name="leave")
    async def clan_leave(self, ctx, error):
        emoji_clan = discord.utils.get(ctx.guild.emojis, name="clan")
        emoji_member = discord.utils.get(ctx.guild.emojis, name="member")

        user_id = ctx.author.id
        clan_name = None
        for name, clan_data in self.clan_manager.clans.items():
            if user_id in clan_data["members"]:
                clan_name = name
                break

        if clan_name:
            if self.clan_manager.leave_clan(clan_name, user_id):
                del self.clan_manager.clans[clan_name]
                self.clan_manager.save_clans()
                await ctx.send(f"{emoji_member} Вы вышли из клана **{clan_name}** {emoji_clan}.")
            else:
                await ctx.send("Ошибка при выходе участника из клана.")
                print(f"Ошибка выходе: {error}")
        else:
            await ctx.send("Ошибка: Вы не состоите в клане.")

async def setup(bot):
    clan_manager = ClanManager() 
    economy = Economy()
    clan_manager.load_clans()
    await bot.add_cog(Clan(bot, clan_manager, economy))