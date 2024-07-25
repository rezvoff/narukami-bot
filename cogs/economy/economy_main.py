#narukami/cogs/economy/economy_main.py | Кодил: резвоф | Открытый исходный код. Telegram channel: https://t.me/rezvof | GitHub: https://github.com/rezvoff

import discord
import random
from discord.ext import commands, tasks
import json

import requests
from cogs.management import Economy, get_balance, set_balance, get_donate_balance,set_donate_balance, get_crypto_balance, set_crypto_balance

ZERO_COMMISSION_ROLE_ID = 0000000000000000000 # ID роли нулевой комиссии (specials)
DOUBLE_REWARD_ROLE_ID = 0000000000000000000 # ID роли удваивающейся награда (specials)

class BalanceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.give_coins.start() 
        self.give_donate_currency.start() 
    def cog_unload(self):
        self.give_coins.cancel()  
        self.give_donate_currency.cancel()

    @tasks.loop(minutes=3)  
    async def give_coins(self):
        for guild in self.bot.guilds:
            for voice_channel in guild.voice_channels:  
                for member in voice_channel.members:  
                    if not member.bot:
                        coins = random.randint(1, 10) 
                        current_balance = get_balance(member.id)
                        set_balance(member.id, current_balance + coins)
                        print(f"Выдано {coins} монет пользователю {member.name} ({member.id}).")

    @give_coins.before_loop
    async def before_give_coins(self):
        await self.bot.wait_until_ready()  

    @tasks.loop(hours=1)  
    async def give_donate_currency(self):
        for guild in self.bot.guilds:
            for voice_channel in guild.voice_channels:
                for member in voice_channel.members:
                    if not member.bot:
                        donate_currency = random.randint(1, 5)  
                        current_donate_balance = get_donate_balance(member.id)
                        set_donate_balance(member.id, current_donate_balance + donate_currency)
                        print(f"Выдано {donate_currency} донат-валюты пользователю {member.name} ({member.id}).")

    @give_donate_currency.before_loop
    async def before_give_donate_currency(self):
        await self.bot.wait_until_ready()  
    @give_donate_currency.before_loop
    async def before_give_donate_currency(self):
        await self.bot.wait_until_ready()

    @commands.command(name="balance", aliases=["bal"], description="Проверка баланса.")
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def balance(self, ctx, member: discord.Member = None):

        emoji_ruble = discord.utils.get(ctx.guild.emojis, name="ruble")
        emoji_coin = discord.utils.get(ctx.guild.emojis, name="coin")
        emoji_btc = discord.utils.get(ctx.guild.emojis, name="btc")

        if member is None:
            member = ctx.author

        user_balance = get_balance(member.id)
        donate_balance = get_donate_balance(member.id)
        crypto_balance = get_crypto_balance(member.id)  

        embed = discord.Embed(title=f"Баланс {member.display_name}", color=discord.Color.blue())
        embed.add_field(name="Монеты:", value=f"**{user_balance:,}** {emoji_coin}", inline=False)
        embed.add_field(name="Рубли:", value=f"**{donate_balance:,}** {emoji_ruble}", inline=False)
        embed.add_field(name="BTC:", value=f"**{crypto_balance:.2f}** {emoji_btc}", inline=False)
        embed.set_footer(text=f"Перевод валюты пользователю возможен через: ,transfer <@юзер> <валюта> <количество>. Комиссия банка: 7%", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @balance.error
    async def balance_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = int(error.retry_after)

            embed = discord.Embed(title="Кулдаун", color=discord.Color.blue())
            embed.description = f"Попробуй снова через {retry_after} секунд."
            await ctx.send(embed=embed)
        else:
            raise error
    
    @commands.command(name="setmoney", description="Установить баланс пользователю.")
    @commands.has_permissions(administrator=True)
    async def setmoney(self, ctx, member: discord.Member, currency: str, amount: int):
        emoji_admins = discord.utils.get(self.bot.emojis, name="admins")

        """Устанавливает баланс пользователя (монеты или рубли)."""
        currency = currency.lower() 
        if currency not in ["монеты", "рубли", "биткоины"]:
            await ctx.send("Неверная валюта. Используйте 'монеты' или 'рубли'.", delete_after=7)
            return

        if currency == "монеты":
            set_balance(member.id, amount)
            balance_type = "монет"
        elif currency == "рубли":
            set_donate_balance(member.id, amount)
            balance_type = "рублей"
        elif currency == "биткоины":
            set_crypto_balance(member.id, amount)
            balance_type = "биткоинов"

        embed = discord.Embed(title=f"{emoji_admins} [АДМИН] Изменение баланса", color=discord.Color.blue())
        embed.description = f"Баланс {balance_type} пользователя {member.mention} установлен на {amount:,}."
        embed.set_footer(text="Не пытайся использовать эту команду сам, это для админов!")
        await ctx.send(embed=embed)

    @setmoney.error
    async def setmoney_error(self, ctx, error):
        emoji_block = discord.utils.get(ctx.guild.emojis, name="block")
        if isinstance(error, commands.MissingPermissions):
            embed = discord.Embed(title=f"{emoji_block} Недостаточно прав!", color=discord.Color.blue())
            await ctx.send(embed=embed)

    @commands.command(name="leaderboard", aliases=["top"], description="Топ 10 по балансу.")
    async def leaderboard(self, ctx):

        emoji_coin = discord.utils.get(ctx.guild.emojis, name="coin")

        with open("economy.json", "r") as f:
            data = json.load(f)

        sorted_users = sorted(data.items(), key=lambda item: item[1]['balance'], reverse=True)

        embed = discord.Embed(title="🏆 Топ 10 богачей", color=discord.Color.blue())

        for i in range(min(10, len(sorted_users))):
            user_id, user_data = sorted_users[i]  
            user = await self.bot.fetch_user(int(user_id))
            balance = user_data['balance']  
            embed.add_field(name=f"{i+1}. {user.name}", value=f"{balance:,} {emoji_coin}", inline=False) 
        embed.set_footer(text=f"Всего пользователей: {len(sorted_users)}", icon_url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="transfer", description="Перевод валюты другому пользователю.")
    async def transfer(self, ctx, recipient: discord.Member, currency: str, amount: int):
        """Перевод монет или рублей другому пользователю."""
        currency = currency.lower()  

        if amount <= 0:
            await ctx.send("Нельзя перевести отрицательную или нулевую сумму.", delete_after=7)
            return

        if currency == "монеты":
            sender_balance = get_balance(ctx.author.id)
            balance_type = "монет"
        elif currency == "рубли":
            sender_balance = get_donate_balance(ctx.author.id)
            balance_type = "рублей"
        else:
            await ctx.send("Неверная валюта. Используйте 'монеты' или 'рубли'.", delete_after=7)
            return

        if sender_balance < amount:
            await ctx.send(f"У вас недостаточно {balance_type} для перевода.", delete_after=7)
            return

        has_zero_commission = discord.utils.get(ctx.author.roles, id=ZERO_COMMISSION_ROLE_ID) is not None

        if has_zero_commission:
            commission = 0
        else:
            commission = int(amount * 0.07)  

        transfer_amount = amount - commission

        if currency == "монеты":
            set_balance(ctx.author.id, sender_balance - amount)
            set_balance(recipient.id, get_balance(recipient.id) + transfer_amount)
        else:
            set_donate_balance(ctx.author.id, sender_balance - amount)
            set_donate_balance(recipient.id, get_donate_balance(recipient.id) + transfer_amount)

        embed = discord.Embed(title=f"Переводы {balance_type}", color=discord.Color.blue())
        embed.add_field(name="Отправитель:", value=ctx.author.mention, inline=False)
        embed.add_field(name="Получатель:", value=recipient.mention, inline=False)
        embed.add_field(name="Сумма:", value=f"**{amount:,}** {balance_type}", inline=False)
        embed.add_field(name="Комиссия:", value=f"{commission} {balance_type}", inline=False)
        embed.add_field(name="Переведено:", value=f"**{transfer_amount:,}** {balance_type}", inline=False)
        embed.set_footer(text="Переводи деньги пользователям с 0% комиссией купив специальную роль. Не трать время и деньги зря!", icon_url=self.user.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="work", description="Заработать деньги.")
    @commands.cooldown(1, 3600, commands.BucketType.user)
    async def work(self, ctx):

        emoji_coin = discord.utils.get(ctx.guild.emojis, name="coin")
        user_id = ctx.author.id
        earned_amount = random.randint(100, 500) 

        if str(ctx.author.id) not in Economy().data:
            Economy().data[str(ctx.author.id)] = {"balance": 0, "donate_balance": 0, "crypto_balance": 0.00}
            Economy().save()

        current_balance = get_balance(user_id)
        new_balance = current_balance + earned_amount
        set_balance(user_id, new_balance)

        embed = discord.Embed(title="Пахарь", color=discord.Color.blue())
        embed.description = f"Твои чистые: **{earned_amount:,}** {emoji_coin}\n" \
                            f"Твой баланс: **{new_balance:,}** {emoji_coin}"
        embed.set_footer(text="Ты можешь пахать каждый час зарабатывая деньги снова и снова!", icon_url=self.bot.user.display_avatar.url)
        await ctx.send(embed=embed)

    @work.error
    async def work_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = int(error.retry_after)
            hours, remainder = divmod(retry_after, 3600)
            minutes, seconds = divmod(remainder, 60)

            embed = discord.Embed(title="Кулдаун", color=discord.Color.blue())
            embed.description = f"Попробуйте снова через {hours}ч {minutes}мин {seconds}сек."
            await ctx.send(embed=embed)
        else:
            raise error
        
    @commands.command(name="lucky", description="Испытай удачу! Пример: ,lucky <количество> <")
    async def lucky(self, ctx, amount: int, multiplier: int):

        emoji_congrats = discord.utils.get(self.bot.emojis, name="congrats")
        emoji_coin = discord.utils.get(ctx.guild.emojis, name="coin")

        if str(ctx.author.id) not in Economy().data:
            Economy().data[str(ctx.author.id)] = {"balance": 0, "donate_balance": 0, "crypto_balance": 0.00}
            Economy().save()

        user_id = ctx.author.id
        balance = get_balance(user_id)

        if amount <= 0 or amount > 10000:
            await ctx.send("Некорректная сумма ставки. Ставка должна быть от 1 до 10000 монет.", delete_after=7)
            return

        if multiplier < 2 or multiplier > 7:
            await ctx.send("Некорректный множитель. Множитель должен быть от 2 до 7.", delete_after=7)
            return

        if balance < amount:
            await ctx.send("У вас недостаточно монет.", delete_after=7)
            return

        win_chance = 1 / multiplier  
        win_roll = random.random()

        if win_roll <= win_chance:
            # win
            winnings = amount * multiplier
            new_balance = balance + winnings
            set_balance(user_id, new_balance)
            embed = discord.Embed(title=f"{emoji_congrats} Вин!", color=discord.Color.blue())
            embed.description = f"Дуракам везеёт. Ты выиграл {winnings:,}{emoji_coin}\n" \
                                f"Твой новый баланс: {new_balance:,}{emoji_coin}"
            embed.set_image(url="https://cdn.discordapp.com/attachments/1257429797441638603/1258817307682148394/d205a1ae2d9253a9.png?ex=66896c79&is=66881af9&hm=6e66382a0b320d7104c68033a611737c233e848899ad281f389c0636dcff76ad&")
            embed.set_footer(text="Чем выше множитель, тем больше шанс проигрыша, но выигрыш выше! Не рискуй и зарабатывай обычным путём.", icon_url=self.bot.user.display_avatar.url)
        else:
            # lose
            new_balance = balance - amount
            set_balance(user_id, new_balance)
            embed = discord.Embed(title="Луз", color=discord.Color.red())
            embed.description = f"Много хочешь, так что, ты проиграл(а) {amount:,}{emoji_coin}\n" \
                                f"Твой новый баланс: {new_balance:,}{emoji_coin}"
            embed.set_image(url="https://cdn.discordapp.com/attachments/1257429797441638603/1258817332856225942/bff626df5539f18f.png?ex=66896c7f&is=66881aff&hm=88c6bad50f1ecfd2cf8d5ba9560c63688dd2607f28ac6315b65eb2ec96a21661&")
            embed.set_footer(text="Чем выше множитель, тем больше шанс проигрыша, но выигрыш выше! Не рискуй и зарабатывай обычным путём.", icon_url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name="reward", description="Получить ежедневную награду.")
    @commands.cooldown(1, 86400, commands.BucketType.user) 
    async def reward(self, ctx):

        emoji_gift = discord.utils.get(self.bot.emojis, name="gift")
        emoji_coin = discord.utils.get(ctx.guild.emojis, name="coin")

        if str(ctx.author.id) not in Economy().data:
            Economy().data[str(ctx.author.id)] = {"balance": 0, "donate_balance": 0, "crypto_balance": 0.00}
            Economy().save()

        has_double_reward = discord.utils.get(ctx.author.roles, id=DOUBLE_REWARD_ROLE_ID) is not None

        reward = 300  
        if has_double_reward:
            reward *= 2

        new_balance = get_balance(ctx.author.id) + reward
        set_balance(ctx.author.id, new_balance)

        embed = discord.Embed(title=f"{emoji_gift} Опа, ежедневка подъехала", color=discord.Color.blue())
        embed.description = f"Ты залутал(а) **{reward:,}**{emoji_coin}\n" \
                            f"Твой новый баланс: **{new_balance:,}**{emoji_coin}"
        embed.set_footer(text="Ты можешь получить ежедневную награду ещё раз через 24 часа. И не забывай, что у специальной роли удваиваются награды.")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1257429797441638603/1258818525817077790/3cb84491e79c1b55a975d37f189ea495.png?ex=66896d9c&is=66881c1c&hm=0a0099f801f0ba2e08ede8f23904e13467f209bf9bafd0178ea0ced55355aaed&")
        await ctx.send(embed=embed)

    @reward.error
    async def reward_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = int(error.retry_after)
            hours, remainder = divmod(retry_after, 3600)
            minutes, seconds = divmod(remainder, 60)
            await ctx.send(f"Не балуйся, а то ты уже получил(а) свою награду сегодня. Попробуйте снова через {hours}ч {minutes}мин {seconds}сек.", delete_after=7)
        else:
            raise error 

    async def get_crypto_price(self, from_currency: str, to_currency: str):
        """Получает курс обмена криптовалюты с помощью CoinGecko API."""
        try:
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={from_currency}&vs_currencies={to_currency}"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            exchange_rate = data[from_currency.lower()][to_currency.lower()]
            return exchange_rate
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении курса обмена: {e}")
            return None

    @commands.command(name="convert", description="Конвертация валюты.")
    async def convert(self, ctx, from_currency: str, amount: float, to_currency: str):
        """Конвертирует валюту с комиссией 7% (0% для роли ZERO_COMMISSION_ROLE_ID)."""

        try:
            from_currency = from_currency.lower()
            to_currency = to_currency.lower()

            if from_currency == to_currency:
                await ctx.send("Нельзя конвертировать валюту саму в себя.", delete_after=7)
                return

            valid_currencies = ["монеты", "рубли", "биткоины"]
            if from_currency not in valid_currencies or to_currency not in valid_currencies:
                await ctx.send("Неверная валюта. Доступные валюты: монеты, рубли, биткоины.", delete_after=7)
                return

            if amount <= 0:
                await ctx.send("Нельзя конвертировать отрицательную или нулевую сумму.", delete_after=7)
                return

            user_balance = get_balance(ctx.author.id)
            user_donate_balance = get_donate_balance(ctx.author.id)
            user_crypto_balance = get_crypto_balance(ctx.author.id)

            has_zero_commission = discord.utils.get(ctx.author.roles, id=ZERO_COMMISSION_ROLE_ID) is not None
            commission_percent = 0.0 if has_zero_commission else 0.07

            # --- Конвертация из монет ---
            if from_currency == "монеты":
                if user_balance < amount:
                    await ctx.send(f"У вас недостаточно монет.", delete_after=7)
                    return
                if to_currency == "рубли":
                    exchange_rate = 100  # 1 рубль = 100 монет
                    converted_amount = amount / exchange_rate * (1 - commission_percent)
                    set_balance(ctx.author.id, user_balance - amount)
                    set_donate_balance(ctx.author.id, user_donate_balance + converted_amount)
                    from_balance_type = "монет"
                    to_balance_type = "рублей"
                elif to_currency == "биткоины":
                    exchange_rate = await self.get_crypto_price("bitcoin", "usd")
                    if exchange_rate is None:
                        await ctx.send("Ошибка при получении курса обмена. Попробуйте позже.", delete_after=7)
                        return
                    converted_amount = (amount / exchange_rate / 100) * (1 - commission_percent)
                    set_balance(ctx.author.id, user_balance - amount)
                    set_crypto_balance(ctx.author.id, user_crypto_balance + converted_amount)
                    from_balance_type = "монет"
                    to_balance_type = "биткоинов"

            # --- Конвертация из рублей ---
            elif from_currency == "рубли":
                if user_donate_balance < amount:
                    await ctx.send(f"У вас недостаточно рублей.", delete_after=7)
                    return
                if to_currency == "монеты":
                    exchange_rate = 100  # 1 рубль = 100 монет
                    converted_amount = amount * exchange_rate * (1 - commission_percent)
                    set_donate_balance(ctx.author.id, user_donate_balance - amount)
                    set_balance(ctx.author.id, user_balance + converted_amount)
                    from_balance_type = "рублей"
                    to_balance_type = "монет"
                elif to_currency == "биткоины":
                    exchange_rate = await self.get_crypto_price("bitcoin", "rub")
                    if exchange_rate is None:
                        await ctx.send("Ошибка при получении курса обмена. Попробуйте позже.", delete_after=7)
                        return
                    converted_amount = (amount / exchange_rate) * (1 - commission_percent)
                    set_donate_balance(ctx.author.id, user_donate_balance - amount)
                    set_crypto_balance(ctx.author.id, user_crypto_balance + converted_amount)
                    from_balance_type = "рублей"
                    to_balance_type = "биткоинов"

            # --- Конвертация из биткоинов ---
            elif from_currency == "биткоины":
                if user_crypto_balance < amount:
                    await ctx.send(f"У вас недостаточно биткоинов.", delete_after=7)
                    return
                if to_currency == "монеты":
                    exchange_rate = await self.get_crypto_price("bitcoin", "usd")
                    if exchange_rate is None:
                        await ctx.send("Ошибка при получении курса обмена. Попробуйте позже.", delete_after=7)
                        return
                    converted_amount = (amount * exchange_rate * 100) * (1 - commission_percent)
                    set_crypto_balance(ctx.author.id, user_crypto_balance - amount)
                    set_balance(ctx.author.id, user_balance + converted_amount)
                    from_balance_type = "биткоинов"
                    to_balance_type = "монет"
                elif to_currency == "рубли":
                    exchange_rate = await self.get_crypto_price("bitcoin", "rub")
                    if exchange_rate is None:
                        await ctx.send("Ошибка при получении курса обмена. Попробуйте позже.", delete_after=7)
                        return
                    converted_amount = (amount * exchange_rate) * (1 - commission_percent)
                    set_crypto_balance(ctx.author.id, user_crypto_balance - amount)
                    set_donate_balance(ctx.author.id, user_donate_balance + converted_amount)
                    from_balance_type = "биткоинов"
                    to_balance_type = "рублей"

            commission = amount / exchange_rate * commission_percent if from_currency == "монеты" else amount * commission_percent

            embed = discord.Embed(title=f"[БАНК] Конвертация валюты", color=discord.Color.blue())
            embed.add_field(name="Отправитель:", value=ctx.author.mention, inline=False)
            embed.add_field(name="Конвертировано из:", value=f"{amount:.2f} {from_balance_type}", inline=False)
            embed.add_field(name="Конвертировано в:", value=f"{converted_amount:.2f} {to_balance_type}", inline=False)
            embed.add_field(name="Комиссия:", value=f"{commission:.2f} {from_balance_type}", inline=False)
            embed.set_footer(text="Конвертируй валюту без комиссии, купив специальную роль!", icon_url=self.bot.user.display_avatar.url)
            await ctx.send(embed=embed)

        except discord.ext.commands.errors.MissingRequiredArgument:
            await ctx.send("Неверный формат команды. Используйте: `,convert <исходная валюта> <количество> <целевая валюта>`")

async def setup(bot):
    await bot.add_cog(BalanceCog(bot))