import discord
from discord.ext import commands
import requests
from bs4 import BeautifulSoup
from table2ascii import table2ascii as t2a, PresetStyle

# Function to fetch and parse mod data from the SWGOH.gg Mod Meta Report
def fetch_mod_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch data. Error: {e}")
        return []
    
    soup = BeautifulSoup(response.content, 'lxml')
    return parse_mod_data(soup)

def parse_mod_data(soup):
    mod_data = []
    rows = soup.find_all('tr')
    for row in rows:
        character_tag = row.find('a')
        if not character_tag:
            continue
        character = character_tag.text.strip()
        sets = row.find_all('div', class_='stat-mod-set-def-icon')
        set_names = [s['title'].strip().split()[-1].lower() for s in sets]
        set_names = ['critical chance' if s == 'chance' else 'critical damage' if s == 'damage' else s for s in set_names]
        primary_stats = row.find_all('td')
        if len(primary_stats) < 6:
            continue
        receiver_stat = primary_stats[2].text.strip().lower()
        holo_array_stat = primary_stats[3].text.strip().lower()
        data_bus_stat = primary_stats[4].text.strip().lower()
        multiplexer_stat = primary_stats[5].text.strip().lower()
        mod_data.append({
            'character': character,
            'set_names': set_names,
            'receiver_stat': receiver_stat,
            'holo_array_stat': holo_array_stat,
            'data_bus_stat': data_bus_stat,
            'multiplexer_stat': multiplexer_stat
        })
    return mod_data

# Function to filter characters based on the selected set, shape, and primary stat
def filter_characters(set_name, shape_choice, primary_choice, mod_data):
    primary_stat_options = {
        'arrow': ["health", "protection", "accuracy", "speed", "offense", "critical avoidance", "defense"],
        'triangle': ["critical chance", "critical damage", "defense", "health", "offense", "protection"],
        'cross': ["offense", "tenacity", "protection", "potency", "defense", "health"],
        'circle': ["health", "protection"]
    }

    filtered_characters = []

    for mod in mod_data:
        if set_name in mod['set_names']:
            if not shape_choice and not primary_choice:
                filtered_characters.append(mod['character'])
            else:
                stat_key = ''
                valid_stats = []
                if shape_choice == 'arrow':
                    valid_stats = primary_stat_options['arrow']
                    stat_key = 'receiver_stat'
                elif shape_choice == 'triangle':
                    valid_stats = primary_stat_options['triangle']
                    stat_key = 'holo_array_stat'
                elif shape_choice == 'cross':
                    valid_stats = primary_stat_options['cross']
                    stat_key = 'multiplexer_stat'
                elif shape_choice == 'circle':
                    valid_stats = primary_stat_options['circle']
                    stat_key = 'data_bus_stat'
                
                if primary_choice and stat_key:
                    if any(primary_choice.lower() == stat.strip().lower() for stat in mod[stat_key].split('/')):
                        filtered_characters.append(mod['character'])
    
    return filtered_characters

# Function to sort and identify set, shape, and primary stat from the input arguments
def sort_arguments(args_list):
    valid_sets = ["health", "critical chance", "critical damage", "tenacity", "potency", "speed", "offense", "defense"]
    valid_shapes = ["arrow", "triangle", "cross", "circle"]
    valid_primaries = ["health", "protection", "accuracy", "speed", "offense", "critical avoidance", "defense", 
                       "critical chance", "critical damage", "tenacity", "potency"]

    set_name = ""
    shape_choice = ""
    primary_choice = ""

    i = 0
    while i < len(args_list):
        if not set_name and (args_list[i] in valid_sets or (args_list[i] == "critical" and i + 1 < len(args_list) and args_list[i + 1] in ["chance", "damage"])):
            # Check for "critical chance" and "critical damage" sets
            if args_list[i] == "critical":
                set_name = f"critical {args_list[i + 1]}"
                i += 1  # Skip the next word as it is part of the set name
            else:
                set_name = args_list[i]
        elif not shape_choice and args_list[i] in valid_shapes:
            shape_choice = args_list[i]
        elif not primary_choice:
            # Check for "critical avoidance", "critical chance", and "critical damage" primaries
            if args_list[i] == "critical" and i + 1 < len(args_list) and args_list[i + 1] in ["avoidance", "chance", "damage"]:
                primary_choice = f"critical {args_list[i + 1]}"
                i += 1  # Skip the next word as it is part of the primary stat
            elif args_list[i] in valid_primaries:
                primary_choice = args_list[i]
        i += 1

    print(f"Sorted Arguments - Set: {set_name}, Shape: {shape_choice}, Primary: {primary_choice}")
    return set_name, shape_choice, primary_choice

# Function to create a formatted table and send it as a message
def create_table(characters, columns=2):
    while len(characters) % columns != 0:
        characters.append("---")
    
    rows = [characters[i:i + columns] for i in range(0, len(characters), columns)]
    table = t2a(
        header=[f"Column {i + 1}" for i in range(columns)],
        body=rows,
        style=PresetStyle.thin_compact
    )
    return table

# Function to split and send messages if they exceed 2000 characters
async def send_split_message(ctx, characters, columns=2):
    max_length = 2000
    index = 0

    while index < len(characters):
        # Create a table and format it
        chunk = characters[index:]
        table_output = create_table(chunk, columns=columns)
        formatted_message = f"```\n{table_output}\n```"

        # Ensure message does not exceed max length
        while len(formatted_message) > max_length:
            split_index = formatted_message.rfind('\n', 0, max_length)
            if split_index == -1:
                split_index = max_length
            await ctx.send(formatted_message[:split_index])
            formatted_message = formatted_message[split_index:].strip()

        await ctx.send(formatted_message)
        break  # Exit the loop after sending the first message

        # Move to next chunk
        index += len(chunk)

# Create the bot instance
intents = discord.Intents.default()
intents.message_content = True  # Enable the intent to read message content

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot connected as {bot.user}')

@bot.command()
async def find_mod(ctx, *, args):
    args = args.lower()
    args_list = args.split()
    set_name, shape_choice, primary_choice = sort_arguments(args_list)

    if not set_name:
        await ctx.send("Invalid input. Please provide at least a set name.")
        return

    url = "https://swgoh.gg/stats/mod-meta-report/guilds_100_gp/"
    mod_data = fetch_mod_data(url)
    if not mod_data:
        await ctx.send("No data found or failed to fetch data.")
        return

    filtered_characters = filter_characters(set_name, shape_choice, primary_choice, mod_data)
    if not filtered_characters:
        await ctx.send("No characters found with the specified criteria.")
        return

    # Send messages with table formatting
    await send_split_message(ctx, filtered_characters, columns=2)

# Run the bot with your token
bot.run('Token')
