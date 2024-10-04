import discord
from discord import app_commands
from discord.ui import Select, View
import random
from datetime import datetime
import re
import math

intents = discord.Intents.all()
intents.message_content = True
intents.members = True
intents.presences = True

client = discord.Client(intents=intents, activity=discord.Game(name="D&D | /help"))
tree = app_commands.CommandTree(client)

import os
import json  # Assuming you intended to use JSON in the original code

# Define the folder name
folder_name = "server_side"

# Check if the folder exists
try:
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Folder '{folder_name}' created.")
    else:
        print(f"Folder '{folder_name}' already exists.")
except OSError as e:
    print(f"Error creating folder '{folder_name}': {e}")

# Utility functions for JSON file management
def get_server_folder(server_id):
    base_folder = 'server_side'
    server_folder = f'side_{server_id}'
    full_path = os.path.join(base_folder, server_folder)
    
    try:
        os.makedirs(full_path, exist_ok=True)
    except OSError as e:
        print(f"Error creating folder '{full_path}': {e}")
        raise  # Re-raise the error after logging it to stop further operations
    
    return full_path

def load_json(server_id, filename):
    folder = get_server_folder(server_id)
    file_path = os.path.join(folder, filename)
    
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found in folder '{folder}'. Returning empty dictionary.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from file '{file_path}': {e}")
        return {}
    except Exception as e:
        print(f"Unexpected error reading file '{file_path}': {e}")
        return {}

def save_json(server_id, filename, data):
    folder = get_server_folder(server_id)
    file_path = os.path.join(folder, filename)
    
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to '{file_path}'.")
    except PermissionError as e:
        print(f"Permission denied when writing to '{file_path}': {e}")
    except OSError as e:
        print(f"Error writing to file '{file_path}': {e}")
    except Exception as e:
        print(f"Unexpected error saving file '{file_path}': {e}")

# Load data on bot startup
# campaigns = load_json('campaigns.json')
# sessions = load_json('sessions.json')
# character_sheets = load_json('character_sheets.json')
# inventories = load_json('inventories.json')

# Utility function to create embeds
def create_embed(title, description, color=discord.Color.red(), fields=None):
    embed = discord.Embed(title=title, description=description, color=color)
    if fields:
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
    return embed

# Command for showing help
AUTHOR_NAME = "Michele Cicerale"
AUTHOR_DISCORD = "Gentle_Ego"
AUTHOR_ICON_URL = "https://imgur.com/a/OsXVVN9"

@tree.command(name="help", description="Show help information for the bot commands")
async def help_command(interaction: discord.Interaction):
    # Embed data for different command categories
    embeds = {
        "Welcome": discord.Embed(
            title="👋 Welcome to the D&D is Easy Bot!",
            description="This bot helps you manage your D&D character information, manage your campaigns and sessions, roll dices, AND SO MUCH MORE... Currently in BETA, so your feedback is crucial!",
            color=discord.Color.blue()
        ).add_field(name="Feedback", value=f"Send feedback directly to {AUTHOR_DISCORD} on Discord.", inline=False)
         .add_field(name="Commands", value="Use the dropdown menu below to explore different categories of commands.", inline=False),

        "General": discord.Embed(
            title="🎲 General Commands",
            description="Here are the general commands you can use:",
            color=discord.Color.green()
        ).add_field(name="/roll", value="Roll dice with optional modifiers. Example: `/roll 2d6 + 3`", inline=False)
         .add_field(name="/list_campaigns", value="List all available campaigns.", inline=False)
         .add_field(name="/list_sessions", value="List scheduled sessions for all campaigns or a specific one.", inline=False),

        "Campaigns": discord.Embed(
            title="📅 Campaign Commands",
            description="Manage your campaigns with these commands:",
            color=discord.Color.gold()
        ).add_field(name="/add_campaign", value="Add a new campaign. Example: `/add_campaign MyCampaign`", inline=False)
         .add_field(name="/remove_campaign", value="Remove a campaign. Example: `/remove_campaign MyCampaign`", inline=False)
         .add_field(name="/schedule_session", value="Schedule a session for a campaign. Example: `/schedule_session MyCampaign 2024-05-15 18:00`", inline=False),

        "Characters": discord.Embed(
            title="🧙 Character Commands",
            description="Manage your characters with these commands:",
            color=discord.Color.purple()
        ).add_field(name="/add_character", value="Add a new character to your campaign. Example: `/add_character MyCampaign Name Race Class Background @user`", inline=False)
         .add_field(name="/create_character", value="Create a character sheet without adding it to a campaign. Example: `/create_character Name Race Class Background`", inline=False)
         .add_field(name="/update_ability", value="Update a character's ability score. Example: `/update_ability Bob strength 16`", inline=False)
         .add_field(name="/view_character", value="View detailed character info. Example: `/view_character Bob`", inline=False)
         .add_field(name="/level_up", value="Level up a character. Example: `/level_up Bob`", inline=False),

        "Skills": discord.Embed(
            title="✨ Skills and Features",
            description="Manage character skills and features with these commands:",
            color=discord.Color.teal()
        ).add_field(name="/add_skill", value="Add a skill proficiency to a character. Example: `/add_skill Bob Acrobatics`", inline=False)
         .add_field(name="/add_feature", value="Add a feature or trait. Example: `/add_feature Bob 'Second Wind' 'Regain some hit points on your turn'`", inline=False),

        "Combat": discord.Embed(
            title="⚔️ Combat Commands",
            description="Manage combat-related information with these commands:",
            color=discord.Color.red()
        ).add_field(name="/update_hp", value="Update a character's hit points. Example: `/update_hp Bob 25 30 2`", inline=False)
         .add_field(name="/char_roll", value="Roll dice for a character. Example: `/char_roll Bob 1d20+5`", inline=False),

        "Equipment": discord.Embed(
            title="🛡️ Equipment Commands",
            description="Manage character equipment with these commands:",
            color=discord.Color.dark_gold()
        ).add_field(name="/add_equipment", value="Add equipment to a character. Example: `/add_equipment Bob Longsword weapons`", inline=False),

        "Spells": discord.Embed(
            title="🔮 Spell Commands",
            description="Manage character spells with these commands:",
            color=discord.Color.dark_purple()
        ).add_field(name="/add_spell", value="Add a spell to a character's spell list. Example: `/add_spell Bob Fireball 3`", inline=False),

        "Proficiencies": discord.Embed(
            title="📚 Proficiencies",
            description="Manage character proficiencies with these commands:",
            color=discord.Color.dark_green()
        ).add_field(name="/add_proficiency", value="Add a proficiency to a character. Example: `/add_proficiency Bob languages Elvish`", inline=False),

        "Appearance": discord.Embed(
            title="👤 Appearance & Backstory",
            description="Manage character appearance and backstory with these commands:",
            color=discord.Color.blue()
        ).add_field(name="/update_appearance", value="Update a character's appearance. Example: `/update_appearance Bob height '6 feet'`", inline=False)
         .add_field(name="/update_backstory", value="Update a character's backstory. Example: `/update_backstory Bob 'Born in a small village...'`", inline=False)
         .add_field(name="/add_note", value="Add a note to a character. Example: `/add_note Bob 'Found a mysterious amulet'`", inline=False)
    }

    # Add footer to all embeds with consistent information
    for embed in embeds.values():
        embed.set_footer(text=f"Created by {AUTHOR_NAME} | Discord: {AUTHOR_DISCORD}", icon_url=AUTHOR_ICON_URL)

    # Dynamic options for the dropdown menu
    options = [
        discord.SelectOption(label="Welcome", description="Welcome message and bot information", emoji="👋"),
        discord.SelectOption(label="General", description="General commands", emoji="🎲"),
        discord.SelectOption(label="Campaigns", description="Campaign management", emoji="📅"),
        discord.SelectOption(label="Characters", description="Character management", emoji="🧙"),
        discord.SelectOption(label="Skills", description="Skills and features management", emoji="✨"),
        discord.SelectOption(label="Combat", description="Combat information management", emoji="⚔️"),
        discord.SelectOption(label="Equipment", description="Equipment management", emoji="🛡️"),
        discord.SelectOption(label="Spells", description="Spell management", emoji="🔮"),
        discord.SelectOption(label="Proficiencies", description="Proficiency management", emoji="📚"),
        discord.SelectOption(label="Appearance", description="Appearance and backstory management", emoji="👤")
    ]

    # Define the callback for the select menu interaction
    async def select_callback(interaction: discord.Interaction):
        selected = interaction.data['values'][0]
        await interaction.response.edit_message(embed=embeds[selected])

    # Create and configure the select menu for the dropdown
    select_menu = Select(placeholder="Select a category", options=options)
    select_menu.callback = select_callback

    # Add the select menu to the view
    view = View()
    view.add_item(select_menu)

    # Send the initial message with the welcome embed and the view
    await interaction.response.send_message(embed=embeds["Welcome"], view=view)

def parse_roll_string(roll_string):
    # Remove spaces and convert to lowercase for easier parsing
    roll_string = roll_string.replace(" ", "").lower()
    
    # Split the input string into individual roll groups
    roll_groups = re.findall(r'([+-]?\d*d?\d+)', roll_string)
    
    rolls = []
    modifier = 0
    
    for group in roll_groups:
        if 'd' in group:
            # Handle dice rolls (dN, NdN)
            match = re.match(r'([+-]?)(\d*)d(\d+)', group)
            sign, num, sides = match.groups()
            num = int(num) if num else 1
            sides = int(sides)
            
            if sign == '-':
                num = -num
            
            rolls.append((num, sides))
        else:
            # Handle modifiers
            modifier += int(group)
    
    return rolls, modifier

def roll_dice(num, sides):
    return [random.randint(1, abs(sides)) for _ in range(abs(num))]

@tree.command(name="roll", description="Roll one or more dice with optional modifiers")
async def roll(interaction: discord.Interaction, dice: str):
    try:
        rolls, modifier = parse_roll_string(dice)
        results = []
        details = []
        
        for num, sides in rolls:
            if abs(num) > 100 or abs(sides) > 1000:
                raise ValueError(f"Number of dice or sides too high: {abs(num)}d{abs(sides)}")
            
            roll_results = roll_dice(num, sides)
            
            if num < 0:
                results.extend([-r for r in roll_results])
                details.append(f"-{abs(num)}d{sides}: {[-r for r in roll_results]}")
            else:
                results.extend(roll_results)
                details.append(f"{num}d{sides}: {roll_results}")
        
        total = sum(results) + modifier
        
        description = f"**Result: {total}**"
        if results:
            description += f" (Dice: {sum(results)}"
            if modifier != 0:
                description += f" {'+' if modifier > 0 else '-'} {abs(modifier)}"
            description += ")"
        
        embed = create_embed("Dice Roll", description, discord.Color.red())
        await interaction.response.send_message(embed=embed)
    
    except ValueError as e:
        error_embed = create_embed("Error", str(e), discord.Color.red())
        await interaction.response.send_message(embed=error_embed)

@tree.command(name="add_campaign", description="Add a new campaign")
async def add_campaign(interaction: discord.Interaction, name: str):
    campaigns = load_json(str(interaction.guild_id), 'campaigns.json')
    campaigns[name] = []
    save_json(str(interaction.guild.id), 'campaigns.json', campaigns)
    embed = create_embed("Campaign Added", f"Campaign '{name}' added successfully.", discord.Color.red())
    await interaction.response.send_message(embed=embed)

@tree.command(name="remove_campaign", description="Remove a campaign")
async def remove_campaign(interaction: discord.Interaction, name: str):
    campaigns = load_json(str(interaction.guild_id), 'campaigns.json')
    if name in campaigns:
        del campaigns[name]
        save_json(str(interaction.guild.id), 'campaigns.json', campaigns)
        embed = create_embed("Campaign Removed", f"Campaign '{name}' removed successfully.", discord.Color.red())
    else:
        embed = create_embed("Error", f"Campaign '{name}' not found.", discord.Color.red())
    await interaction.response.send_message(embed=embed)

@tree.command(name="add_character", description="Add a character to a campaign")
async def add_character(interaction: discord.Interaction, campaign: str, character: str, race: str, class_: str, background : str, user: discord.User = None):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    campaigns = load_json(str(interaction.guild_id), 'campaigns.json')
    if campaign not in campaigns:
        embed = create_embed("Error", f"Campaign '{campaign}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    create_character(character, race, class_, background,  character_sheets, str(interaction.guild_id))
    character_info = {"name": character, "race": race, "class": class_, "user": str(user.id) if user else None}
    campaigns[campaign].append(character_info)
    save_json(str(interaction.guild.id), 'campaigns.json', campaigns)
    embed = create_embed("Character Added", f"Character '{character}' added to campaign '{campaign}'.", discord.Color.red())
    await interaction.response.send_message(embed=embed)

@tree.command(name="list_campaigns", description="List all campaigns")
async def list_campaigns(interaction: discord.Interaction):
    campaigns = load_json(str(interaction.guild_id), 'campaigns.json')
    if not campaigns:
        embed = create_embed("Campaigns", "No campaigns found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    embed = create_embed("Campaigns", "List of all campaigns and characters", discord.Color.red())
    for campaign, characters in campaigns.items():
        char_list = "\n".join([f"• {char['name']} ({char['race']} {char['class']}) - {'<@' + char['user'] + '>' if char['user'] else 'N/A'}" for char in characters])
        embed.add_field(name=campaign, value=char_list or "No characters", inline=False)
    
    await interaction.response.send_message(embed=embed)

@tree.command(name="schedule_session", description="Schedule a session")
async def schedule_session(interaction: discord.Interaction, campaign: str, date: str, time: str):
    campaigns = load_json(str(interaction.guild_id), 'campaigns.json')
    sessions = load_json(str(interaction.guild_id), 'sessions.json')
    if campaign not in campaigns:
        embed = create_embed("Error", f"Campaign '{campaign}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    try:
        session_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        sessions.setdefault(campaign, []).append(session_datetime.strftime("%Y-%m-%d %H:%M"))
        save_json(str(interaction.guild.id), 'sessions.json', sessions)
        embed = create_embed("Session Scheduled", f"Session scheduled for campaign '{campaign}' on {date} at {time}.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
    except ValueError:
        embed = create_embed("Error", "Invalid date/time format. Use YYYY-MM-DD for date and HH:MM for time.", discord.Color.red())
        await interaction.response.send_message(embed=embed)

@tree.command(name="list_sessions", description="List scheduled sessions")
async def list_sessions(interaction: discord.Interaction, campaign: str = None):
    sessions = load_json(str(interaction.guild_id), 'sessions.json')
    if campaign and campaign not in sessions:
        embed = create_embed("Sessions", f"No sessions scheduled for campaign '{campaign}'.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    embed = create_embed("Scheduled Sessions", "List of all scheduled sessions", discord.Color.red())
    for camp, dates in sessions.items():
        if campaign and camp != campaign:
            continue
        session_list = "\n".join([f"• {date}" for date in dates])
        embed.add_field(name=camp, value=session_list or "No sessions scheduled", inline=False)
    
    await interaction.response.send_message(embed=embed)

def calculate_modifier(stat):
    return (stat - 10) // 2

"""
# Expanded character_sheets structure
character_sheets = {
    "character_name": {
        "basic_info": {
            "name": "",
            "race": "",
            "class": "",
            "background": "",
            "alignment": "",
            "level": 1,
            "experience": 0
        },
        "abilities": {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        },
        "skills": {
            "acrobatics": 0,
            "animal_handling": 0,
            "arcana": 0,
            "athletics": 0,
            "deception": 0,
            "history": 0,
            "insight": 0,
            "intimidation": 0,
            "investigation": 0,
            "medicine": 0,
            "nature": 0,
            "perception": 0,
            "performance": 0,
            "persuasion": 0,
            "religion": 0,
            "sleight_of_hand": 0,
            "stealth": 0,
            "survival": 0
        },
        "saving_throws": {
            "strength": 0,
            "dexterity": 0,
            "constitution": 0,
            "intelligence": 0,
            "wisdom": 0,
            "charisma": 0
        },
        "combat": {
            "armor_class": 10,
            "initiative": 0,
            "speed": 30,
            "hit_points": {
                "max": 10,
                "current": 10,
                "temporary": 0
            },
            "hit_dice": "1d8"
        },
        "equipment": {
            "weapons": [],
            "armor": [],
            "other": []
        },
        "spells": {
            "spell_slots": {
                "1st": 0,
                "2nd": 0,
                "3rd": 0,
                "4th": 0,
                "5th": 0,
                "6th": 0,
                "7th": 0,
                "8th": 0,
                "9th": 0
            },
            "known_spells": []
        },
        "features_and_traits": [],
        "proficiencies": {
            "languages": [],
            "tools": [],
            "weapons": [],
            "armor": []
        },
        "appearance": {
            "age": 0,
            "height": "",
            "weight": "",
            "eyes": "",
            "skin": "",
            "hair": ""
        },
        "backstory": "",
        "notes": ""
    }
}

save_json(serverid, ‘character_sheets.json', character_sheets)
"""

# character_sheets = load_json('character_sheets.json')

# Function to create a new character
def create_character(name, race, char_class, background, character_sheets, serverid):
    character_sheets[name] = {
        "basic_info": {
            "name": name,
            "race": race,
            "class": char_class,
            "background": background,
            "alignment": "",
            "level": 1,
            "experience": 0
        },
        "abilities": {
            "strength": 10,
            "dexterity": 10,
            "constitution": 10,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 10
        },
        "skills": {skill: 0 for skill in ["acrobatics", "animal_handling", "arcana", "athletics", "deception", "history", "insight", "intimidation", "investigation", "medicine", "nature", "perception", "performance", "persuasion", "religion", "sleight_of_hand", "stealth", "survival"]},
        "saving_throws": {save: 0 for save in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]},
        "combat": {
            "armor_class": 10,
            "initiative": 0,
            "speed": 30,
            "hit_points": {
                "max": 10,
                "current": 10,
                "temporary": 0
            },
            "hit_dice": "1d8"
        },
        "equipment": {
            "weapons": [],
            "armor": [],
            "other": []
        },
        "spells": {
            "spell_slots": {level: 0 for level in range(1, 10)},
            "known_spells": []
        },
        "features_and_traits": [],
        "proficiencies": {
            "languages": [],
            "tools": [],
            "weapons": [],
            "armor": []
        },
        "appearance": {
            "age": 0,
            "height": "",
            "weight": "",
            "eyes": "",
            "skin": "",
            "hair": ""
        },
        "backstory": "",
        "notes": ""
    }
    save_json(serverid, 'character_sheets.json', character_sheets)

# Function to update character ability scores
def update_ability_score(character, ability, score, character_sheets, serverid):
    if character in character_sheets and ability in character_sheets[character]["abilities"]:
        character_sheets[character]["abilities"][ability] = score
        save_json(serverid, 'character_sheets.json', character_sheets)

# Function to add a skill proficiency
def add_skill_proficiency(character, skill, character_sheets, serverid):
    if character in character_sheets and skill in character_sheets[character]["skills"]:
        character_sheets[character]["skills"][skill] = 1  # 1 indicates proficiency
        save_json(serverid, 'character_sheets.json', character_sheets)

# Function to calculate ability modifier
def calculate_modifier(score):
    return (score - 10) // 2

# Function to update hit points
def update_hit_points(character, current, max=None, temporary=0, character_sheets=None, serverid=0):
    if character in character_sheets:
        character_sheets[character]["combat"]["hit_points"]["current"] = current
        if max:
            character_sheets[character]["combat"]["hit_points"]["max"] = max
        character_sheets[character]["combat"]["hit_points"]["temporary"] = temporary
        save_json(serverid, 'character_sheets.json', character_sheets)

# Function to add a spell
def add_spell(character, spell_name, level, character_sheets, serverid):
    if character in character_sheets:
        character_sheets[character]["spells"]["known_spells"].append({"name": spell_name, "level": level})
        save_json(serverid, 'character_sheets.json', character_sheets)

# Function to add a feature or trait
def add_feature(character, feature_name, description, character_sheets, serverid):
    if character in character_sheets:
        character_sheets[character]["features_and_traits"].append({"name": feature_name, "description": description})
        save_json(serverid, 'character_sheets.json', character_sheets)

# Function to add equipment
def add_equipment(character, item_name, item_type, character_sheets, serverid):
    if character in character_sheets and item_type in character_sheets[character]["equipment"]:
        character_sheets[character]["equipment"][item_type].append(item_name)
        save_json(serverid, 'character_sheets.json', character_sheets)

# Function to update proficiency
def update_proficiency(character, proficiency_type, item, character_sheets, serverid):
    if character in character_sheets and proficiency_type in character_sheets[character]["proficiencies"]:
        character_sheets[character]["proficiencies"][proficiency_type].append(item)
        save_json(serverid, 'character_sheets.json', character_sheets)

# Function to update appearance
def update_appearance(character, attribute, value, character_sheets, serverid):
    if character in character_sheets and attribute in character_sheets[character]["appearance"]:
        character_sheets[character]["appearance"][attribute] = value
        save_json(serverid, 'character_sheets.json', character_sheets)

# Create embed helper function
def create_embed(title, description, color):
    return discord.Embed(title=title, description=description, color=color)

class CharacterView(View):
    def __init__(self, character, char_info):
        super().__init__()
        self.character = character
        self.char_info = char_info
        self.add_item(self.create_info_select())

    def create_info_select(self):
        select = Select(
            placeholder="Choose information to view",
            options=[
                discord.SelectOption(label="Basic Info", value="basic_info"),
                discord.SelectOption(label="Abilities", value="abilities"),
                discord.SelectOption(label="Skills", value="skills"),
                discord.SelectOption(label="Combat", value="combat"),
                discord.SelectOption(label="Equipment", value="equipment"),
                discord.SelectOption(label="Spells", value="spells"),
                discord.SelectOption(label="Features & Traits", value="features_and_traits"),
                discord.SelectOption(label="Proficiencies", value="proficiencies"),
                discord.SelectOption(label="Appearance", value="appearance"),
                discord.SelectOption(label="Backstory", value="backstory"),
            ]
        )
        select.callback = self.select_callback
        return select

    async def select_callback(self, interaction: discord.Interaction):
        option = interaction.data["values"][0]
        embed = self.create_info_embed(option)
        await interaction.response.edit_message(embed=embed)

    def create_info_embed(self, option):
        embed = create_embed(f"{self.character}'s {option.replace('_', ' ').title()}", "", discord.Color.blue())

        if option == "basic_info":
            basic_info = self.char_info["basic_info"]
            for key, value in basic_info.items():
                embed.add_field(name=key.replace('_', ' ').title(), value=str(value), inline=True)

        elif option == "abilities":
            abilities = self.char_info["abilities"]
            for ability, score in abilities.items():
                embed.add_field(name=ability.capitalize(), value=f"{score} ({calculate_modifier(score):+d})", inline=True)

        elif option == "skills":
            skills = self.char_info["skills"]
            sorted_skills = sorted(skills.items())
            mid = math.ceil(len(sorted_skills) / 2)
            
            left_column = "\n".join([f"{skill.replace('_', ' ').title()}: {bonus:+d}" for skill, bonus in sorted_skills[:mid]])
            right_column = "\n".join([f"{skill.replace('_', ' ').title()}: {bonus:+d}" for skill, bonus in sorted_skills[mid:]])
            
            embed.add_field(name="Skills (1/2)", value=left_column, inline=True)
            embed.add_field(name="Skills (2/2)", value=right_column, inline=True)

        elif option == "combat":
            combat = self.char_info["combat"]
            embed.add_field(name="Armor Class", value=str(combat["armor_class"]), inline=True)
            embed.add_field(name="Initiative", value=f"{combat['initiative']:+d}", inline=True)
            embed.add_field(name="Speed", value=f"{combat['speed']} ft", inline=True)
            embed.add_field(name="Hit Points", value=f"{combat['hit_points']['current']}/{combat['hit_points']['max']} (+{combat['hit_points']['temporary']} temp)", inline=True)
            embed.add_field(name="Hit Dice", value=combat["hit_dice"], inline=True)

        elif option == "equipment":
            equipment = self.char_info["equipment"]
            embed.add_field(name="Weapons", value=", ".join(equipment["weapons"]) or "None", inline=False)
            embed.add_field(name="Armor", value=", ".join(equipment["armor"]) or "None", inline=False)
            embed.add_field(name="Other", value=", ".join(equipment["other"]) or "None", inline=False)

        elif option == "spells":
            spells = self.char_info["spells"]
            spell_slots = spells["spell_slots"]
            spell_slots_str = "\n".join([f"Level {level}: {slots}" for level, slots in spell_slots.items()])
            embed.add_field(name="Spell Slots", value=spell_slots_str, inline=False)
            known_spells = [f"{spell['name']} (Level {spell['level']})" for spell in spells["known_spells"]]
            embed.add_field(name="Known Spells", value="\n".join(known_spells) or "None", inline=False)

        elif option == "features_and_traits":
            features = self.char_info["features_and_traits"]
            for feature in features:
                embed.add_field(name=feature["name"], value=feature["description"], inline=False)

        elif option == "proficiencies":
            proficiencies = self.char_info["proficiencies"]
            for category, items in proficiencies.items():
                embed.add_field(name=category.capitalize(), value=", ".join(items) or "None", inline=False)

        elif option == "appearance":
            appearance = self.char_info["appearance"]
            for key, value in appearance.items():
                embed.add_field(name=key.capitalize(), value=str(value), inline=True)

        elif option == "backstory":
            backstory = self.char_info["backstory"]
            embed.description = backstory[:4096] if backstory else "No backstory available."

        return embed

# Command to create a new character sheet
@tree.command(name="create_character", description="Create a new character sheet")
async def create_character_command(interaction: discord.Interaction, name: str, race: str, char_class: str, background: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    create_character(name, race, char_class, background, character_sheets)
    embed = create_embed("Character Created", f"Created character sheet for {name} ({race} {char_class}).", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# Command to update ability scores
@tree.command(name="update_ability", description="Update a character's ability score")
async def update_ability_score_command(interaction: discord.Interaction, character: str, ability: str, score: int):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    ability = ability.lower()
    if ability not in character_sheets[character]["abilities"]:
        embed = create_embed("Error", f"Ability '{ability}' is not valid.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    update_ability_score(character, ability, score,  character_sheets, str(interaction.guild_id))
    modifier = calculate_modifier(score)
    embed = create_embed("Ability Updated", f"{ability.capitalize()} of {character} updated to {score} (Modifier: {modifier:+d}).", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# Command to add skill proficiency
@tree.command(name="add_skill", description="Add a skill proficiency to a character")
async def add_skill_proficiency_command(interaction: discord.Interaction, character: str, skill: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    skill = skill.lower().replace(" ", "_")
    if skill not in character_sheets[character]["skills"]:
        embed = create_embed("Error", f"Skill '{skill}' is not valid.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    add_skill_proficiency(character, skill,  character_sheets, str(interaction.guild_id))
    embed = create_embed("Skill Proficiency Added", f"Added proficiency in {skill.replace('_', ' ').title()} for {character}.", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# Command to view character information
@tree.command(name="view_character", description="View detailed character information")
async def view_character(interaction: discord.Interaction, character: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    char_info = character_sheets[character]
    
    embed = create_embed(f"{character}'s Character Sheet", "Select an option below to view more details.", discord.Color.blue())
    view = CharacterView(character, char_info)
    
    await interaction.response.send_message(embed=embed, view=view)

# New command to add a feature to a character
@tree.command(name="add_feature", description="Add a feature or trait to a character")
async def add_feature_command(interaction: discord.Interaction, character: str, feature_name: str, description: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    add_feature(character, feature_name, description,  character_sheets, str(interaction.guild_id))
    embed = create_embed("Feature Added", f"Added '{feature_name}' to {character}'s features and traits.", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# New command to add a spell to a character
@tree.command(name="add_spell", description="Add a spell to a character's spell list")
async def add_spell_command(interaction: discord.Interaction, character: str, spell_name: str, level: int):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    add_spell(character, spell_name, level,  character_sheets, str(interaction.guild_id))
    embed = create_embed("Spell Added", f"Added '{spell_name}' (Level {level}) to {character}'s spell list.", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# New command to update hit points
@tree.command(name="update_hp", description="Update a character's hit points")
async def update_hp_command(interaction: discord.Interaction, character: str, current: int, max: int = None, temporary: int = 0):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    update_hit_points(character, current, max, temporary,  character_sheets, str(interaction.guild_id))
    embed = create_embed("HP Updated", f"Updated {character}'s hit points. Current: {current}, Max: {max if max else 'unchanged'}, Temp: {temporary}", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# New command to add equipment to a character
@tree.command(name="add_equipment", description="Add equipment to a character")
async def add_equipment_command(interaction: discord.Interaction, character: str, item_name: str, item_type: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    if item_type not in ["weapons", "armor", "other"]:
        embed = create_embed("Error", "Item type must be 'weapons', 'armor', or 'other'.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    add_equipment(character, item_name, item_type,  character_sheets, str(interaction.guild_id))
    embed = create_embed("Equipment Added", f"Added '{item_name}' to {character}'s {item_type}.", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# New command to update proficiencies
@tree.command(name="add_proficiency", description="Add a proficiency to a character")
async def add_proficiency_command(interaction: discord.Interaction, character: str, proficiency_type: str, item: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    if proficiency_type not in ["languages", "tools", "weapons", "armor"]:
        embed = create_embed("Error", "Proficiency type must be 'languages', 'tools', 'weapons', or 'armor'.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    update_proficiency(character, proficiency_type, item,  character_sheets, str(interaction.guild_id))
    embed = create_embed("Proficiency Added", f"Added '{item}' to {character}'s {proficiency_type} proficiencies.", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# New command to update appearance
@tree.command(name="update_appearance", description="Update a character's appearance")
async def update_appearance_command(interaction: discord.Interaction, character: str, attribute: str, value: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    if attribute not in ["age", "height", "weight", "eyes", "skin", "hair"]:
        embed = create_embed("Error", "Invalid appearance attribute.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    update_appearance(character, attribute, value,  character_sheets, str(interaction.guild_id))
    embed = create_embed("Appearance Updated", f"Updated {character}'s {attribute} to '{value}'.", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# New command to update backstory
@tree.command(name="update_backstory", description="Update a character's backstory")
async def update_backstory_command(interaction: discord.Interaction, character: str, backstory: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    character_sheets[character]["backstory"] = backstory
    save_json(str(interaction.guild.id), 'character_sheets.json', character_sheets)
    embed = create_embed("Backstory Updated", f"Updated {character}'s backstory.", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# New command to add notes
@tree.command(name="add_note", description="Add a note to a character")
async def add_note_command(interaction: discord.Interaction, character: str, note: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    character_sheets[character]["notes"] += f"\n- {note}"
    save_json(str(interaction.guild.id), 'character_sheets.json', character_sheets)
    embed = create_embed("Note Added", f"Added note to {character}'s character sheet.", discord.Color.green())
    await interaction.response.send_message(embed=embed)

# New command to level up a character
@tree.command(name="level_up", description="Level up a character")
async def level_up_command(interaction: discord.Interaction, character: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    character_sheets[character]["basic_info"]["level"] += 1
    save_json(str(interaction.guild.id), 'character_sheets.json', character_sheets)
    new_level = character_sheets[character]["basic_info"]["level"]
    embed = create_embed("Level Up", f"{character} has leveled up to level {new_level}!", discord.Color.gold())
    await interaction.response.send_message(embed=embed)

# New command to roll dice for a character
@tree.command(name="char_roll", description="Roll dice for a character")
async def roll_command(interaction: discord.Interaction, character: str, dice: str):
    character_sheets = load_json(str(interaction.guild_id), 'character_sheets.json')
    if character not in character_sheets:
        embed = create_embed("Error", f"Character '{character}' not found.", discord.Color.red())
        await interaction.response.send_message(embed=embed)
        return
    
    try:
        # Use the advanced dice parsing function
        rolls, modifier = parse_roll_string(dice)
        results = []
        details = []
        
        for num, sides in rolls:
            if abs(num) > 100 or abs(sides) > 1000:
                raise ValueError(f"Number of dice or sides too high: {abs(num)}d{abs(sides)}")
            
            # Roll dice for each group
            roll_results = roll_dice(num, sides)
            
            # If it's a negative dice roll, we reverse the value
            if num < 0:
                results.extend([-r for r in roll_results])
                details.append(f"-{abs(num)}d{sides}: {[-r for r in roll_results]}")
            else:
                results.extend(roll_results)
                details.append(f"{num}d{sides}: {roll_results}")
        
        total = sum(results) + modifier
        
        # Build the result message
        description = f"Rolling {dice} for {character}:\n**Result: {total}**"
        if results:
            description += f" (Dice: {sum(results)}"
            if modifier != 0:
                description += f" {'+' if modifier > 0 else '-'} {abs(modifier)}"
            description += ")"
      
        
        # Create the embed message with details
        embed = create_embed("Dice Roll", description, discord.Color.red())
        await interaction.response.send_message(embed=embed)
    
    except ValueError as e:
        # Handle any errors like dice limit exceeded or parsing issues
        error_embed = create_embed("Error", str(e), discord.Color.red())
        await interaction.response.send_message(embed=error_embed)



# Creator ID
CREATOR_ID = 857925971004882975

# Sync the tree with the bot (registers the slash commands)
@client.event
async def on_ready():
    await tree.sync()
    print(f'Logged in as {client.user}!')

# Define the slash command using the tree structure

@tree.command(name='creator_stats', description='Displays bot stats, only for Gentle_Ego.')
async def creator_stats(interaction: discord.Interaction):
    # Check if the user is the bot creator
    if interaction.user.id != CREATOR_ID:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    # Get a list of guilds (servers) the bot is in
    guilds = client.guilds
    
    # Number of servers
    total_servers = len(guilds)

    # Sort guilds by member count in descending order
    top_guilds = sorted(guilds, key=lambda g: g.member_count, reverse=True)[:5]

    # Construct the description
    description = f"Bot is currently in **{total_servers}** servers.\n\n**Top 5 Servers by Member Count:**\n"

    for idx, guild in enumerate(top_guilds, 1):
        owner = await client.fetch_user(guild.owner_id)
        owner_name = f"{owner.name}#{owner.discriminator}" if owner else "Unknown"
        creation_date = guild.created_at.strftime('%Y-%m-%d')
        humans = len([member for member in guild.members if not member.bot])
        bots = len([member for member in guild.members if member.bot])
        online = len([member for member in guild.members if member.status == discord.Status.online])
        features = ', '.join(guild.features) if guild.features else "None"

        description += (
            f"{idx}. **{guild.name}**\n"
            f"   - **Members:** {guild.member_count}\n"
            f"   - **Owner:** {owner_name} (ID: {guild.owner_id})\n"
            f"   - **Creation Date:** {creation_date}\n"
            f"   - **Boost Level:** {guild.premium_tier}\n"
            f"   - **Humans:** {humans}, **Bots:** {bots}\n"
            f"   - **Online:** {online}\n"
            f"   - **Features:** {features}\n"
        )

    # Calculate the average members per server
    average_members = sum(g.member_count for g in guilds) / total_servers

    # Additional information
    additional_info = (
        f"\n**Total Commands:** {len(tree.get_commands())}\n"
        f"**Bot Latency:** {round(client.latency * 1000, 2)} ms\n"
        f"**Average Members per Server:** {round(average_members, 2)}"
    )

    # Creating the embed to display the stats
    embed = discord.Embed(title="Bot Stats", description=description + additional_info, color=discord.Color.blue())

    # Respond with the embed message
    await interaction.response.send_message(embed=embed)

client.run('BOT_TOKEN')
