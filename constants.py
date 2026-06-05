SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCALE = 1
ZOOM_SCALE = 1.0  # Current zoom level (1.0 = no zoom, < 1.0 = zoom out)

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

ASTEROID_TIER_HEALTH_MULTIPLIERS = {1: 1, 2: 2, 3: 4}

# Magnetizer resistance multipliers (higher tier = more resistant)
ASTEROID_TIER_MAGNETIZER_RESISTANCE = {
    1: 1.0,
    2: 0.5,
    3: 0.25,
}

ASTEROID_MIN_RADIUS = 15
ASTEROID_KINDS = 5
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
    # Wingman-specific upgrades
    "Wingman Speed",
    "Wingman Fire Rate",
    "Wingman Intelligence",
    # Shield upgrades
    "Shield Regeneration",
    "Shield Regen Cooldown",
]

# Special upgrades (one-time)
SPECIAL_UPGRADES = ["Wingman Formations", "Basic Fighter Maneuvers"]

# Formation types
WINGMEN_FORMATIONS = ["Scouting", "Close Follow", "Radar Follow"]

# ============================================
# SHIELD CONSTANTS
# ============================================
SHIELD_PERMANENT_UNLOCK_LEVEL = 3  # Need 3 shields to unlock permanent shield
SHIELD_REGEN_COOLDOWN = 10.0  # Seconds for permanent shield to regenerate
SHIELD_REGEN_UPGRADE_DECREMENT = 1.0  # Cooldown reduction per upgrade level
SHIELD_REGEN_MIN_COOLDOWN = 7.0

# ============================================
# UPGRADE UNLOCK SYSTEM
# ============================================
# Each upgrade can have:
# - per_round_unlock: Requirements that must be met to unlock this upgrade in the current round
# - TODO: general_unlock: Score threshold to unlock permanently
#
# - locks: Other upgrades that should be locked if this one is selected
# - unlocks: Other upgrades that should be unlocked when this one is selected
# - final_upgrade: If this upgrade is a final upgrade, what it replaces
# - requires: Requirements to show this upgrade as an option
#
# Conditions format:
# - weapon_level: {"weapon": "Laser", "level": 3} - requires Laser at level 3
# - upgrade_owned: {"upgrade": "Laser"} - requires Laser upgrade to be owned
# - stat_value: {"stat": "shot_no", "value": 2, "comparison": ">="} - requires shot_no >= 2

# Final upgrades (unlocked when base weapon reaches level 3)
FINAL_UPGRADES = {
    "Laser": "Shockwave",
    # Add more here: "Rotator": "Rotator Pro", etc.
}


FINAL_UPGRADE_CONDITIONS = {
    "Laser": {"type": "weapon_level", "weapon": "Laser", "level": 3},
}

# Upgrade locking and unlocking rules
UPGRADE_RULES = {
    "Laser": {
        "unlocks_final": "Shockwave",  # Unlocks Shockwave at level 3
        "final_upgrade_level": 3,
        # Locking bullet-related upgrades when laser is selected
        "locks": ["Bigger Bullets", "Piercing Bullets", "Rapid Fire"],
    },
    "Shockwave": {
        "replaces": "Laser",
        "locks": ["Laser"],
        "requires": {"type": "weapon_level", "weapon": "Laser", "level": 3},
    },
    "Multi Shot": {
        "locks": [],
    },
    "Wingman Formations": {
        "requires": {"type": "weapon_level", "weapon": "Wingmen", "level": 1},
        "unlocks": ["Basic Fighter Maneuvers"],
    },
    "Basic Fighter Maneuvers": {
        "requires": {"type": "upgrade_owned", "upgrade": "Wingman Formations"},
    },
    "Shield": {
        "locks": [],
    },
    "Piercing Bullets": {
        "locks": [
            "Laser"
        ],  # Laser has its own piercing, but this is mostly for balancing
    },
    "Rapid Fire": {
        "locks": [],
    },
    "Bigger Bullets": {
        "locks": [],
    },
    "Extra Life": {
        "locks": [],
    },
    "EMP": {
        "locks": [],
    },
    "Rotator": {
        "locks": [],
    },
    "Wingmen": {
        "locks": [],
    },
    "Magnetizer": {
        "locks": [],
    },
    "Wingman Speed": {
        "requires": {"type": "weapon_level", "weapon": "Wingmen", "level": 1},
        "locks": [],
        "max_level": 5,
    },
    "Wingman Fire Rate": {
        "requires": {"type": "weapon_level", "weapon": "Wingmen", "level": 1},
        "locks": [],
        "max_level": 5,
    },
    "Wingman Intelligence": {
        "requires": {"type": "weapon_level", "weapon": "Wingmen", "level": 3},
        "locks": [],
        "one_time": True,
    },
    "Shield Regeneration": {
        "requires": {
            "type": "stat_value",
            "stat": "shield",
            "value": SHIELD_PERMANENT_UNLOCK_LEVEL,
            "comparison": ">=",
        },
        "locks": ["Shield"],
        "one_time": True,
    },
    "Shield Regen Cooldown": {
        "requires": {"type": "upgrade_owned", "upgrade": "Shield Regeneration"},
        "locks": [],
        "max_level": 3,
    },
}

# Wingmen Weapon constants - renamed from Minions
WINGMEN_COUNT = 2
WINGMEN_SPEED = 100  # Half of base shot speed (200)
WINGMEN_BASE_SPEED = 100  # Starting speed
WINGMEN_FIRE_COOLDOWN = 1.0  # seconds
WINGMEN_BASE_FIRE_COOLDOWN = 1.0  # Starting fire cooldown
WINGMEN_MAX_RANGE = 300
WINGMEN_SHOT_SPEED = 250
WINGMEN_RADIUS = 50

# Wingman upgrade increments
WINGMEN_SPEED_INCREMENT = 20  # Speed increase per upgrade
WINGMEN_FIRE_RATE_INCREMENT = 0.2  # Cooldown decrease per upgrade

# Wingmen formation types
WINGMEN_FORMATION_SCOUTING = 0
WINGMEN_FORMATION_CLOSE_FOLLOW = 1
WINGMEN_FORMATION_RADAR_FOLLOW = 2
EMP_RANGE = 100  # From EMP_RADIUS constant for reference

# Formation-dependent max distances for wingmen to follow asteroids
WINGMEN_MAX_ATTACK_DISTANCE = {
    WINGMEN_FORMATION_CLOSE_FOLLOW: 150,
    WINGMEN_FORMATION_SCOUTING: 500,
    WINGMEN_FORMATION_RADAR_FOLLOW: 300,
}

MAGNETIZER_BASE_PUSH_AMOUNT = 20
MAGNETIZER_PUSH_RANGE = 75
MAGNETIZER_MAX_ASTEROID_SIZE = 80

# Weapon specific:
ROTATOR_SPEED = 300
ROTATOR_RADIUS = 30

EMP_RADIUS = 100

LASER_WIDTH = 5
LASER_SPEED_MULT = 30

SHOT_RADIUS = 7
SHOT_SPEED = 400
