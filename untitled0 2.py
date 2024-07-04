import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup

# Function to fetch and parse mod data from the SWGOH.gg Mod Meta Report
def fetch_mod_data():
    url = "https://swgoh.gg/stats/mod-meta-report/guilds_100_gp/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch data. HTTP Status Code: {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, 'lxml')

    mod_data = []

    # Find all character rows
    rows = soup.find_all('tr')
    for row in rows:
        # Find character name
        character_tag = row.find('a')
        if not character_tag:
            continue
        character = character_tag.text.strip()

        # Find mod sets
        sets = row.find_all('div', class_='stat-mod-set-def-icon')
        set_names = [s['title'].strip().split()[-1].lower() for s in sets]
        
        # Fix for critical chance and critical damage
        set_names = ['critical chance' if s == 'chance' else 'critical damage' if s == 'damage' else s for s in set_names]
        
        # Find primary stats
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
        'arrow': ["Health", "Protection", "Accuracy", "Speed", "Offense", "Critical Avoidance", "Defense"],
        'triangle': ["Critical Chance", "Critical Damage", "Defense", "Health", "Offense", "Protection"],
        'cross': ["Offense", "Tenacity", "Protection", "Potency", "Defense", "Health"],
        'circle': ["Health", "Protection"]
    }

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
    else:
        valid_stats = []
        stat_key = ''

    filtered_characters = []
    for mod in mod_data:
        if set_name in mod['set_names']:
            # Check if primary_choice matches any of the primary stats for the current character
            if any(primary_choice.lower() == stat.strip().lower() for stat in mod[stat_key].split('/')):
                filtered_characters.append(mod['character'])

    return filtered_characters

# Function to handle shape selection and update primary stat dropdown
def on_shape_select(event):
    shape_choice = shape_var.get().lower()

    if shape_choice == 'arrow':
        primary_menu['values'] = ["Health", "Protection", "Accuracy", "Speed", "Offense", "Critical Avoidance", "Defense"]
    elif shape_choice == 'triangle':
        primary_menu['values'] = ["Critical Chance", "Critical Damage", "Defense", "Health", "Offense", "Protection"]
    elif shape_choice == 'cross':
        primary_menu['values'] = ["Offense", "Tenacity", "Protection", "Potency", "Defense", "Health"]
    elif shape_choice == 'circle':
        primary_menu['values'] = ["Health", "Protection"]

    primary_var.set(primary_menu['values'][0])  # Set default value

# Function to handle selection and display the results
def on_select():
    set_choice = set_var.get().lower()
    shape_choice = shape_var.get().lower()
    primary_choice = primary_var.get().lower()

    mod_data = fetch_mod_data()
    if not mod_data:
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "No data found or failed to fetch data.")
        return
    
    filtered_characters = filter_characters(set_choice, shape_choice, primary_choice, mod_data)
    
    result_text.delete(1.0, tk.END)
    result_text.insert(tk.END, f"Characters with {set_choice.capitalize()} set, {shape_choice.capitalize()} shape, and {primary_choice.capitalize()} primary:\n\n")
    
    # Print results in two columns
    num_characters = len(filtered_characters)
    middle_index = (num_characters + 1) // 2  # Split into two columns
    
    for i, character in enumerate(filtered_characters):
        if i == middle_index:
            result_text.insert(tk.END, "\n")
        result_text.insert(tk.END, f"{character}\n")

# Function to reset all selections and results
def reset_selection():
    set_var.set("")  # Reset set dropdown
    shape_var.set("")  # Reset shape dropdown
    primary_var.set("")  # Reset primary stat dropdown
    result_text.delete(1.0, tk.END)  # Clear result text

# Initialize the main window
root = tk.Tk()
root.title("SWGOH Mod Finder")

# Set dropdown options
set_options = ["Health", "Critical Chance", "Critical Damage", "Tenacity", "Potency", "Speed", "Offense"]
shape_options = ["Arrow", "Triangle", "Cross", "Circle"]

# Create StringVars for the dropdown selections
set_var = tk.StringVar()
shape_var = tk.StringVar()
primary_var = tk.StringVar()

# Set dropdown menu for Set
set_label = tk.Label(root, text="Select Set:")
set_label.pack(pady=5)
set_menu = ttk.Combobox(root, textvariable=set_var, values=set_options, state='readonly')
set_menu.pack(pady=5)

# Set dropdown menu for Shape
shape_label = tk.Label(root, text="Select Shape:")
shape_label.pack(pady=5)
shape_menu = ttk.Combobox(root, textvariable=shape_var, values=shape_options, state='readonly')
shape_menu.pack(pady=5)
shape_menu.bind("<<ComboboxSelected>>", on_shape_select)

# Set dropdown menu for Primary Stat
primary_label = tk.Label(root, text="Select Primary Stat:")
primary_label.pack(pady=5)
primary_menu = ttk.Combobox(root, textvariable=primary_var, state='readonly')
primary_menu.pack(pady=5)

# Submit button
submit_button = tk.Button(root, text="Submit", command=on_select)
submit_button.pack(pady=20)

# Reset button
reset_button = tk.Button(root, text="Reset", command=reset_selection)
reset_button.pack(pady=5)

# Result label (Text widget)
result_text = tk.Text(root, wrap=tk.WORD, width=50, height=20)
result_text.pack(pady=10)

# Start the GUI event loop
root.mainloop()
