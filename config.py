# Swarmancer Developer Sandbox Configuration
# Use these constants to override initial game conditions for easy playtesting.

# Overrides the initial threat level (Default: 1, Max: 10).
# Modifying this instantly triggers higher-tier enemies at launch.
# Example: 3 spawns Boomers, 5 spawns Laser Drones.
DEBUG_START_THREAT_LEVEL = 1

# Overrides the starting currency (Default: 0).
# Useful for testing the Dark Altar shop purchasing flow immediately.
DEBUG_START_SOULS = 0

# Overrides the initial size of the player's swarm (Default: 50).
# Allows scaling up/down for swarm density tests.
DEBUG_START_SWARM_COUNT = 50

# Opens the shop as soon as the player loads into the game
# This is used for testing the shop functionality
DEBUG_OPEN_SHOP_AT_START = False

# A list of upgrades the player spawns with (Default: []).
# Supported values:
#   - "skeletal_archers"
#   - "grave_robbers_yield"
#   - "evasion_mastery"
#   - "bone_shrapnel"
#   - "necrotic_momentum"
#   - "plague_wizard"
# Example: DEBUG_START_UPGRADES = ["skeletal_archers", "necrotic_momentum"]
DEBUG_START_UPGRADES = []
