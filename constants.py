SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCALE = 1

PLAYER_RADIUS = 20
PLAYER_TURN_SPEED = 300
PLAYER_SPEED = 300
PLAYER_HEALTH = 3
PLAYER_SHIELD = 0
SHIELD_DURATION = 5000  # milliseconds

PLAYER_SHOOT_SPEED = 500
PLAYER_SHOOT_COOLDOWN = 1
PLAYER_SHOT_NO = 1
PLAYER_SHOT_PIERCE = 0

# Difficulty settings
DIFFICULTY_SPAWN_MULTIPLIERS = {
    0: 1.0,  # Easy
    1: 1.75,  # Medium - between easy and nightmare
    2: 2.5,  # Nightmare
}

DIFFICULTY_SPEED_MULTIPLIERS = {
    0: 1.0,  # Easy
    1: 1.5,  # Medium - between 1.0 and 1.8
    2: 1.8,  # Nightmare
}

DIFFICULTY_SIZE_MULTIPLIERS = {
    0: 1.0,  # Easy
    1: 1.35,  # Medium - between 1.0 and 1.5
    2: 1.5,  # Nightmare
}

# Asteroid types/tiers
ASTEROID_TIER_COLORS = {
    1: (200, 200, 200),  # White - tier 1 (1x health)
    2: (255, 200, 100),  # Orange - tier 2 (2x health)
    3: (255, 100, 100),  # Red - tier 3 (3x health)
}

ASTEROID_TIER_HEALTH_MULTIPLIERS = {1: 1, 2: 2, 3: 3}

# Magnetizer resistance multipliers (higher tier = more resistant)
ASTEROID_TIER_MAGNETIZER_RESISTANCE = {
    1: 1.0,  # Normal asteroids: full effect
    2: 0.5,  # Medium asteroids: half effect
    3: 0.25,  # High level asteroids: quarter effect
}

ASTEROID_MIN_RADIUS = 20
ASTEROID_KINDS = 3
ASTEROID_SPAWN_RATE = 1  # seconds
ASTEROID_MAX_RADIUS = ASTEROID_MIN_RADIUS * ASTEROID_KINDS

# Weapons
WEAPONS = ["Rotator", "EMP", "Laser", "Wingmen", "Magnetizer"]
UPGRADES = [
    "Multi Shot",
    "Shield",
    "Bigger Bullets",
    "Extra Life",
    "Piercing Bullets",
    "Rapid Fire",
]

# Special upgrades (one-time)
SPECIAL_UPGRADES = ["Wingman Formations", "Basic Fighter Maneuvers"]

# Formation types
WINGMEN_FORMATIONS = ["Scouting", "Close Follow", "Radar Follow"]

# Final upgrades - unlocked when base weapon reaches level 3
FINAL_UPGRADES = {
    "Laser": "Shockwave",
    # Add more here: "Rotator": "Rotator Pro", etc.
}

# Conditions for final upgrades (can be extended)
FINAL_UPGRADE_CONDITIONS = {
    "Laser": {"level": 3, "type": "weapon_level"},
}

# Wingmen Weapon constants - renamed from Minions
WINGMEN_COUNT = 2
WINGMEN_SPEED = 100  # Half of base shot speed (200)
WINGMEN_FIRE_COOLDOWN = 1.0  # seconds
WINGMEN_MAX_RANGE = 200
WINGMEN_SHOT_SPEED = 150
WINGMEN_RADIUS = 50

# Wingmen formation types
WINGMEN_FORMATION_SCOUTING = 0
WINGMEN_FORMATION_CLOSE_FOLLOW = 1
WINGMEN_FORMATION_RADAR_FOLLOW = 2
EMP_RANGE = 100  # From EMP_RADIUS constant for reference

MAGNETIZER_BASE_PUSH_AMOUNT = 20  # Base amount at level 1 (increased from 15)
MAGNETIZER_PUSH_RANGE = 75  # Half of what it was (150 -> 75)
MAGNETIZER_MAX_ASTEROID_SIZE = 80

# Weapon specific:
ROTATOR_SPEED = 300
ROTATOR_RADIUS = 30

EMP_RADIUS = 100

LASER_WIDTH = 10
LASER_SPEED_MULT = 30

SHOT_RADIUS = 7
SHOT_SPEED = 400

