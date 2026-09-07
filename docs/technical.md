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
- **Math Utilities (`math_utils.py`):** Provides fast vector normalization, squared distance calculations, and angle-to-direction mapping (`velocity_to_direction`) to map 2D velocities into 8 directional sectors (45° each).
- **Asset Loader (`asset_loader.py`):** Centralized caching utility that loads multiple distinct sprite folders (e.g., `"skeleton"`, `"skeleton_archer"`) at startup, keeping sprites at native 1.0x scale (16x16 canvas) to maintain the 60 FPS standard by eliminating disk I/O and real-time pixel modifications during the render loop.

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
- **Non-Linear Threat Derivation:** `THREAT_THRESHOLDS = [20.0, 45.0, 75.0, 120.0, 180.0, 255.0, 330.0, 420.0, 510.0]` is defined in `main.py`. The `current_threat_level` is calculated by determining how many thresholds have been exceeded. This is passed to systems via the `threat_level` keyword argument.
- **Spawner Escalation:** `SpawnerSystem.update(entities, dt, threat_level)` heavily mutates its internal timers and spawn routines based on the level tier:
  - Spawn rates dynamically adjust according to a lookup matrix.
  - At Level 7+, `Grunt(x, y)` instantiation is modified to override the default `max_speed` of the generated `Physics` component, ensuring the change remains data-driven and avoids inheritance.
  - At Level 8+, the `spawn_grunt` method loops multiple times, adding random coordinate offsets to create swarm clusters.
- **Shop Trigger Logic:** Four milestone targets (`SHOP_MILESTONES = [75.0, 180.0, 330.0, 510.0]`) are tracked via a pointer in `main.py`. When `current_survival_time >= next_shop_milestone`, the loop enters `GameState.SHOP`.
- **Grave Spawn Rate:** `resource_timer_threshold` in `main.py` is set to `3.0` for `threat_level < 6` and `5.0` for `threat_level >= 6`.
- **Elite Laser Tracking:** `BehaviorSystem.update(entities, dt, threat_level)` performs Y-axis interpolation (`lerp` toward `target_pos.y`) for `laser_drone` entities during telegraphing when `threat_level >= 9`.

## 10. Victory State

- **GameState.VICTORY** is added to `utils/state.py` as a new enum value.
- **Transition:** In `main.py`, after incrementing `current_survival_time`, the check `if current_survival_time >= 600.0 and current_state == GameState.PLAYING` transitions to `GameState.VICTORY` and records the final time.
- **Spawner Guard:** `SpawnerSystem.update()` is not called when the state is `VICTORY`, naturally halting all spawning.
- **VictoryController (MenuController):** `draw_victory(screen, final_time, souls)` renders the Victory screen. `handle_event` is extended to return `"MAIN_MENU"` when the menu button is clicked while `current_state == GameState.VICTORY`.

## 11. Static Arena Rendering

- **Background Caching:** The static arena floor (`background.jpg`) is preloaded and cached by the `AssetLoader` utility at initialization. It is loaded using Pygame's `.convert()` method to maximize opaque blitting speed. Any required dimensional scaling occurs only once at startup to prevent frame drops during gameplay.
- **ECS Decoupling:** Adhering to SOLID principles, the background is not processed as an ECS Entity. It bypasses the spatial `Transform` and `Graphics` component architecture entirely. Instead, it is blitted directly to the display surface at the very beginning of the main rendering loop (`main.py`), acting as the global base layer.
