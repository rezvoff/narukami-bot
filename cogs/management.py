import discord
from discord.ext import commands
import json
import os

# --- кланы ---

class ClanManager:
    def __init__(self):
        self.clan_file = 'clans_manager.json'
        self.clans = {}
        self.load_clans()

    def load_clans(self):
        try:
            with open(self.clan_file, 'r', encoding='utf-8') as f:
                self.clans = json.load(f)
                for clan_data in self.clans.values():
                    clan_data["members"] = {int(k): v for k, v in clan_data["members"].items()}
        except FileNotFoundError:
            self.clans = {}

    def save_clans(self):
        try:
            for clan_data in self.clans.values():
                clan_data["members"] = {str(k): v for k, v in clan_data["members"].items()}
            with open(self.clan_file, 'w') as file:
                json.dump(self.clans, file, indent=4)
        except Exception as e:
            print(f"Ошибка сохранение даты кланов: {e}")

    def create_clan(self, clan_name, owner_id, creation_date):
        if clan_name not in self.clans:
            self.clans[clan_name] = {
                "owner_id": owner_id,
                "creation_date": creation_date,
                "members": {
                    owner_id: "owner"
                },
                "description": "Девиз клана отсутствует.",
                "clan_level": 1,
                "clan_points": 0,
                "clan_members": 1 
            }
            self.save_clans()
            self.load_clans()
            return True
        else:
            return False

    def set_moderator(self, clan_name, owner_id, member_id):
        clan = self.clans.get(clan_name)
        if clan and clan["owner_id"] == owner_id and member_id in clan["members"]:
            clan["members"][member_id] = "moderator"
            self.save_clans()
            return True
        return False

    def kick_member(self, clan_name, kicker_id, member_id):
        clan = self.clans.get(clan_name)
        if clan:
            kicker_role = clan["members"].get(kicker_id)
            if (kicker_role == "owner" or kicker_role == "moderator") and member_id in clan["members"]:
                del clan["members"][member_id]
                self.save_clans()
                return True
        return False
    
    def change_clan_description(self, clan_name, owner_id, new_description):
        clan = self.clans.get(clan_name)
        if clan and clan["owner_id"] == owner_id:
            clan["description"] = new_description
            self.save_clans()
            return True
        return False
    
    def leave_clan(self, clan_name, user_id):
        if clan_name in self.clans:
            if user_id in self.clans[clan_name]["members"]:
                del self.clans[clan_name]["members"][user_id]
                self.save_clans()
                return True
        return False

# --- экономика ---

class Economy:
    def __init__(self):
        self.data_file = "economy.json"
        self.data = {}
        self.load_data()

    def load_data(self):
        try:
            with open(self.data_file, "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}


    def save(self):
        try:
            with open(self.data_file, "w") as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Ошибка сохранения данных экономики: {e}")

    def remove_donate_currency(self, user_id, amount):
        user_id = str(user_id) 
        if user_id in self.data:
            if self.data[user_id]["donate_balance"] >= amount:
                self.data[user_id]["donate_balance"] -= amount
                self.save()
                return True
        return False
    
economy = Economy()

# --- утилиты ---

def get_balance(user_id: int):
    """Получает баланс пользователя (основную валюту) по ID."""
    user_id = str(user_id)
    if user_id not in economy.data:  # Используем глобальный экземпляр economy
        economy.data[user_id] = {"balance": 0, "donate_balance": 0, "crypto_balance": 0.00}
        economy.save()
    return economy.data[user_id].get("balance", 0)

def set_balance(user_id: int, balance: int):
    """Устанавливает баланс пользователя (основную валюту)."""
    user_id = str(user_id)
    if user_id not in economy.data:  # Используем глобальный экземпляр economy
        economy.data[user_id] = {"balance": 0, "donate_balance": 0, "crypto_balance": 0.00}
    economy.data[user_id]["balance"] = balance
    economy.save()

def get_donate_balance(user_id: int):
    """Получает донат-баланс пользователя по ID."""
    user_id = str(user_id)
    if user_id not in economy.data:  # Используем глобальный экземпляр economy
        economy.data[user_id] = {"balance": 0, "donate_balance": 0, "crypto_balance": 0.00}
        economy.save()
    return Economy().data[user_id].get("donate_balance", 0)

def set_donate_balance(user_id: int, donate_balance: int):
    """Устанавливает донат-баланс пользователя."""
    user_id = str(user_id)
    if user_id not in economy.data:  # Используем глобальный экземпляр economy
        economy.data[user_id] = {"balance": 0, "donate_balance": 0, "crypto_balance": 0.00}
        economy.save()
    Economy().save()

def get_crypto_balance(user_id: int):
    """Получает баланс криптовалюты пользователя по ID."""
    user_id = str(user_id)
    if user_id not in economy.data:  # Используем глобальный экземпляр economy
        economy.data[user_id] = {"balance": 0, "donate_balance": 0, "crypto_balance": 0.00}
        economy.save()
    return Economy().data[user_id].get("crypto_balance", 0.00)

def set_crypto_balance(user_id: int, crypto_balance: float):
    """Устанавливает баланс криптовалюты пользователя."""
    user_id = str(user_id)
    if user_id not in economy.data:  # Используем глобальный экземпляр economy
        economy.data[user_id] = {"balance": 0, "donate_balance": 0, "crypto_balance": 0.00}
        economy.save()
    Economy().save()

def load_user_data():
    try:
        with open("user_data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        print(f"Ошибка загрузки данных пользователей: {e}")
        return {}

def save_user_data(data):
    try:
        with open("user_data.json", "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"Ошибка сохранения данных пользователей: {e}")


def get_user_data(user_id):
    """Загружает данные пользователя из user_data.json"""
    user_data = load_user_data()
    return user_data.get(str(user_id), {})

def set_user_data(user_id, data):
    """Сохраняет данные пользователя в user_data.json"""
    user_data = load_user_data()
    user_data[str(user_id)] = data
    user_data[str(user_id)]["voice_time"] = 0
    save_user_data(user_data)

def update_user_data(user_id, data):
    """Обновляет данные пользователя в user_data.json"""
    user_data = load_user_data()
    user_data[str(user_id)].update(data)
    save_user_data(user_data)
