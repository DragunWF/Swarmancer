# Swarmancer: Technical Design Specification

## 1. Architecture Overview

Swarmancer utilizes a hybrid Entity-Component-System (ECS) engine. Data is stored in pure data classes (Components), bundled together by object-oriented prefabs (Entities), and processed sequentially by isolated logic loops (Systems). A top-level state machine in `main.py` manages transitions between the Menu, Gameplay, Shop, and Game Over states.

## 2. Component Layer (`components/`)

Components contain only flat data attributes and zero game logic.

- **Transform:** `x` (float), `y` (float), `rotation` (float).
- **Physics:** `velocity` (Vector2), `acceleration` (Vector2), `max_speed` (float), `mass` (float).
- **Graphics:** `sprite_ref` (string), `color` (RGB tuple), `scale` (float), `alpha` (int 0-255).
- **Collider:** `radius` (float), `is_trigger` (boolean).
- **Health:** `current` (int), `max` (int).
- **Timers:** `DenseTimer` (float, 2s max duration, 3s cooldown), `ScatterTimer` (float, defaults to 3.0), `AimingTimer` (float), `FuseTimer` (float, 5s default for Boomer self-detonation), `LifespanTimer` (float for particle/pickup decay).
- **Value:** `soul_amount` (int for currency drops).

## 3. Entity Prefabs (`entities/`)

Entities are OOP classes that act as initialization containers. They automatically instantiate and attach the required components to themselves upon creation.

- **Player (`player.py`):** Holds the central `Transform` (mapped to cursor position), `ScatterTimer`, and `DenseTimer`.
- **Boid (`swarm.py`):** Represents a skeleton minion. Contains `Transform`, `Physics`, `Graphics`, `Collider` (small radius).
- **Grunt (`enemies.py`):** The peasant militia. Contains `Transform`, `Physics` (tracking logic), `Graphics`, `Collider` (1-to-1 popping).
- **Boomer (`enemies.py`):** The dwarf sapper. Contains `Transform`, `Physics` (slow speed), `Graphics`, `Collider` (contact trigger, `is_trigger=True`), `FuseTimer` (5s fuse). Carries `blast_radius` (randomized 80–150px per spawn), `fuse_proximity_radius` (200px — fuse triggers within this range of the player cursor), and `fuse_expired` flag (set by behavior_system, read by collision_system).
- **LaserDrone (`enemies.py`):** The wizard tower. Contains `Transform` (static), `Graphics`, `AimingTimer` (controls telegraph state), `LifespanTimer` (15s duration). Carries `beam_width = 50.0` (100px total laser band).
- **SoulPickup (`powerups.py`):** Dropped currency. Contains `Transform`, `Graphics`, `Collider`, `LifespanTimer`, `Value`.

## 4. System Layer (`systems/`)

Systems iterate over the entity pool every frame (60 FPS), targeting only entities possessing specific component signatures.

- **Behavior System (`behavior_system.py`):** Reads mouse inputs, calculates Boids AI rules, and updates enemy telegraph timers.
- **Movement System (`movement_system.py`):** Iterates over `Transform` + `Physics` signatures to update spatial coordinates.
- **Collision System (`collision_system.py`):** Evaluates squared distance overlaps between `Collider` components. Handles combat attrition and currency spawning.
- **Particle System (`particle_system.py`):** Manages the `LifespanTimer` of visual effects and updates `Graphics.alpha` to fade objects.
- **Render System (`render_system.py`):** Draws pixel art, primitive shapes, and UI overlays (including dynamic timer texts for enemies) to the Pygame display surface.

## 5. Optimization Layer (`utils/`)

- **SpatialHash Grid (`spatial_hash.py`):** Divides the screen into a 2D grid matrix. Limits system processing queries strictly to adjacent cells to maintain 60 FPS.
- **Math Utilities (`math_utils.py`):** Provides fast vector normalization and squared distance calculations.

## 6. UI Layer (`ui/`)

- **MenuController (`menu_controller.py`):** Handles static UI drawing and state signals for the Main Menu and Game Over screens. Uses primitive Pygame shapes for placeholders.
- **ShopController (`shop_controller.py`):** Manages rendering the Dark Altar overlay, item selection logic, and player currency validation during shop phases. Maintains a dynamic list (`available_upgrades`) to track single-purchase constraints.

## 7. Deployment & Packaging

- **Web Assembly (pygbag):** The project is packaged for the web using `pygbag`.
- **Asynchronous Execution:** The top-level controller in `main.py` utilizes the `asyncio` library. The primary game loop is wrapped in an asynchronous function containing `await asyncio.sleep(0)` to yield execution back to the browser, preventing the tab from locking up during gameplay.

## 8. Upgrades Logic

- **Skeletal Archers:** Equips the `RangedAttack` component to a subset of existing boids upon purchase and sets `has_skeletal_archers` on `PlayerState`, ensuring that minions resurrected at glowing graves continue to spawn archers.
- **Grave Robber's Yield:** Modify the `Resource` class within `entities/powerups.py` and the associated logic in `collision_system.py` to scale the yield multiplier upon collision per upgrade tier.
- **Evasion Mastery:** Reduce the 3.0 second cooldown threshold on the `ScatterTimer` component attached to the Player entity.
- **Bone Shrapnel:** Add a secondary micro-collision damage check to the ECS logic in `collision_system.py` when Grunts and minions pop during a 1-to-1 collision.
- **Necrotic Momentum:** Increase the `max_speed` limit within the `Physics` component so the boids can condense significantly faster.
- **Single-Purchase Logic:** Upon a successful purchase in `main.py`, the selected upgrade is permanently removed from `shop_controller.available_upgrades`. If `available_upgrades` is empty, a dormant state with a single "Continue" button is rendered.

## 9. Pacing & Threat Level Architecture

- **Global Timer:** `current_survival_time` (float) in `main.py` accumulates `dt` every frame while `current_state == GameState.PLAYING`.
- **Threat Level Derivation:** `current_threat_level = min(10, int(current_survival_time // 60) + 1)`. This is computed each frame and passed to `SpawnerSystem.update()` and `BehaviorSystem.update()` as the `threat_level` keyword argument.
- **Spawner Escalation:** `SpawnerSystem.update(entities, dt, threat_level)` gates enemy type spawning behind level thresholds and dynamically sets `self.spawn_rate` based on the level tier, reading from a constant rate table.
- **Shop Trigger Logic:** Four milestone targets (`SHOP_MILESTONES = {120.0, 240.0, 360.0, 480.0}`) are tracked in a `next_shop_milestone` variable in `main.py`. When `current_survival_time >= next_shop_milestone`, the loop enters `GameState.SHOP`, awards the soul stipend, and advances `next_shop_milestone` to the next target.
- **Grave Spawn Rate:** `resource_timer_threshold` in `main.py` is set to `3.0` for Threat Levels 1–4 and `5.0` for Levels 5–10.
- **Elite Laser Tracking:** `BehaviorSystem.update(entities, dt, threat_level)` adds a Y-axis interpolation step (`lerp` toward `target_pos.y` at 30px/s) for all `laser_drone` entities when `threat_level >= 8` and the drone is in its telegraph phase (`not at.is_firing`). This preserves the single-responsibility principle: position mutation stays in the behavior system.

## 10. Victory State

- **GameState.VICTORY** is added to `utils/state.py` as a new enum value.
- **Transition:** In `main.py`, after incrementing `current_survival_time`, the check `if current_survival_time >= 600.0 and current_state == GameState.PLAYING` transitions to `GameState.VICTORY` and records the final time.
- **Spawner Guard:** `SpawnerSystem.update()` is not called when the state is `VICTORY`, naturally halting all spawning.
- **VictoryController (MenuController):** `draw_victory(screen, final_time, souls)` renders the Victory screen. `handle_event` is extended to return `"MAIN_MENU"` when the menu button is clicked while `current_state == GameState.VICTORY`.

