#!/usr/bin/env python3
"""
Lunch Quest: A CLI Game with Textual GUI
Theme: Lunch Rush at the Secret Garden Cafe
Protagonist: Simon Kennedy, Electrical Engineer & University Lecturer

Features:
1. Inventory & Ingredients - Collect ingredients from cafes to create power-ups
2. Skill Progression (XP & Levels) - Earn engineering XP and level up
3. Dynamic Events - Random events that affect gameplay
4. Multiple Locations - Different cafes to visit
5. Mini-Game Variety - Various engineering puzzles
6. Branching Storylines - Choices leading to different career paths
7. Multiplayer Mode - Turn-based challenge mode
8. Save/Load & Leaderboards - Store progress and compare scores
"""
import curses
import time
import random
import sys
import json
import os
from collections import defaultdict

# Game constants
DAYS_PER_WEEK = 7
TOTAL_DAYS = 14  # two-week simulation including weekends
WORK_DAYS = [1, 3]  # Tuesday & Thursday
START_MONEY = 50
LUNCH_COST_RANGE = (5, 15)
CLASS_DURATION = 2  # hours per class session
TRAVEL_TIME = 1     # hours between class & cafe
PUZZLE_TIME_LIMIT = 30  # seconds
LEVEL_UP_XP = 50
SAVE_FILE = "lunch_quest_save.json"
LEADERBOARD_FILE = "lunch_quest_leaderboard.json"

# Cafe locations
LOCATIONS = {
    'Secret Garden Cafe': {
        'description': 'A peaceful cafe hidden in the university gardens',
        'specialty': 'Organic salads and herbal teas',
        'price_modifier': 1.0,
        'xp_bonus': 0
    },
    'Circuit Board Food Truck': {
        'description': 'A tech-themed food truck with electronic decorations',
        'specialty': 'Fusion tacos and energy drinks',
        'price_modifier': 0.8,
        'xp_bonus': 5
    },
    'International Food Court': {
        'description': 'A vibrant food court with cuisines from around the world',
        'specialty': 'Global dishes and exotic flavors',
        'price_modifier': 1.2,
        'xp_bonus': 10
    },
    'Faculty Lounge Cafe': {
        'description': 'A quiet cafe exclusively for university staff',
        'specialty': 'Premium coffee and artisanal sandwiches',
        'price_modifier': 1.5,
        'xp_bonus': 15
    }
}

# Ingredients that can be collected
INGREDIENTS = [
    'Mystery Spice',
    'Quantum Coffee Beans',
    'Silicon Chips',
    'Conductive Honey',
    'Binary Pepper',
    'Logic Gate Lettuce',
    'Resistor Rice',
    'Capacitor Carrots',
    'Diode Dressing',
    'Transistor Tomatoes'
]

# Recipes that can be crafted
RECIPES = {
    'Brain Booster': {
        'ingredients': ['Quantum Coffee Beans', 'Conductive Honey'],
        'effect': 'Doubles XP gain for one day',
        'duration': 1
    },
    'Energy Circuit': {
        'ingredients': ['Silicon Chips', 'Binary Pepper', 'Resistor Rice'],
        'effect': 'Reduces time spent on activities by 1 hour',
        'duration': 1
    },
    'Focus Field Generator': {
        'ingredients': ['Logic Gate Lettuce', 'Diode Dressing', 'Mystery Spice'],
        'effect': 'Increases puzzle success chance',
        'duration': 2
    },
    'Happiness Amplifier': {
        'ingredients': ['Transistor Tomatoes', 'Capacitor Carrots', 'Conductive Honey'],
        'effect': 'Doubles happiness gain for two days',
        'duration': 2
    }
}

# Career paths
CAREER_PATHS = {
    'Research': {
        'description': 'Focus on groundbreaking electrical engineering research',
        'money_modifier': 1.2,
        'xp_modifier': 1.5,
        'happiness_modifier': 0.8
    },
    'Startup': {
        'description': 'Join a tech startup as lead engineer',
        'money_modifier': 1.5,
        'xp_modifier': 1.0,
        'happiness_modifier': 0.9
    },
    'Academia': {
        'description': 'Commit to university teaching and mentoring',
        'money_modifier': 0.8,
        'xp_modifier': 1.2,
        'happiness_modifier': 1.3
    },
    'Sabbatical': {
        'description': 'Take time off to travel and explore new ideas',
        'money_modifier': 0.5,
        'xp_modifier': 0.8,
        'happiness_modifier': 1.5
    }
}

# Mini-games
# FPGA Logic Design Puzzle
def fpga_logic_puzzle(stdscr):
    """Puzzle to determine the output of a simple FPGA logic circuit"""
    inputs = [random.randint(0, 1) for _ in range(3)]
    logic_gates = ['AND', 'OR', 'XOR']
    gate1 = random.choice(logic_gates)
    gate2 = random.choice(logic_gates)

    # Simulate the circuit
    intermediate = {
        'AND': inputs[0] & inputs[1],
        'OR': inputs[0] | inputs[1],
        'XOR': inputs[0] ^ inputs[1]
    }[gate1]
    output = {
        'AND': intermediate & inputs[2],
        'OR': intermediate | inputs[2],
        'XOR': intermediate ^ inputs[2]
    }[gate2]

    stdscr.clear()
    stdscr.addstr(1, 1, "FPGA Logic Design Puzzle!")
    stdscr.addstr(3, 1, f"Inputs: A={inputs[0]}, B={inputs[1]}, C={inputs[2]}")
    stdscr.addstr(4, 1, f"Gate 1: {gate1} (A, B)")
    stdscr.addstr(5, 1, f"Gate 2: {gate2} (Result of Gate 1, C)")
    stdscr.addstr(7, 1, "What is the final output? (0/1): ")
    stdscr.refresh()

    user_input = ""
    while True:
        ch = stdscr.getch()
        if ch in (ord('0'), ord('1')):
            user_input = chr(ch)
            break
        elif ch in (curses.KEY_ENTER, 10, 13):
            break

    try:
        return int(user_input) == output
    except ValueError:
        return False

# FPGA Resource Utilization Puzzle
def fpga_resource_puzzle(stdscr):
    """Puzzle to calculate FPGA resource utilization"""
    total_luts = random.randint(1000, 5000)
    used_luts = random.randint(500, total_luts)

    stdscr.clear()
    stdscr.addstr(1, 1, "FPGA Resource Utilization Puzzle!")
    stdscr.addstr(3, 1, f"Total LUTs available: {total_luts}")
    stdscr.addstr(4, 1, f"LUTs used: {used_luts}")
    stdscr.addstr(6, 1, "What is the percentage of LUTs used? (Round to nearest integer): ")
    stdscr.refresh()

    user_input = ""
    while True:
        ch = stdscr.getch()
        if ch in (8, 127, curses.KEY_BACKSPACE):
            if user_input:
                user_input = user_input[:-1]
                stdscr.addstr(6, 50, " " * 10)
                stdscr.addstr(6, 50, user_input)
        elif ch in (curses.KEY_ENTER, 10, 13):
            break
        elif ch >= 48 and ch <= 57:  # ASCII codes for 0-9
            user_input += chr(ch)
            stdscr.addstr(6, 50, user_input)
        stdscr.refresh()

    try:
        correct_answer = round((used_luts / total_luts) * 100)
        return int(user_input) == correct_answer
    except ValueError:
        return False




def resistor_color_puzzle(stdscr):
    """Puzzle to decode resistor color bands"""
    colors = ['Black', 'Brown', 'Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Violet', 'Grey', 'White']
    
    band1 = random.randint(0, 9)
    band2 = random.randint(0, 9)
    multiplier = random.randint(0, 5)
    
    value = (band1 * 10 + band2) * (10 ** multiplier)
    
    stdscr.clear()
    stdscr.addstr(1, 1, f"Resistor Color Puzzle!")
    stdscr.addstr(3, 1, f"Band 1: {colors[band1]} ({band1})")
    stdscr.addstr(4, 1, f"Band 2: {colors[band2]} ({band2})")
    stdscr.addstr(5, 1, f"Multiplier: {colors[multiplier]} (10^{multiplier})")
    stdscr.addstr(7, 1, f"What is the resistor value in ohms? ")
    stdscr.refresh()
    
    start = time.time()
    stdscr.timeout(1000)
    
    user_input = ""
    while True:
        if time.time() - start > PUZZLE_TIME_LIMIT:
            return False
            
        ch = stdscr.getch()
        
        # Handle backspace
        if ch in (8, 127, curses.KEY_BACKSPACE):
            if user_input:
                user_input = user_input[:-1]
                stdscr.addstr(7, 39, " " * 20)
                stdscr.addstr(7, 39, user_input)
        # Handle enter key
        elif ch in (curses.KEY_ENTER, 10, 13):
            break
        # Handle digit keys
        elif ch >= 48 and ch <= 57:  # ASCII codes for 0-9
            user_input += chr(ch)
            stdscr.addstr(7, 39, user_input)
        
        stdscr.refresh()
    
    try:
        return int(user_input) == value
    except ValueError:
        return False

def ohms_law_puzzle(stdscr):
    """Puzzle to calculate using Ohm's Law: V = IR"""
    # Randomly choose two values and ask for the third
    choice = random.randint(0, 2)
    
    if choice == 0:  # Calculate voltage
        current = random.randint(1, 10)
        resistance = random.randint(10, 100)
        answer = current * resistance
        
        stdscr.clear()
        stdscr.addstr(1, 1, "Ohm's Law Puzzle!")
        stdscr.addstr(3, 1, f"Given:")
        stdscr.addstr(4, 1, f"Current (I) = {current} A")
        stdscr.addstr(5, 1, f"Resistance (R) = {resistance} Ω")
        stdscr.addstr(7, 1, f"Calculate the Voltage (V): ")
    
    elif choice == 1:  # Calculate current
        voltage = random.randint(10, 100)
        resistance = random.randint(10, 100)
        answer = voltage / resistance
        
        stdscr.clear()
        stdscr.addstr(1, 1, "Ohm's Law Puzzle!")
        stdscr.addstr(3, 1, f"Given:")
        stdscr.addstr(4, 1, f"Voltage (V) = {voltage} V")
        stdscr.addstr(5, 1, f"Resistance (R) = {resistance} Ω")
        stdscr.addstr(7, 1, f"Calculate the Current (I): ")
    
    else:  # Calculate resistance
        voltage = random.randint(10, 100)
        current = random.randint(1, 10)
        answer = voltage / current
        
        stdscr.clear()
        stdscr.addstr(1, 1, "Ohm's Law Puzzle!")
        stdscr.addstr(3, 1, f"Given:")
        stdscr.addstr(4, 1, f"Voltage (V) = {voltage} V")
        stdscr.addstr(5, 1, f"Current (I) = {current} A")
        stdscr.addstr(7, 1, f"Calculate the Resistance (R): ")
    
    stdscr.refresh()
    
    start = time.time()
    stdscr.timeout(1000)
    
    user_input = ""
    while True:
        if time.time() - start > PUZZLE_TIME_LIMIT:
            return False
            
        ch = stdscr.getch()
        
        # Handle backspace
        if ch in (8, 127, curses.KEY_BACKSPACE):
            if user_input:
                user_input = user_input[:-1]
                stdscr.addstr(7, 35, " " * 20)
                stdscr.addstr(7, 35, user_input)
        # Handle enter key
        elif ch in (curses.KEY_ENTER, 10, 13):
            break
        # Handle digit keys and decimal point
        elif (ch >= 48 and ch <= 57) or ch == 46:  # ASCII codes for 0-9 and '.'
            user_input += chr(ch)
            stdscr.addstr(7, 35, user_input)
        
        stdscr.refresh()
    
    try:
        # Allow a small margin of error for floating point calculations
        return abs(float(user_input) - answer) < 0.1
    except ValueError:
        return False

# Logic gate puzzle (enhanced from original)
def circuit_puzzle(stdscr):
    gates = ['AND', 'OR', 'XOR', 'NAND', 'NOR', 'XNOR']
    gate = random.choice(gates)
    a, b = random.randint(0, 1), random.randint(0, 1)
    
    answer = {
        'AND': a & b,
        'OR': a | b,
        'XOR': a ^ b,
        'NAND': 1 - (a & b),
        'NOR': 1 - (a | b),
        'XNOR': 1 - (a ^ b)
    }[gate]
    
    stdscr.clear()
    stdscr.addstr(1, 1, "Circuit Puzzle!")
    stdscr.addstr(3, 1, f"What is the output of {a} {gate} {b}? (0/1): ")
    stdscr.refresh()
    
    start = time.time()
    stdscr.timeout(1000)
    
    user_input = ""
    while True:
        elapsed = time.time() - start
        if elapsed > PUZZLE_TIME_LIMIT:
            return False
            
        # Show time remaining
        time_left = int(PUZZLE_TIME_LIMIT - elapsed)
        stdscr.addstr(5, 1, f"Time remaining: {time_left} seconds")
        
        ch = stdscr.getch()
        
        # Handle backspace
        if ch in (8, 127, curses.KEY_BACKSPACE):
            if user_input:
                user_input = user_input[:-1]
                stdscr.addstr(3, 40, " ")
                stdscr.addstr(3, 40, user_input)
        # Handle enter key
        elif ch in (curses.KEY_ENTER, 10, 13):
            break
        # Handle 0 and 1 keys
        elif ch in (ord('0'), ord('1')):
            user_input = chr(ch)
            stdscr.addstr(3, 40, user_input)
        
        stdscr.refresh()
    
    try:
        return int(user_input) == answer
    except ValueError:
        return False

# Generate menu with random prices
def generate_menu(location):
    """Generate a menu with prices adjusted for location"""
    base_items = ['Salad', 'Sandwich', 'Pasta', 'Soup', 'Cake']
    specialty = LOCATIONS[location]['specialty'].split(' and ')
    
    # Add location specialties to the menu
    items = base_items + specialty
    
    # Make sure we have 5 unique items
    if len(items) > 5:
        items = random.sample(items, 5)
    
    price_mod = LOCATIONS[location]['price_modifier']
    return {i+1: (item, int(random.randint(*LUNCH_COST_RANGE) * price_mod)) 
            for i, item in enumerate(items)}

# Dynamic random events
def dynamic_event(stdscr, game):
    chance = random.random()
    if chance < 0.3:  # Increased chance for events
        events = [
            ('Surprise Guest Speaker! +20 XP', lambda g: setattr(g, 'xp', g.xp + 20)),
            ('Cafe Discount Day! -$5 for next lunch', lambda g: setattr(g, 'discount', 5)),
            ('Lunch Rush Traffic! +1 hour delay', lambda g: setattr(g, 'time', g.time + 1)),
            ('Free coffee refills! +10 happiness', lambda g: setattr(g, 'happiness', min(100, g.happiness + 10))),
            ('Found a $10 bill on the ground!', lambda g: setattr(g, 'money', g.money + 10)),
            ('Met an old friend! Shared lunch (-$5, +15 happiness)', 
                lambda g: (setattr(g, 'money', g.money - 5), setattr(g, 'happiness', min(100, g.happiness + 15)))),
            ('Power outage at the campus! Class canceled (+2 free hours)', lambda g: setattr(g, 'time', max(9, g.time - 2))),
            ('Spontaneous department meeting (+1 hour, +5 XP)', 
                lambda g: (setattr(g, 'time', g.time + 1), setattr(g, 'xp', g.xp + 5)))
        ]
        desc, effect = random.choice(events)
        stdscr.clear()
        game.draw_header()
        stdscr.addstr(3, 5, f"Dynamic Event: {desc}")
        effect(game)
        stdscr.addstr(5, 5, "Press Enter to continue...")
        stdscr.refresh()
        stdscr.getch()  # Wait for user input before continuing

# Save game function
def save_game(game):
    save_data = {
        'day': game.day,
        'time': game.time,
        'money': game.money,
        'happiness': game.happiness,
        'inventory': game.inventory,
        'ingredients': game.ingredients,
        'active_effects': game.active_effects,
        'xp': game.xp,
        'level': game.level,
        'career_path': game.career_path,
        'visited_locations': game.visited_locations,
        'discount': game.discount,
        'player_name': game.player_name
    }
    
    with open(SAVE_FILE, 'w') as f:
        json.dump(save_data, f)

# Load game function
def load_game(game):
    try:
        with open(SAVE_FILE, 'r') as f:
            save_data = json.load(f)
            
            game.day = save_data['day']
            game.time = save_data['time']
            game.money = save_data['money']
            game.happiness = save_data['happiness']
            game.inventory = save_data['inventory']
            game.ingredients = save_data['ingredients']
            game.active_effects = save_data['active_effects']
            game.xp = save_data['xp']
            game.level = save_data['level']
            game.career_path = save_data['career_path']
            game.visited_locations = save_data['visited_locations']
            game.discount = save_data['discount']
            game.player_name = save_data['player_name']
            
            return True
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        return False

# Update leaderboard
def update_leaderboard(game):
    leaderboard = []
    
    # Load existing leaderboard
    try:
        with open(LEADERBOARD_FILE, 'r') as f:
            leaderboard = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        leaderboard = []
    
    # Calculate score based on game metrics
    score = (game.money + game.happiness * 2 + game.xp * 3 + game.level * 100)
    
    # Add new entry
    leaderboard.append({
        'name': game.player_name,
        'score': score,
        'level': game.level,
        'money': game.money,
        'happiness': game.happiness,
        'career_path': game.career_path,
        'date': time.strftime("%Y-%m-%d %H:%M")
    })
    
    # Sort by score (highest first)
    leaderboard.sort(key=lambda x: x['score'], reverse=True)
    
    # Keep only top 10
    leaderboard = leaderboard[:10]
    
    # Save leaderboard
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(leaderboard, f)
    
    return leaderboard

# Display leaderboard
def show_leaderboard(stdscr):
    try:
        with open(LEADERBOARD_FILE, 'r') as f:
            leaderboard = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        leaderboard = []
    
    stdscr.clear()
    stdscr.addstr(1, 5, "=== LUNCH QUEST LEADERBOARD ===")
    
    if not leaderboard:
        stdscr.addstr(3, 5, "No scores yet. Be the first!")
    else:
        stdscr.addstr(3, 2, "RANK  NAME             SCORE    LEVEL  CAREER PATH")
        stdscr.addstr(4, 2, "-" * 60)
        
        for i, entry in enumerate(leaderboard[:10]):
            rank_str = f"{i+1:2d}."
            name_str = entry['name'][:15].ljust(15)
            score_str = f"{entry['score']:7d}"
            level_str = f"{entry['level']:5d}"
            path_str = entry['career_path'][:15] if entry['career_path'] else "None"
            
            stdscr.addstr(5+i, 2, f"{rank_str}  {name_str}  {score_str}  {level_str}  {path_str}")
    
    stdscr.addstr(16, 5, "Press Enter to continue...")
    stdscr.refresh()
    stdscr.getch()  # Wait for user input

class Game:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.reset_game()
        self.player_name = "Simon"
    
    def reset_game(self):
        """Reset the game to initial state"""
        self.day = 0
        self.time = 9
        self.money = START_MONEY
        self.happiness = 50
        self.menu = {}
        self.inventory = []  # For completed items and power-ups
        self.ingredients = []  # For raw ingredients
        self.active_effects = {}  # For tracking active power-ups
        self.xp = 0
        self.level = 1
        self.discount = 0
        self.career_path = None
        self.visited_locations = []
        self.current_location = "Secret Garden Cafe"
        self.multiplayer_scores = {}
    
    def draw_header(self):
        """Draw the game header with stats"""
        header = f"Day {self.day+1}/{TOTAL_DAYS} | Time {self.time:02d}:00 | $ {self.money} | 😊 {self.happiness}/100 | XP {self.xp}/{LEVEL_UP_XP*self.level} | Lvl {self.level}"
        self.stdscr.addstr(0, 2, header)
        self.stdscr.hline(1, 0, '-', len(header)+4)
        
        # Show career path if selected
        if self.career_path:
            self.stdscr.addstr(0, len(header) + 5, f"Career: {self.career_path}")
            
        # Display active effects
        if self.active_effects:
            effects_str = " | ".join([f"{effect}({duration}d)" for effect, duration in self.active_effects.items()])
            self.stdscr.addstr(2, 2, f"Active Effects: {effects_str}")
    
    def get_input(self, prompt, y, x, max_len=20, numeric_only=False):
        """Get user input with proper handling"""
        # Get terminal dimensions
        max_y, max_x = self.stdscr.getmaxyx()

        # Ensure y and x are within bounds
        if y >= max_y:
            y = max_y - 1
        if x + len(prompt) >= max_x:
            x = max_x - len(prompt) - 1

        self.stdscr.addstr(y, x, prompt)
        input_x = x + len(prompt)
        self.stdscr.move(y, input_x)
        self.stdscr.refresh()

        user_input = ""
        while True:
            ch = self.stdscr.getch()

            # Handle backspace
            if ch in (8, 127, curses.KEY_BACKSPACE):
                if user_input:
                    user_input = user_input[:-1]
                    self.stdscr.addstr(y, input_x, " " * max_len)
                    self.stdscr.addstr(y, input_x, user_input)
            # Handle enter key
            elif ch in (curses.KEY_ENTER, 10, 13):
                break
            # Handle digit keys for numeric input
            elif numeric_only and ch >= 48 and ch <= 57 and len(user_input) < max_len:
                user_input += chr(ch)
                self.stdscr.addstr(y, input_x, user_input)
            # Handle all printable characters for text input
            elif not numeric_only and ch >= 32 and ch <= 126 and len(user_input) < max_len:
                user_input += chr(ch)
                self.stdscr.addstr(y, input_x, user_input)

            self.stdscr.refresh()

        return user_input
        
    def wait_for_key(self, message=None, y=None, x=None):
        """Wait for the user to press a key"""
        if message:
            if y is None or x is None:
                max_y, max_x = self.stdscr.getmaxyx()
                y = max_y - 2
                x = 5
            self.stdscr.addstr(y, x, message)
        self.stdscr.refresh()
        while True:
            key = self.stdscr.getch()
            if key != -1:  # Ensure a key was pressed
                break
    
    def display_menu(self, options, title="Menu", start_y=3):
        """Display a menu and get user choice"""
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(start_y, 5, title)
        
        for i, (option, _) in enumerate(options):
            self.stdscr.addstr(start_y + i + 2, 5, f"{i+1}. {option}")
        
        self.stdscr.addstr(start_y + len(options) + 3, 5, f"Choose option (1-{len(options)}): ")
        self.stdscr.refresh()
        
        while True:
            choice = self.get_input("", start_y + len(options) + 3, 5 + len(f"Choose option (1-{len(options)}): "), 2, True)
            
            if choice and 1 <= int(choice) <= len(options):
                return options[int(choice) - 1][1]
    
    def main_menu(self):
        """Display the main menu"""
        while True:
            options = [
                ("New Game", "new"),
                ("Load Game", "load"),
                ("Multiplayer Mode", "multiplayer"),
                ("View Leaderboard", "leaderboard"),
                ("Exit", "exit")
            ]
            
            choice = self.display_menu(options, "=== LUNCH QUEST ===")
            
            if choice == "new":
                self.reset_game()
                self.setup_new_game()
                return True
            elif choice == "load":
                if load_game(self):
                    self.stdscr.clear()
                    self.draw_header()
                    self.stdscr.addstr(3, 5, "Game loaded successfully!")
                    self.wait_for_key("Press any key to continue...", 5, 5)
                    return True
                else:
                    self.stdscr.clear()
                    self.draw_header()
                    self.stdscr.addstr(3, 5, "No save file found or corrupted save.")
                    self.wait_for_key("Press any key to continue...", 5, 5)
            elif choice == "multiplayer":
                self.multiplayer_setup()
                return True
            elif choice == "leaderboard":
                show_leaderboard(self.stdscr)
            elif choice == "exit":
                return False
    
    def setup_new_game(self):
        """Setup a new game with player name"""
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, "Welcome to Lunch Quest!")
        
        name = self.get_input("Enter your name: ", 5, 5, 15)
        if name:
            self.player_name = name
        
        self.stdscr.addstr(7, 5, f"Hello, {self.player_name}! You are an Electrical Engineering lecturer.")
        self.stdscr.addstr(8, 5, f"Navigate your busy schedule, enjoy lunches, and solve engineering puzzles.")
        
        self.wait_for_key("Press any key to start your adventure...", 10, 5)
    
    def multiplayer_setup(self):
        """Setup multiplayer mode"""
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, "=== MULTIPLAYER MODE ===")
        self.stdscr.addstr(5, 5, "How many players? (1-4): ")
        
        while True:
            num_players = self.get_input("", 5, 29, 1, True)
            try:
                num_players = int(num_players)
                if 1 <= num_players <= 4:
                    break
                else:
                    self.stdscr.addstr(6, 5, "Please enter a number between 1 and 4")
            except ValueError:
                self.stdscr.addstr(6, 5, "Please enter a valid number")
        
        self.multiplayer_players = []
        for i in range(num_players):
            self.stdscr.clear()
            self.draw_header()
            self.stdscr.addstr(3, 5, f"Player {i+1} Name: ")
            name = self.get_input("", 3, 20, 15)
            if not name:
                name = f"Player {i+1}"
            self.multiplayer_players.append(name)
            self.multiplayer_scores[name] = 0
        
        self.multiplayer_mode = True
        self.reset_game()
    
    def teach_class(self, session):
        """Simulate teaching a class session"""
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, f"Teaching Session {session} - EE 101: Camera Circuits")
        self.stdscr.addstr(5, 5, "You explain designs and field student questions...")
        
        # Apply career path modifiers if applicable
        xp_gain = 10
        happiness_gain = 5
        
        if self.career_path:
            xp_gain *= CAREER_PATHS[self.career_path]['xp_modifier']
            happiness_gain *= CAREER_PATHS[self.career_path]['happiness_modifier']
        
        # Apply active effects
        if "Brain Booster" in self.active_effects:
            xp_gain *= 2
            
        if "Happiness Amplifier" in self.active_effects:
            happiness_gain *= 2
        
        self.xp += int(xp_gain)
        self.happiness = min(100, self.happiness + int(happiness_gain))
        
        # Show gains
        self.stdscr.addstr(7, 5, f"+{int(xp_gain)} XP, +{int(happiness_gain)} happiness")
        
        self.wait_for_key("Press any key to continue...", 9, 5)
        
        # Apply time effects
        time_spent = CLASS_DURATION
        if "Energy Circuit" in self.active_effects:
            time_spent = max(1, time_spent - 1)
            
        self.time += time_spent
    
    def choose_location(self):
        """Allow the player to choose a lunch location"""
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, "Where would you like to go for lunch?")
        
        # Generate options
        options = []
        y = 5
        for i, (name, details) in enumerate(LOCATIONS.items(), 1):
            status = " (visited)" if name in self.visited_locations else ""
            options.append((f"{name}{status}", name))
            self.stdscr.addstr(y, 5, f"{i}. {name}{status}")
            self.stdscr.addstr(y+1, 8, f"- {details['description']}")
            self.stdscr.addstr(y+2, 8, f"- Specialty: {details['specialty']}")
            y += 4
        
        choice = self.get_input("Enter your choice (1-4): ", y, 5, 1, True)
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(LOCATIONS):
                selected = list(LOCATIONS.keys())[idx]
                self.current_location = selected
                if selected not in self.visited_locations:
                    self.visited_locations.append(selected)
                    self.xp += 5  # Bonus XP for visiting a new location
                return selected
            else:
                # Default to Secret Garden Cafe if invalid choice
                return "Secret Garden Cafe"
        except (ValueError, IndexError):
            return "Secret Garden Cafe"
    
    def lunch_break(self):
        """Visit cafe and order lunch"""
        # First choose location
        location = self.choose_location()
        
        # Generate menu for the location
        self.menu = generate_menu(location)
        
        # Travel to location
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, f"Travel to {location}...")
        xp_bonus = LOCATIONS[location]['xp_bonus']
        if xp_bonus > 0:
            self.stdscr.addstr(4, 5, f"(+{xp_bonus} XP for visiting this location)")
            self.xp += xp_bonus
            
        self.wait_for_key("Press any key to continue...", 6, 5)
        
        # Apply time effects for travel
        travel_time = TRAVEL_TIME
        if "Energy Circuit" in self.active_effects:
            travel_time = max(0, travel_time - 1)
        self.time += travel_time
        
        # Display menu and get order
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, f"{location} - Menu:")
        y = 5
        for num, (item, price) in self.menu.items():
            discounted = max(price - self.discount, 0)
            discount_text = f" (${price} - ${self.discount} discount)" if self.discount else ""
            self.stdscr.addstr(y, 5, f"{num}. {item} - ${discounted}{discount_text}")
            y += 1
        
        choice = self.get_input("Choose lunch (number): ", y + 2, 5, 1, True)
        
        try:
            num = int(choice)
            item, cost = self.menu[num]
            cost = max(cost - self.discount, 0)
            
            if cost > self.money:
                self.stdscr.addstr(y + 4, 5, f"You can't afford the {item}! -10 happiness.")
                self.happiness = max(0, self.happiness - 10)
            else:
                # Apply career path money modifier if applicable
                if self.career_path:
                    refund = int(cost * (1 - CAREER_PATHS[self.career_path]['money_modifier']))
                    if refund > 0:
                        self.stdscr.addstr(y + 4, 5, f"Your {self.career_path} path refunds ${refund}!")
                        cost -= refund
                
                self.money -= cost
                
                # Calculate happiness gain
                happiness_gain = 10
                if self.career_path:
                    happiness_gain *= CAREER_PATHS[self.career_path]['happiness_modifier']
                if "Happiness Amplifier" in self.active_effects:
                    happiness_gain *= 2
                
                self.happiness = min(100, self.happiness + int(happiness_gain))
                
                # Get a random ingredient
                ingredient = random.choice(INGREDIENTS)
                self.ingredients.append(ingredient)
                
                self.stdscr.addstr(y + 4, 5, f"Ate {item}! +{int(happiness_gain)} happiness.")
                self.stdscr.addstr(y + 5, 5, f"Found ingredient: {ingredient}")
        except (ValueError, KeyError):
            self.stdscr.addstr(y + 4, 5, "Invalid choice! -5 happiness.")
            self.happiness = max(0, self.happiness - 5)
        
        self.wait_for_key("Press any key to continue...", y + 7, 5)
        
        # Apply time effects for lunch
        lunch_time = 1
        if "Energy Circuit" in self.active_effects:
            lunch_time = max(0, lunch_time - 1)
        self.time += lunch_time
        
        # Reset discount after use
        self.discount = 0
    
    def inventory_menu(self):
        """Display and manage inventory"""
        while True:
            self.stdscr.clear()
            self.draw_header()
            self.stdscr.addstr(3, 5, "=== INVENTORY ===")
            
            # Display ingredients
            self.stdscr.addstr(5, 5, "Ingredients:")
            if not self.ingredients:
                self.stdscr.addstr(6, 7, "No ingredients collected yet.")
            else:
                ingredient_counts = defaultdict(int)
                for ingredient in self.ingredients:
                    ingredient_counts[ingredient] += 1
                
                y = 6
                for ingredient, count in ingredient_counts.items():
                    self.stdscr.addstr(y, 7, f"{ingredient} x{count}")
                    y += 1
            
            # Display active items/power-ups
            self.stdscr.addstr(15, 5, "Active Effects:")
            if not self.active_effects:
                self.stdscr.addstr(16, 7, "No active effects.")
            else:
                y = 16
                for effect, duration in self.active_effects.items():
                    self.stdscr.addstr(y, 7, f"{effect} ({duration} days remaining)")
                    y += 1
            
            # Options
            options = [
                ("Craft a recipe", "craft"),
                ("Return to game", "return")
            ]
            
            y = 20
            for i, (option, _) in enumerate(options, 1):
                self.stdscr.addstr(y + i, 5, f"{i}. {option}")
            
            choice = self.get_input("Choose option: ", y + len(options) + 2, 5, 1, True)
            
            try:
                if int(choice) == 1:
                    self.craft_recipe()
                else:
                    break
            except ValueError:
                break
    
    def craft_recipe(self):
        """Interface for crafting recipes from ingredients"""
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, "=== CRAFTING ===")

        # Display available recipes
        self.stdscr.addstr(5, 5, "Available Recipes:")

        options = []
        y = 7
        for i, (name, details) in enumerate(RECIPES.items(), 1):
            self.stdscr.addstr(y, 5, f"{i}. {name}")
            self.stdscr.addstr(y + 1, 8, f"Effect: {details['effect']}")
            self.stdscr.addstr(y + 2, 8, f"Ingredients: {', '.join(details['ingredients'])}")
            options.append((name, name))
            y += 4

        options.append(("Return", "return"))
        self.stdscr.addstr(y, 5, f"{len(options)}. Return")

        choice = self.get_input("Choose recipe to craft: ", y + 2, 5, 1, True)

        try:
            idx = int(choice) - 1
            if idx == len(options) - 1:
                return

            recipe_name = options[idx][1]
            recipe = RECIPES[recipe_name]

            # Check if player has the ingredients
            has_ingredients = True
            inventory_copy = self.ingredients.copy()

            for ingredient in recipe['ingredients']:
                if inventory_copy.count(ingredient) < recipe['ingredients'].count(ingredient):
                    has_ingredients = False
                    break

            if has_ingredients:
                # Remove ingredients from inventory
                for ingredient in recipe['ingredients']:
                    self.ingredients.remove(ingredient)

                # Add the effect
                self.active_effects[recipe_name] = recipe['duration']

                self.stdscr.addstr(y + 4, 5, f"Successfully crafted {recipe_name}!")
                self.stdscr.addstr(y + 5, 5, f"Effect: {recipe['effect']} for {recipe['duration']} days")
            else:
                self.stdscr.addstr(y + 4, 5, "You don't have all the required ingredients!")

            # Ensure the message fits within the terminal
            max_y, _ = self.stdscr.getmaxyx()
            message_y = min(y + 7, max_y - 1)
            self.wait_for_key("Press any key to continue...", message_y, 5)
        except (ValueError, IndexError, KeyError):
            self.stdscr.addstr(y + 4, 5, "Invalid choice!")
            max_y, _ = self.stdscr.getmaxyx()
            message_y = min(y + 6, max_y - 1)
            self.wait_for_key("Press any key to continue...", message_y, 5)


    def career_choice(self):
        """Allow the player to choose a career path."""
        self.stdscr.clear()
        self.draw_header()

        # Get terminal dimensions
        max_y, max_x = self.stdscr.getmaxyx()

        # Ensure the content fits within the terminal
        y = 5
        if y + len(CAREER_PATHS) + 3 >= max_y:  # Check if there's enough vertical space
            y = max_y - (len(CAREER_PATHS) + 4)
        if y < 0:
            y = 0

        self.stdscr.addstr(y, 5, "Choose your career path:")
        for i, (path, details) in enumerate(CAREER_PATHS.items()):
            if y + i + 1 >= max_y:  # Prevent writing outside the terminal
                break
            self.stdscr.addstr(y + i + 1, 7, f"{i + 1}. {path} - {details['description']}")

        self.stdscr.addstr(y + len(CAREER_PATHS) + 1, 5, "Enter your choice (1-4):")
        self.stdscr.refresh()

        # Get user input
        choice = self.get_input("", y + len(CAREER_PATHS) + 2, 5, 1, numeric_only=True)
        try:
            choice = int(choice)
            if 1 <= choice <= len(CAREER_PATHS):
                selected = list(CAREER_PATHS.keys())[choice - 1]
                self.career_path = selected
                # Ensure the message fits within the terminal
                message_y = y + len(CAREER_PATHS) + 3
                if message_y >= max_y:
                    message_y = max_y - 1
                self.stdscr.addstr(message_y, 5, f"You have chosen the {selected} path!")
            else:
                self.stdscr.addstr(y + len(CAREER_PATHS) + 3, 5, "Invalid choice. No career path selected.")
        except ValueError:
            self.stdscr.addstr(y + len(CAREER_PATHS) + 3, 5, "Invalid input. No career path selected.")

        self.stdscr.refresh()
        time.sleep(2)
            
    def play_random_puzzle(self):
        """Play a random puzzle from the available types"""
        puzzle_types = [
            ("FPGA Logic Design Puzzle", fpga_logic_puzzle),
            ("FPGA Resource Utilization Puzzle", fpga_resource_puzzle),
            ("Logic Gate Puzzle", circuit_puzzle)
        ]
        
        # Select a puzzle based on player level
        available_puzzles = puzzle_types[:min(self.level, len(puzzle_types))]
        puzzle_name, puzzle_func = random.choice(available_puzzles)
        
        # Inform player about the puzzle
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, f"Time for a {puzzle_name}!")
        self.wait_for_key("Press any key to start the puzzle...", 5, 5)
        
        # Puzzle difficulty increases with level
        time_mod = max(0.5, 1.0 - (self.level * 0.1))  # Reduce time by 10% per level
        global PUZZLE_TIME_LIMIT
        original_time = PUZZLE_TIME_LIMIT
        PUZZLE_TIME_LIMIT = int(original_time * time_mod)
        
        # Run the puzzle
        focus_boost = "Focus Field Generator" in self.active_effects
        if focus_boost:
            # With focus boost, give a 50% chance of automatic success
            if random.random() < 0.5:
                solved = True
                self.stdscr.clear()
                self.draw_header()
                self.stdscr.addstr(3, 5, "Your Focus Field Generator helped you solve the puzzle instantly!")
                self.wait_for_key("Press any key to continue...", 5, 5)
            else:
                solved = puzzle_func(self.stdscr)
        else:
            solved = puzzle_func(self.stdscr)
        
        # Reset the time limit
        PUZZLE_TIME_LIMIT = original_time
        
        # Calculate rewards based on result
        xp_gain = 20 if solved else 5
        happiness_change = 10 if solved else -5
        
        # Apply career modifiers
        if self.career_path:
            xp_gain *= CAREER_PATHS[self.career_path]['xp_modifier']
            happiness_change *= CAREER_PATHS[self.career_path]['happiness_modifier']
        
        # Apply active effects
        if "Brain Booster" in self.active_effects:
            xp_gain *= 2
        if "Happiness Amplifier" in self.active_effects and happiness_change > 0:
            happiness_change *= 2
        
        # Update stats
        self.xp += int(xp_gain)
        self.happiness = max(0, min(100, self.happiness + int(happiness_change)))
        
        # Show results
        self.stdscr.clear()
        self.draw_header()
        result = "Solved" if solved else "Failed"
        self.stdscr.addstr(3, 5, f"Puzzle {result}!")
        self.stdscr.addstr(5, 5, f"+{int(xp_gain)} XP")
        
        if happiness_change >= 0:
            self.stdscr.addstr(6, 5, f"+{int(happiness_change)} Happiness")
        else:
            self.stdscr.addstr(6, 5, f"{int(happiness_change)} Happiness")
        
        if solved and random.random() < 0.3:  # 30% chance to get bonus ingredient on success
            ingredient = random.choice(INGREDIENTS)
            self.ingredients.append(ingredient)
            self.stdscr.addstr(7, 5, f"You found a bonus ingredient: {ingredient}")
        
        self.wait_for_key("Press any key to continue...", 9, 5)
        
        return solved
    
    def update_effects(self):
        """Update all active effects at the end of the day"""
        expired = []
        for effect, duration in self.active_effects.items():
            self.active_effects[effect] = duration - 1
            if self.active_effects[effect] <= 0:
                expired.append(effect)
        
        for effect in expired:
            del self.active_effects[effect]
            
        if expired:
            self.stdscr.clear()
            self.draw_header()
            self.stdscr.addstr(3, 5, "Effects Expired:")
            for i, effect in enumerate(expired):
                self.stdscr.addstr(5 + i, 7, f"- {effect}")
            
            self.wait_for_key("Press any key to continue...", 5 + len(expired) + 2, 5)
    
    def check_level(self):
        """Check if player has leveled up"""
        if self.xp >= LEVEL_UP_XP * self.level:
            old_level = self.level
            while self.xp >= LEVEL_UP_XP * self.level:
                self.level += 1
            
            levels_gained = self.level - old_level
            bonus = 10 * self.level * levels_gained
            
            self.stdscr.clear()
            self.draw_header()
            if levels_gained == 1:
                self.stdscr.addstr(3, 5, f"Level Up! Now Level {self.level}")
            else:
                self.stdscr.addstr(3, 5, f"You gained {levels_gained} levels! Now Level {self.level}")
                
            self.stdscr.addstr(5, 5, f"+{bonus} happiness!")
            
            # Career choices are offered at levels 3, 6, and 9
            if old_level < 3 <= self.level and not self.career_path:
                self.stdscr.addstr(7, 5, "You've unlocked career choices!")
            
            self.happiness = min(100, self.happiness + bonus)
            self.wait_for_key("Press any key to continue...", 9, 5)
    
    def daily_actions(self):
        """Menu of possible daily actions"""
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, "What would you like to do?")
        
        options = [
            ("Check Inventory", "inventory"),
            ("Save Game", "save"),
            ("Continue Day", "continue")
        ]
        
        # Career choice becomes available at level 3
        if self.level >= 3 and not self.career_path:
            options.insert(0, ("Choose Career Path", "career"))
        
        y = 5
        for i, (option, _) in enumerate(options, 1):
            self.stdscr.addstr(y + i, 5, f"{i}. {option}")
        
        choice = self.get_input("Choose option: ", y + len(options) + 2, 5, 1, True)
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                action = options[idx][1]
                
                if action == "inventory":
                    self.inventory_menu()
                elif action == "career":
                    self.career_choice()
                elif action == "save":
                    save_game(self)
                    self.stdscr.clear()
                    self.draw_header()
                    self.stdscr.addstr(3, 5, "Game saved successfully!")
                    self.wait_for_key("Press any key to continue...", 5, 5)
                # continue just returns to continue the day
        except ValueError:
            pass  # Invalid input, just continue
    
    def play_day(self):
        """Play through one day in the game"""
        # Reset time and create a new menu
        self.time = 9
        
        # Show day start
        self.stdscr.clear()
        self.draw_header()
        weekday = self.day % DAYS_PER_WEEK
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.stdscr.addstr(3, 5, f"Day {self.day+1}: {weekday_names[weekday]}")
        
        # Check for random events
        dynamic_event(self.stdscr, self)
        
        # Daily actions menu (inventory, save, etc.)
        self.daily_actions()
        
        # Different schedule for work days vs weekends
        if weekday in WORK_DAYS:  # Tuesday & Thursday
            # Morning class
            self.teach_class(1)
            
            # Travel & lunch
            self.lunch_break()
            
            # Puzzle time
            self.play_random_puzzle()
            
            # Afternoon class
            self.teach_class(2)
        else:
            # Weekend or rest day
            self.stdscr.clear()
            self.draw_header()
            
            rest_activities = [
                "PCB prototyping in your home lab",
                "Walking in the park while listening to engineering podcasts",
                "Binge-watching a circuit design documentary series",
                "Attending a virtual engineering conference",
                "Working on a side project for a local robotics competition",
                "Meeting with colleagues to discuss research",
                "Writing a chapter for your upcoming textbook"
            ]
            
            activity = random.choice(rest_activities)
            self.stdscr.addstr(3, 5, f"Rest day: {activity}")
            
            # Base rewards
            money_gain = 5
            happiness_gain = 8
            xp_gain = 5
            
            # Career modifiers
            if self.career_path:
                money_gain *= CAREER_PATHS[self.career_path]['money_modifier']
                happiness_gain *= CAREER_PATHS[self.career_path]['happiness_modifier']
                xp_gain *= CAREER_PATHS[self.career_path]['xp_modifier']
            
            # Apply effects
            if "Brain Booster" in self.active_effects:
                xp_gain *= 2
            if "Happiness Amplifier" in self.active_effects:
                happiness_gain *= 2
            
            self.money += int(money_gain)
            self.happiness = min(100, self.happiness + int(happiness_gain))
            self.xp += int(xp_gain)
            
            self.stdscr.addstr(5, 5, f"+${int(money_gain)}, +{int(happiness_gain)} happiness, +{int(xp_gain)} XP")
            
            # 50% chance for a random ingredient on rest days
            if random.random() < 0.5:
                ingredient = random.choice(INGREDIENTS)
                self.ingredients.append(ingredient)
                self.stdscr.addstr(7, 5, f"You found an ingredient: {ingredient}")
            
            self.time += 4  # Rest day activities take time too
            
            self.wait_for_key("Press any key to continue...", 9, 5)
        
        # End of day updates
        self.update_effects()
        self.check_level()
        self.day += 1
        self.happiness = max(0, min(self.happiness, 100))
    
    def multiplayer_turn(self, player_name):
        """Handle one player's turn in multiplayer mode"""
        self.stdscr.clear()
        original_values = {
            'money': self.money,
            'happiness': self.happiness,
            'xp': self.xp
        }
        
        self.stdscr.addstr(1, 5, f"=== {player_name}'s Turn ===")
        self.stdscr.addstr(3, 5, f"Starting: ${self.money}, {self.happiness} happiness, {self.xp} XP")
        self.wait_for_key("Press any key to take your turn...", 5, 5)
        
        # Play the day for this player
        self.play_day()
        
        # Calculate score change
        score_change = (self.money - original_values['money']) + \
                      (self.happiness - original_values['happiness']) * 2 + \
                      (self.xp - original_values['xp']) * 3
        
        self.multiplayer_scores[player_name] += score_change
        
        self.stdscr.clear()
        self.stdscr.addstr(1, 5, f"=== {player_name}'s Turn Complete ===")
        self.stdscr.addstr(3, 5, f"Starting: ${original_values['money']}, {original_values['happiness']} happiness, {original_values['xp']} XP")
        self.stdscr.addstr(4, 5, f"Ending: ${self.money}, {self.happiness} happiness, {self.xp} XP")
        self.stdscr.addstr(6, 5, f"Points earned this turn: {score_change}")
        self.stdscr.addstr(7, 5, f"Total score: {self.multiplayer_scores[player_name]}")
        
        self.wait_for_key("Press Enter to end your turn...", 9, 5)
    
    def play_multiplayer(self):
        """Play the game in multiplayer mode"""
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, "=== MULTIPLAYER MODE ===")
        self.stdscr.addstr(5, 5, f"Playing {len(self.multiplayer_players)} player game")
        self.stdscr.addstr(6, 5, f"First to reach 500 points wins!")
        self.wait_for_key("Press any key to start...", 8, 5)
        
        round_num = 1
        winner = None
        
        while self.day < TOTAL_DAYS and not winner:
            self.stdscr.clear()
            self.draw_header()
            self.stdscr.addstr(3, 5, f"=== ROUND {round_num} ===")
            
            # Show current scores
            y = 5
            self.stdscr.addstr(y, 5, "Current Scores:")
            for i, player in enumerate(self.multiplayer_players):
                score = self.multiplayer_scores[player]
                self.stdscr.addstr(y + i + 1, 5, f"{player}: {score} points")
            
            self.wait_for_key("Press any key to continue...", y + len(self.multiplayer_players) + 2, 5)
            
            # Each player takes a turn
            for player in self.multiplayer_players:
                self.multiplayer_turn(player)
                
                # Check if anyone has won
                if self.multiplayer_scores[player] >= 500:
                    winner = player
                    break
            
            round_num += 1
        
        # Game over - show final scores
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, "=== GAME OVER ===")
        
        if winner:
            self.stdscr.addstr(5, 5, f"{winner} wins with {self.multiplayer_scores[winner]} points!")
        else:
            # Find the winner based on highest score
            max_score = -1
            for player, score in self.multiplayer_scores.items():
                if score > max_score:
                    max_score = score
                    winner = player
            
            self.stdscr.addstr(5, 5, f"Game complete! {winner} wins with {max_score} points!")
        
        # Show all final scores
        y = 7
        self.stdscr.addstr(y, 5, "Final Scores:")
        sorted_scores = sorted(self.multiplayer_scores.items(), key=lambda x: x[1], reverse=True)
        for i, (player, score) in enumerate(sorted_scores):
            self.stdscr.addstr(y + i + 1, 5, f"{i+1}. {player}: {score} points")
        
        self.wait_for_key("Press any key to return to main menu...", y + len(sorted_scores) + 2, 5)
        
    def summary(self):
        """Display game summary at the end"""
        self.stdscr.clear()
        self.draw_header()
        self.stdscr.addstr(3, 5, "-- Game Over --")
        
        self.stdscr.addstr(5, 5, f"Days: {self.day}")
        self.stdscr.addstr(6, 5, f"Money: ${self.money}")
        self.stdscr.addstr(7, 5, f"Happiness: {self.happiness}/100")
        self.stdscr.addstr(8, 5, f"Level: {self.level}  XP: {self.xp}")
        
        # Career path
        if self.career_path:
            self.stdscr.addstr(9, 5, f"Career Path: {self.career_path}")
            self.stdscr.addstr(10, 5, f"- {CAREER_PATHS[self.career_path]['description']}")
        
        # Locations visited
        self.stdscr.addstr(12, 5, f"Locations Visited: {len(self.visited_locations)}/{len(LOCATIONS)}")
        for i, loc in enumerate(self.visited_locations):
            self.stdscr.addstr(13 + i, 7, f"- {loc}")
        
        # Calculate score
        score = (self.money + self.happiness * 2 + self.xp * 3 + self.level * 100)
        self.stdscr.addstr(13 + len(self.visited_locations) + 1, 5, f"Final Score: {score}")
        
        # Update leaderboard
        update_leaderboard(self)
        
        self.stdscr.addstr(13 + len(self.visited_locations) + 3, 5, "Thanks for playing Lunch Quest!")
        self.wait_for_key("Press any key to return to the main menu...", 13 + len(self.visited_locations) + 5, 5)


def main(stdscr):
    # Setup
    curses.curs_set(1)  # Show cursor
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)

    # Initialize game
    game = Game(stdscr)

    # Main menu loop
    while True:
        if not game.main_menu():
            break

        # Game loop
        while game.day < TOTAL_DAYS:
            try:
                game.play_day()
            except KeyboardInterrupt:
                # Handle Ctrl+C: Save the game and return to the main menu
                save_game(game)
                stdscr.clear()
                stdscr.addstr(3, 5, "Game saved! Returning to the main menu...")
                stdscr.refresh()
                time.sleep(2)
                break

        # End of game summary
        game.summary()

        # Ask if the player wants to play again
        while True:
            stdscr.clear()
            stdscr.addstr(3, 5, "Would you like to play again? (y/n): ")
            stdscr.refresh()
            key = stdscr.getch()
            if key in (ord('y'), ord('Y')):
                break
            elif key in (ord('n'), ord('N')):
                return  # Exit the game loop

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        print("\nGame interrupted. Goodbye!")
        sys.exit(0)
