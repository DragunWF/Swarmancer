# Swarmancer: Functional Design Specification

## 1. Core Gameplay Loop & Win/Loss States

- **Objective:** Survive endless waves of enemies for as long as possible.
- **Health System:** The player does not have a traditional health bar; the total swarm count acts directly as the player's health.
- **Loss Condition:** A "Game Over" state triggers the moment the swarm count reaches zero.
- **Progression:** The game difficulty scales over time by increasing enemy spawn rates and occasionally pausing for a shop phase where players spend collected resources on upgrades.

## 2. Input Mapping & Mechanics

- **Mouse Movement:** The cursor dictates the central target point for the swarm. The swarm automatically follows the cursor using Boids AI rules (cohesion, alignment, separation).
- **Dense State (Hold Left Click):** Increases cohesion and cursor attraction. The swarm shrinks into a tight ball, useful for navigating narrow gaps or evading wide attacks. This state has a 2-second maximum duration before overheating, triggering a 3-second cooldown. Releasing early triggers a proportional cooldown.
- **Scatter Evasion (Press Right Click):** Triggers a temporary scatter evasion by applying massive repulsion physics. This forces the swarm to rapidly explode outward to escape immediate danger. This ability is restricted by a strict 3-second cooldown.

## 3. The Swarm Economy

- **The Swarm:** A massive, fluid horde of tiny skeleton minions.
- **Resource Cores:** The game spawns open glowing graves across the map.
- **Replenishment:** Guiding the swarm to consume an open glowing grave instantly grants new soldiers, offsetting combat attrition.

## 4. Enemy Entity Behaviors

- **Peasant Militia (The Grunt):**
  - **Behavior:** Charging peasant militia rush toward the player's cursor.
  - **Interaction:** Colliding with a skeleton minion triggers a 1-to-1 popping effect, destroying both entities.
- **Dwarf Sappers (The Boomer):**
  - **Behavior:** Heavy dwarf sappers carrying powder keg bombs move slowly toward the swarm.
  - **Fuse:** Each Boomer carries a 5-second fuse that only begins counting down once the Boomer enters within 200 pixels of the player cursor. Once triggered, the timer continues to tick down even if the Boomer moves out of range, ensuring it will eventually detonate.
  - **Interaction:** Upon contact with any minion, or when the fuse expires, the Boomer detonates an area-of-effect explosion. Each Boomer's blast radius is randomized between 80 and 150 pixels per spawn, keeping encounters unpredictable. This mechanic specifically punishes players who hold the Dense state (Left Click) too long.
- **Wizard Towers (The Laser Drone):**
  - **Behavior:** Stationary stone wizard towers that telegraph an attack before firing. They have a 15-second lifespan before they expire.
  - **Interaction:** Fires a wide, holy light laser beam with a 100-pixel total band (50px half-width) centered on the drone's position. This attack destroys any minion caught in its path, specifically punishing loose, spread-out formations.

## 5. UI Flow & State Management

- **HUD Elements:** In-game visual indicators including dynamic countdown timers floating above Boomers (fuse) and Laser Drones (lifespan) to clearly communicate threat urgency.
- **Main Menu:** Contains options to Play, view Controls, and adjust Settings. Displays the current highest survival time.
- **Settings:** Provides individual volume sliders/increments for master sound effects and background music.
- **Game Over Screen:** Halts all gameplay physics and enemy spawning. Compares the current run's survival time against the high score, updates it if necessary, and allows the player to restart.

## 6. The Shop Economy & Progression

- **Currency (Souls):** A secondary resource explicitly used for purchasing upgrades during shop phases, independent of the player's active swarm count.
- **Acquisition - Combat Drops:** Destroying enemies has a chance to drop a temporary Soul pickup. The player must physically maneuver the swarm to collect it before it fades.
- **Acquisition - Survival Milestones:** Players receive a passive Soul stipend for every 30 seconds they remain alive, encouraging evasion and longevity.
- **Acquisition - Rare Pickups:** High-value powerups spawn occasionally across the map. Unlike glowing graves that replenish the swarm, these specific pickups grant a massive boost to shop currency.
- **Upgrade - Grave Robber's Yield:** Consuming an open glowing grave grants an increased number of new soldiers per upgrade tier.
- **Upgrade - Evasion Mastery:** Reduces the standard 3-second cooldown on the scatter evasion (Right Click), allowing players to utilize repulsion physics more frequently against stationary stone wizard towers.
- **Upgrade - Bone Shrapnel:** Adds a secondary micro-collision damage check when Grunts pop during a 1-to-1 collision with the swarm, damaging nearby enemies.
- **Upgrade - Necrotic Momentum:** Increases the maximum speed limits of the swarm, allowing them to condense and shrink into a tight ball much faster.
- **Single-Purchase System:** Upgrades are strictly single-purchase. Once acquired, an upgrade is permanently removed from the available pool and cannot be selected in future shop phases.
- **Dormant State:** When the available upgrade pool reaches zero, the shop UI renders a "The Dark Altar is Dormant" message with a single "Continue" button to seamlessly resume the active game loop.

## 7. Threat Level Escalation

The game operates on a 10-stage difficulty arc, with the Threat Level incrementing every 60 seconds of active survival time.

| Threat Level | Time Elapsed | Active Spawn Pool                                  | Grave Spawn Rate |
|--------------|--------------|----------------------------------------------------|------------------|
| 1–2          | 0:00 – 1:59  | Grunts only                                        | Every 3 seconds  |
| 3–4          | 2:00 – 3:59  | Grunts + Boomers                                   | Every 3 seconds  |
| 5–7          | 4:00 – 6:59  | Grunts + Boomers + LaserDrones                     | Every 5 seconds  |
| 8–10         | 7:00 – 9:59  | Grunts (max density) + Boomers + Elite LaserDrones | Every 5 seconds  |

- **Grunt Spawn Rate by Level:** Levels 1–4: every 2.0s. Levels 5–7: every 1.5s. Levels 8–10: every 0.8s.
- **Elite LaserDrone Tracking (Levels 8–10):** During the telegraph phase, the drone's Y position slowly interpolates toward the player cursor's Y position at a rate of 30 pixels per second, making the horizontal laser band harder to evade with static positioning.
- **Automatic Shop Intervals:** The Dark Altar shop triggers precisely when `current_survival_time` crosses 120s, 240s, 360s, and 480s (the end of each even Threat Level). Each trigger is gated by a flag to prevent double-triggering.

## 8. Victory State

- **Win Condition:** The game is won when `current_survival_time` reaches 600 seconds (10:00).
- **On Victory:** All enemy spawning halts immediately. The game state transitions to `VICTORY`.
- **Victory Screen:** Displays a "VICTORY" title, the player's final survival score (formatted as `MM:SS`), and a "Main Menu" button.
- **Score Display:** The victory screen shows both the full 600-second run time and the final Soul count as a measure of performance.

