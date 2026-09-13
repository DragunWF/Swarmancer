# Swarmancer - Game Specification

## Overview

A fast-paced dark fantasy survival arena game built in Pygame using an Entity-Component-System (ECS) architecture.

# Epic 1: The Swarm Economy & Basic Attrition

The player must manage a fluid swarm against escalating waves of enemies. The swarm count acts directly as the player's health bar, requiring constant movement to consume resources and offset the 1-to-1 attrition rate of standard enemies.

## Feature 1: Boids Swarm Navigation

- The player acts as the central commander or cursor logic.
- The swarm consists of a fluid horde of tiny skeleton minions.
- Minion movement relies on calculating Boid AI rules (cohesion, alignment, separation) toward the cursor.

## Feature 2: The Replenishment Cycle

- The game periodically spawns open glowing graves to act as resource cores.
- A collision system checks for overlaps between entities with Collider components.
- Consuming an open glowing grave grants new soldiers to the swarm.

## Feature 3: Standard Enemy Attrition

- The game spawns charging peasant militia as the standard "Grunt" enemy.
- The militia utilize basic tracking logic to rush the swarm.
- Colliding with a peasant militia triggers a 1-to-1 popping effect.

## Feature 4: Ranged Attrition (The Inquisition Marksman)

- The game spawns advanced ranged crusaders known as Inquisition Marksmen at Threat Level 6+.
- Marksmen track the swarm centroid/cursor at moderate speed (110 px/s), then halt completely once within 180 pixels to avoid entering melee range.
- When halted, Marksmen telegraph a shot via their `AimingTimer` (3-second charge) and fire a fast, linear solar-gold bolt projectile targeting the swarm, then reset their firing cycle.
- The Marksman itself retains the standard 1-to-1 sacrifice counterplay: direct minion contact destroys both entities, identical to the Grunt interaction.

## User Stories

- **As a player**, I want my skeleton minions to constantly update their position toward my cursor using Boids AI rules, **so that** I can seamlessly steer the entire horde.
- **As a player**, I want to guide my swarm into open glowing graves, **so that** my overall swarm count increases, acting as my replenishing health bar.
- **As a player**, I want charging peasant militia to destroy one of my skeletons upon contact, **so that** I must actively manage my attrition rate to prevent a game over.
- **As a player**, I want to see minions face the direction they are moving using 8-directional skeleton sprites, **so that** the swarm feels alive and cohesive.
  - *Acceptance Criteria:* Minions moving in 8 cardinal/ordinal directions display the corresponding sprite. Stationary minions fallback to a default facing (e.g., South). Performance remains at 60 FPS with 300+ minions.
- **As a player**, I want Inquisition Marksmen to halt at range and fire solar-gold bolts, **so that** I must simultaneously dodge crossfire and manage advancing melee enemies.
- **As a player**, I want to sacrifice a minion by direct contact with a Marksman to destroy it, **so that** aggressive flanking is a viable counter-strategy against ranged threats.

# Epic 2: Shape-Shifting Combat Mechanics

The player's ability to manipulate the swarm's density and trigger scatter evasions. This epic covers the active input states required to survive advanced enemy types.

## Feature 1: Density Control (Dense State)

- The player can trigger a physical state change by holding Left Click.
- Activating this state increases cohesion and cursor attraction.
- This mechanic allows the swarm to shrink into a tight ball to evade area-of-effect explosions from Boomers.
- The state has a 2-second maximum duration before overheating, which triggers a 3-second cooldown. Releasing early triggers a proportional cooldown.

## Feature 2: Scatter Evasion (Panic State)

- The player triggers a temporary scatter evasion by pressing the right mouse button.
- The ability functions by applying correct repulsion physics to push the boids rapidly outward.
- The mechanic is restricted by a 3-second cooldown.

## Feature 3: Anti-State Enemy Interactions

- Boomer enemies initialize with a variable blast radius component, randomized per spawn between 80 and 150 pixels.
- Boomers act as heavy dwarf sappers carrying powder keg bombs.
- A Boomer detonates its area-of-effect explosion either upon contact with any minion, or automatically after a 5-second fuse timer expires, whichever comes first. The fuse only begins counting down once the Boomer enters within 200 pixels of the player swarm. Once triggered, the fuse continues to tick down regardless of distance.
- Boomer explosions heavily punish players who stay in the tightly packed "Dense" state.
- Laser Drones act as stationary stone wizard towers that telegraph a wide, holy light laser beam.
- A Laser Drone will telegraph an attack before firing.
- Laser Drones fire a beam with a 100-pixel total band (50px half-width), specifically punishing loose, spread-out swarm formations.
- Laser Drones have a lifespan of 15 seconds, after which they automatically despawn to prevent cluttering the arena.

## User Stories

- **As a player**, I want to hold Left Click to drastically increase cohesion and cursor attraction, **so that** my swarm shrinks into a tight ball to evade area-of-effect explosions from Boomers.
- **As a player**, I want to press the right mouse button to scatter my swarm using repulsion physics, **so that** I can rapidly escape immediate danger.
- **As a player**, I want the scatter evasion to trigger a 3-second cooldown, **so that** I cannot spam the ability to stay permanently invincible.
- **As a player**, I want a Laser Drone to telegraph an attack before firing, **so that** I have enough warning to condense my spread-out swarm and dodge the beam.

# Epic 3: Technical ECS Architecture & Systems

Establish the underlying hybrid Entity-Component-System (ECS) engine and spatial optimization structures. This epic ensures high-performance rendering and sequential data processing required to manage hundreds of active boid entities without framerate drops.

## Feature 1: Component & Entity Composition

- Define light, data-only Component classes to hold position, velocity, hitboxes, and timers.
- Use Object-Oriented Entity containers as prefabs to bundle components automatically upon instantiation.
- Maintain strict separation between entity data storage and system processing logic.

## Feature 2: Core Processing Systems

- Movement System: Iterates through entities containing Transform and Physics components to calculate new positions.
- Behavior System: Evaluates Boids flocking vectors, tracking behaviors, and laser telegraphing routines.
- Collision System: Evaluates bounding box and distance-squared overlaps between active Colliders.
- Particle System: Processes life cycles, shrink scale logic, and rendering for death burst particles.
- Render System: Draws entities and active particle effects onto the Pygame display surface.

## Feature 3: Spatial Partitioning & Performance Optimization

- Implement a SpatialHash grid system in the utility layer.
- Group spatial entities into discrete grid cells based on screen coordinates.
- Query only neighboring grid cells during Boid perception and collision detection routines to maintain a constant 60 FPS.

## User Stories

- **As a developer**, I want components to contain only data attributes, **so that** systems can process game logic in clean, sequential sweeps.
- **As a developer**, I want to query spatial neighbors through a SpatialHash grid, **so that** distance calculations for hundreds of swarm entities remain performant without checking every entity against every other entity.
- **As a developer**, I want collision checks to evaluate squared distance values, **so that** the computational overhead of square root calculations is avoided during runtime.
- **As a player**, I want entity deaths to spawn fading particle pops managed by a particle system, **so that** combat impacts feel visually clear and responsive.
- **As a player**, I want to see distinctly colored and physics-driven particle bursts for Skeleton Shatters, Crusader Vanguard Pops, Sun Wizard Teleportations, and Dwarf Sapper Detonations, **so that** specific combat events provide immediate, readable visual feedback.

# Epic 4: Swarm Upgrades & Progression

The player can access a mid-run or end-of-run shop system to mutate the swarm, spending collected resources to unlock specialized units and stat enhancements.

## Feature 1: The Dark Altar (Shop UI)

- The game pauses and overlays a shop interface at designated survival intervals.
- The UI displays current currency (e.g., Souls) and renders all available upgrades simultaneously in a persistent grid layout.
- The player can purchase multiple upgrades during a single shop phase as long as they have sufficient Souls.
- The shop remains open until the player explicitly clicks a "Continue" button.
- Purchased upgrades are flagged and persistently rendered on the grid with a grayed-out tint and disabled interactions, instead of being removed from the pool, so the player can track what they have acquired.
- Hovering the mouse over an upgrade's bounding box dynamically renders a floating tooltip containing its specific description and cost.

## Feature 2: Specialized Swarm Units

- The engine supports equipping a `RangedAttack` or `PlagueCaster` component to a subset of the swarm.
- These units independently calculate line-of-sight and fire projectiles at the nearest standard enemy.
- Ranged units maintain standard Boids AI rules (cohesion, alignment, separation) while firing.
- `PlagueCaster` units fire Plague Bombs that trigger AoE detonations upon hitting an enemy, severely damaging dense clusters of standard enemies.

## Feature 3: Currency Acquisition (Souls)

- Enemies have a calculated probability to drop a temporary Soul entity upon destruction.
- The game loop automatically awards a passive Soul stipend at 30-second survival milestones.
- Rare "Cursed Chalice" powerups spawn periodically, granting a massive currency boost rather than swarm replenishment.

## User Stories

- **As a player**, I want to spend my accumulated resources at a shop interface, **so that** I can purchase permanent upgrades that help me survive longer.
- **As a player**, I want to see all available upgrades in a grid layout, **so that** I can plan my build progression across the entire pool rather than relying on randomized draws.
- **As a player**, I want to purchase multiple upgrades in a single shop phase, **so that** I can spend accumulated Souls efficiently in one visit.
- **As a player**, I want purchased upgrades to remain visible but grayed out on the grid, **so that** I can easily track what I have already acquired during the run.
- **As a player**, I want a "Continue" button to manually exit the shop, **so that** I control when to return to the combat phase.
- **As a player**, I want to see a tooltip when hovering over an upgrade, **so that** I understand its effects and cost before spending my Souls.
- **As a player**, I want to purchase Skeletal Archers that fire projectiles automatically, **so that** my swarm can deal damage without risking direct 1-to-1 collision attrition.
- **As a developer**, I want upgrades to dynamically attach new components to existing entities, **so that** the shop seamlessly integrates with the established ECS architecture without requiring hardcoded subclass changes.
- **As a player**, I want destroyed enemies to drop temporary Souls, **so that** I am incentivized to maneuver my swarm aggressively into combat zones.
- **As a player**, I want to receive passive currency the longer I survive, **so that** evasion and longevity are intrinsically rewarded.
- **As a player**, I want to collect rare Cursed Chalices for massive wealth, **so that** I have to weigh the risk of breaking formation to chase high-value loot.
- **As a player**, I want to purchase Grave Robber's Yield, **so that** I receive more minions every time I consume an open glowing grave.
- **As a player**, I want to purchase Evasion Mastery, **so that** the cooldown on my scatter evasion is reduced, allowing me to dodge Laser Drone beams more frequently.
- **As a player**, I want to purchase Bone Shrapnel, **so that** my minions deal secondary area damage when they pop against charging peasant militia.
- **As a player**, I want to purchase Necrotic Momentum, **so that** my swarm's maximum speed increases, letting them condense into a tight ball much faster.
- **As a player**, I want to purchase Plague Wizard, **so that** a subset of my minions fire toxic projectiles that explode on impact, destroying clusters of enemies simultaneously.
- **As a player**, I want upgrade items to be grayed out after I purchase them, **so that** I can see my build history and am prevented from re-purchasing the same upgrade.
- **As a player**, I want the shop to display a "The Dark Altar is Dormant" message with a continue button when all upgrades are purchased, **so that** the shop phase resolves smoothly when the pool is empty.

# Epic 5: User Interface & Game State Management

The player navigates through distinct game states (Menu, Gameplay, Settings) before and after the core survival loop. This epic defines the main menu screens, audio configuration, and high score tracking required for a polished game jam entry.

## Feature 1: Main Menu & Navigation

- The application initializes into a Main Menu state upon launch.
- The main menu renders a dedicated scaled background image (`menu-background.png`).
- A global background dimming overlay (semi-transparent black) sits behind the UI to enhance text readability.
- Advanced text rendering applies 1px outlines and drop shadows to all menu titles and labels.
- The menu contains clearly labeled buttons: "Play", "Controls", and "Settings".
- Buttons use a Deep Charcoal background with Bone-white default borders/text, which switch to a Solar-Gold highlight on mouse hover.
- Clicking "Play" transitions the application into the active Gameplay state, resetting the survival timer and swarm count.
- Clicking "Controls" opens an overlay detailing the left-click (Dense) and right-click (Scatter) inputs.

## Feature 2: High Score Tracking

- The game records the highest survival time achieved during the current session.
- The high score is prominently displayed on the Main Menu interface.
- When a "Game Over" state triggers (swarm count reaches zero), the system compares the final survival time against the stored high score and updates it if necessary.

## Feature 3: Audio Settings & Configuration

- The Settings menu allows players to adjust the master volume for sound effects and background music independently.
- Adjustments are made via clickable sliders or discrete increment buttons (e.g., +/- 10%).
- The Pygame mixer is updated dynamically as the user modifies these settings.

## Feature 4: Pause Menu & Audio Settings

- The pause menu is triggered by pressing the "P" key, safely halting the continuous tick of the real-time game loop.
- The controls menu displays the "P" key binding alongside movement and swarm inputs.
- The pause overlay provides options to Continue, Return to Main Menu, and adjust individual volume sliders for Sound Effects and Music.
- Selecting the Main Menu option triggers a secondary confirmation dialog ("Are you sure? Progress will be lost.") to prevent accidental quits.
- State transitions and volume adjustments are managed via an MVC overlay controller that pauses processing in the active ECS world.

## User Stories

- **As a player**, I want to see my high score on the main menu, **so that** I have a clear benchmark to beat in my next session.
- **As a player**, I want to access a Controls overlay from the main menu, **so that** I understand the density and scatter mechanics before starting a run.
- **As a player**, I want to adjust the volume of sound effects and music independently in a Settings menu, **so that** I can balance the audio to my personal preference.
- **As a developer**, I want the game logic to pause entirely while in the Menu or Settings states, **so that** enemies do not spawn and the physics engine does not process data in the background.
- **As a player**, I want to press "P" to open the pause menu, **so that** I can safely step away from the active game loop without my swarm dying.
- **As a player**, I want to see the "P" key listed in the controls menu, **so that** I know how to halt the game.
- **As a player**, I want to adjust the sound effects and music volume within the pause screen, **so that** I can balance the audio to my preference.
- **As a player**, I want a confirmation dialog to appear when selecting the Main Menu button, **so that** I do not accidentally erase my current survival run.

## Feature 5: Active Gameplay HUD & Visual Feedback

- **Minimalist HUD Anchors:** The HUD displays pure text without icons. Swarm Count is anchored top-left, Souls top-right, and Survival Timer top-center.
- **Advanced Rendering:** HUD elements use 1px outlines and drop shadows for high contrast against the background.
- **Diegetic Floating Text:** Collecting currency drops spawns a "+[amount]" text entity that floats upward and fades out.
- **Danger Vignette:** A faint red pulsing vignette appears at the screen edges when the swarm count drops below 15.
- **Minimalist Action Bar:** A sleek horizontal progress bar anchored at the bottom-center. It tracks the Scatter ability cooldown with a horizontal liquid fill, pulsing when ready. It is positioned directly beneath dynamic text hints (`[LMB] Condense  |  Scatter [RMB]`) that snap to full brightness when the cooldown completes.

## Feature 6: Event-Driven Background Music Playlist

- The game features a dynamic background music playlist utilizing the Pygame mixer.
- The playlist sequentially loops through 4 tracks located in `/audio/music/`:
  1. `desert_dawn.ogg` (Index 0)
  2. `oasis_quest.ogg` (Index 1)
  3. `desert_dash.ogg` (Index 2)
  4. `desert_storm.ogg` (Index 3)
- Upon completion of `desert_storm.ogg` (Index 3), the playlist pointer loops back to `oasis_quest.ogg` (Index 1) and continues cycling (1-2-3-1-2-3). Index 0 acts strictly as the intro track for the start of the run.
- Transitions are event-driven (`pygame.mixer.music.set_endevent`) and handled within the main game loop (`pygame.event.get()`), avoiding threading or blocking queues to maintain strict WebAssembly (Pygbag) compatibility.
- Music playback persists seamlessly when the game transitions into `PAUSE` or `SHOP` states.

## Feature 7: SFX Asset Integration & Triggers

- The game features non-blocking `.wav` sound effects pre-loaded into a centralized `AssetLoader` dictionary.
- The Pygame mixer is initialized with `pygame.mixer.set_num_channels(16)` to ensure overlapping sounds (e.g., rapid pops and explosions) do not cut each other off.
- Seven distinct `.wav` assets are utilized:
  1. `skeleton_pop`: Triggered in `CollisionSystem` on 1-to-1 attrition and projectile hits.
  2. `dwarf_explosion`: Triggered in `CollisionSystem` during Boomer AoE and PlagueBomb detonations.
  3. `laser_spell`: Triggered in `BehaviorSystem` when a Laser Drone's `AimingTimer` reaches its firing threshold.
  4. `win`: Triggered in `main.py` when transitioning to the `VICTORY` state.
  5. `lose`: Triggered in `main.py` when transitioning to the `GAME_OVER` state.
  6. `ui_click`: Triggered across `menu_controller.py`, `shop_controller.py`, and `pause_controller.py` on successful button interactions or upgrade purchases.
  7. `ui_error`: Triggered in `main.py` when attempting to purchase an upgrade with insufficient Souls in the Dark Altar.
- The `AssetLoader` provides a `set_sfx_volume(volume)` method dynamically linked to the SFX slider in `pause_controller.py`, actively updating the playback volume for all 7 loaded sounds simultaneously.

# Epic 6: Pacing, Escalation & Victory

The game presents a structured 10-minute survival arc, where a global Threat Level (1–10) escalates every 60 seconds, automatically injecting new enemy types into the spawn pool, tightening shop intervals, and culminating in a Victory state when the player survives all 10 levels.

## Feature 1: Non-Linear Threat Level Scaling

- A global `threat_level` integer (1-10) is determined by evaluating the survival time against an explicit, non-linear threshold array, dramatically compressing the early game.
- The `SpawnerSystem` reads the current `threat_level` to govern hazard injection.
- Level 1 (0:00): Grunts only. Plentiful glowing graves.
- Level 2 (0:20): Grunt spawn cooldown halved; wave density doubles.
- Level 3 (0:45): Heavy dwarf sappers (Boomers) enter the spawn pool.
- Level 5 (2:00): Stationary stone wizard towers (LaserDrones) enter the spawn pool.
- Level 7 (4:15): Newly spawned Grunts receive a boosted maximum velocity via their Physics component.
- Level 8 (5:30): Grunts spawn in tight, dense clusters rather than isolated individuals.
- Level 9 (7:00): LaserDrones engage elite Y-axis tracking during their telegraph phase.
- Level 10 (8:30): Spawn rates across all hazard types are maximized.

## Feature 2: Staggered Shop Intervals

- The Dark Altar shop UI automatically triggers at the exact start times of Threat Levels 4 (1:15), 6 (3:00), 8 (5:30), and 10 (8:30).
- Level 6 specifically begins resource starvation by throttling the spawn rate of glowing graves.
- The shop trigger safely pauses the ECS physics loop and awards the passive Soul stipend.

## Feature 3: 10-Minute Victory Condition

- When `current_survival_time` reaches 600 seconds (10 minutes), all enemy spawning halts.
- The game transitions to the `VICTORY` state via the MVC state machine in `main.py`.
- The `VictoryController` (rendered by `menu_controller.py`) displays a victory title, the final survival score, and a "Main Menu" button to return to the start screen.

## User Stories

- **As a player**, I want the game to clearly escalate its difficulty over 10 stages, **so that** I experience a structured challenge arc rather than an immediate, unmanageable difficulty spike.
- **As a player**, I want the shop to automatically open at fixed 2-minute intervals, **so that** I can plan my build progression around a reliable upgrade schedule.
- **As a player**, I want to be rewarded with a Victory screen if I survive 10 full minutes, **so that** my run has a clear, achievable win condition beyond endless attrition.
- **As a player**, I want glowing graves to become scarcer at higher Threat Levels, **so that** the mid-to-late game feels increasingly desperate and the swarm economy tightens.
- **As a player**, I want elite LaserDrones to track my swarm's Y position during higher Threat Levels, **so that** the late game demands active, precise evasion rather than static positioning.
- **As a developer**, I want the `threat_level` to be passed as a parameter into `SpawnerSystem.update()` and `BehaviorSystem.update()`, **so that** the escalation logic remains cleanly contained within the System layer and does not pollute the main game loop.

## Feature 5: Static Environmental Assets
- The game arena utilizes a static 2D pixel art background (`background.jpg`) as the foundational floor layer.
- The background sits seamlessly behind all active ECS entities, particles, and UI elements without impacting collision physics.
- **User Story:** **As a player**, I want to see a detailed, thematic arena background, **so that** the game world feels cohesive and immersive rather than an empty black void.

# Epic 7: Developer Sandbox & Playtest Configuration

The game includes a centralized configuration file (`config.py`) to streamline playtesting by allowing developers to easily manipulate initial game states. This eliminates the need to wait for the organic escalation of the game loop to test mid-to-late game mechanics.

## Feature 1: Debug Configuration Overrides

- `DEBUG_START_THREAT_LEVEL`: Overrides the initial threat level (Default: 1, Max: 10). Modifying this instantly triggers higher-tier enemies at launch.
- `DEBUG_START_SOULS`: Overrides the starting currency (Default: 0).
- `DEBUG_START_SWARM_COUNT`: Overrides the initial size of the player's swarm (Default: 50).
- `DEBUG_START_UPGRADES`: A list of upgrades the player spawns with (Default: []). Supported values: "skeletal_archers", "grave_robbers_yield", "evasion_mastery", "bone_shrapnel", "necrotic_momentum", "plague_wizard".

## Feature 2: Initialization Logic

- `main.py` reads these constants when launching a new game session (`GameState.PLAYING`).
- If `DEBUG_START_THREAT_LEVEL > 1`, the survival timer is offset correctly to match the threshold of that threat level, and the system automatically advances the `next_shop_milestone_index` pointer so past shop phases do not trigger out of order.
- Active `DEBUG_START_UPGRADES` are applied immediately to the `PlayerState` on start and removed from the shop's available pool.
