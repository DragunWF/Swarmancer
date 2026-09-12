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

- **The Swarm:** A massive, fluid horde of tiny skeleton minions. They visually represent their movement using 8-directional skeleton sprites, and upgraded Skeletal Archers use a distinct "Sun-Faded Marksman" sprite set.
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

## 4b. Visual Feedback (Particle Effects)
- **Skeleton Shatter:** Destroyed minions emit bleached bone-white and necrotic cyan pixels.
- **Crusader Vanguard Pop:** Destroyed Grunts emit a chaotic burst of sunbaked tan and sweat-stained yellow pixels.
- **Sun Wizard Teleportation:** Laser Drones emit a high-velocity, non-fading solar-gold burst upon instantiation, and a similar explosive exit teleportation burst upon death.
- **Dwarf Sapper Detonation:** Boomers emit a dense radial blast of deep copper, charred brown, and blazing solar-gold sparks with heavy drag to simulate lingering smoke.

## 5. UI Flow & State Management

- **HUD Elements:** In-game visual indicators including dynamic countdown timers floating above Boomers (fuse) and Laser Drones (lifespan) to clearly communicate threat urgency. Also features anchored minimalist text for Swarm, Souls, and Timer, floating diegetic text on pickup, a pulsating red danger vignette when swarm count is critical, and a Minimalist Action Bar to visually track the Scatter ability cooldown alongside dynamic text hints.
- **Main Menu:** Contains options to Play, view Controls, and adjust Settings. Displays the current highest survival time and the game's menu background image (`menu-background.png`).
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

The game operates on a non-linear 10-stage difficulty arc designed to compress the early game and rapidly scale chaos. The Threat Level shifts according to an explicit schedule of survival time thresholds.

| Level | Time | Key Escalation Trigger | Shop Pause |
|-------|------|------------------------|------------|
| 1 | 0:00 | Baseline Grunts | - |
| 2 | 0:20 | Grunt density doubled | - |
| 3 | 0:45 | Boomers introduced | - |
| 4 | 1:15 | Boomer spawn rate increased | YES |
| 5 | 2:00 | LaserDrones introduced | - |
| 6 | 3:00 | Grave spawns throttled | YES |
| 7 | 4:15 | Grunt velocity increased | - |
| 8 | 5:30 | Grunts spawn in massive clusters | YES |
| 9 | 7:00 | Elite tracking on LaserDrones | - |
| 10 | 8:30 | All spawn rates maximized | YES |

- **Automatic Shop Intervals:** The Dark Altar shop triggers precisely at 75s, 180s, 330s, and 510s.
- **Resource Starvation:** The time between glowing grave spawns increases from 3 seconds to 5 seconds at Level 6.
- **Velocity Scaling (Level 7+):** Newly spawned Grunts have their Physics `max_speed` significantly elevated.
- **Cluster Spawning (Level 8+):** Grunts spawn in groups of 3-5 simultaneously at a single edge location.
- **Elite LaserDrone Tracking (Level 9+):** During the telegraph phase, the drone's Y position slowly interpolates toward the player cursor's Y position at a rate of 30 pixels per second.

## 8. Victory State

- **Win Condition:** The game is won when `current_survival_time` reaches 600 seconds (10:00).
- **On Victory:** All enemy spawning halts immediately. The game state transitions to `VICTORY`.
- **Victory Screen:** Displays a "VICTORY" title, the player's final survival score (formatted as `MM:SS`), and a "Main Menu" button.
- **Score Display:** The victory screen shows both the full 600-second run time and the final Soul count as a measure of performance.

