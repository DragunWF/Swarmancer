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

## User Stories

- **As a player**, I want my skeleton minions to constantly update their position toward my cursor using Boids AI rules, **so that** I can seamlessly steer the entire horde.
- **As a player**, I want to guide my swarm into open glowing graves, **so that** my overall swarm count increases, acting as my replenishing health bar.
- **As a player**, I want charging peasant militia to destroy one of my skeletons upon contact, **so that** I must actively manage my attrition rate to prevent a game over.

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

# Epic 4: Swarm Upgrades & Progression

The player can access a mid-run or end-of-run shop system to mutate the swarm, spending collected resources to unlock specialized units and stat enhancements.

## Feature 1: The Dark Altar (Shop UI)

- The game pauses and overlays a shop interface at designated survival intervals.
- The UI displays current currency (e.g., Souls) and three randomized upgrade choices.
- Selecting an upgrade immediately applies the associated ECS components to the active swarm pool.

## Feature 2: Specialized Swarm Units

- The engine supports equipping a `RangedAttack` component to a subset of the swarm.
- These units independently calculate line-of-sight and fire projectiles at the nearest standard enemy.
- Ranged units maintain standard Boids AI rules (cohesion, alignment, separation) while firing.

## Feature 3: Currency Acquisition (Souls)

- Enemies have a calculated probability to drop a temporary Soul entity upon destruction.
- The game loop automatically awards a passive Soul stipend at 30-second survival milestones.
- Rare "Cursed Chalice" powerups spawn periodically, granting a massive currency boost rather than swarm replenishment.

## User Stories

- **As a player**, I want to spend my accumulated resources at a shop interface, **so that** I can purchase permanent upgrades that help me survive longer.
- **As a player**, I want to purchase Skeletal Archers that fire projectiles automatically, **so that** my swarm can deal damage without risking direct 1-to-1 collision attrition.
- **As a developer**, I want upgrades to dynamically attach new components to existing entities, **so that** the shop seamlessly integrates with the established ECS architecture without requiring hardcoded subclass changes.
- **As a player**, I want destroyed enemies to drop temporary Souls, **so that** I am incentivized to maneuver my swarm aggressively into combat zones.
- **As a player**, I want to receive passive currency the longer I survive, **so that** evasion and longevity are intrinsically rewarded.
- **As a player**, I want to collect rare Cursed Chalices for massive wealth, **so that** I have to weigh the risk of breaking formation to chase high-value loot.

# Epic 5: User Interface & Game State Management

The player navigates through distinct game states (Menu, Gameplay, Settings) before and after the core survival loop. This epic defines the main menu screens, audio configuration, and high score tracking required for a polished game jam entry.

## Feature 1: Main Menu & Navigation

- The application initializes into a Main Menu state upon launch.
- The menu contains clearly labeled buttons: "Play", "Controls", and "Settings".
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
