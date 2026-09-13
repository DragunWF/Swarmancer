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
- **InquisitionMarksman (`enemies.py`):** The ranged advanced crusader. Contains `Transform`, `Physics` (`max_speed=110.0`, `mass=1.8`), `Graphics` (`sprite_ref="marksman"`, silver-blue tint), `Collider` (standard 1-to-1 radius, `is_trigger=False`), and `AimingTimer` (`charge_duration=3.0`, `fire_duration=0.1`). Carries `near_distance_sq` (pre-computed squared halt threshold of `180² = 32400`) and `is_halted` (bool, set by `behavior_system`).
- **SoulPickup (`powerups.py`):** Dropped currency. Contains `Transform`, `Graphics`, `Collider`, `LifespanTimer`, `Value`.
- **SolarGoldBolt (`projectiles.py`):** Linear projectile fired by the InquisitionMarksman. Contains `Transform`, `Physics` (`max_speed=600.0`, pre-set `velocity`), `Graphics` (solar-gold, scale `3.0×`), `Collider` (`is_trigger=True` — routes to 1-to-1 attrition in `collision_system`), `LifespanTimer` (3s, off-screen cleanup). Carries `projectile_type = 'solar_gold_bolt'`.

## 4. System Layer (`systems/`)

Systems iterate over the entity pool every frame (60 FPS), targeting only entities possessing specific component signatures.

- **Behavior System (`behavior_system.py`):** Reads mouse inputs, calculates Boids AI rules, and updates enemy telegraph timers.
  - _Standard Enemy Tracking:_ Steers Grunt and Boomer entities toward the player cursor each frame. Marksmen are explicitly excluded from this generic loop.
  - _Optimal-Distance AI (Marksman):_ Evaluates squared distance between each `InquisitionMarksman` and the cursor. If `dist_sq > near_distance_sq`, steers normally and resets the `AimingTimer`. If `dist_sq <= near_distance_sq`, zeroes velocity and acceleration completely (halt), then increments `AimingTimer.elapsed`.
  - _Projectile Firing (Marksman):_ When `AimingTimer.elapsed >= charge_duration`, instantiates a `SolarGoldBolt` aimed at the cursor and appends it to the world entity list via `entities.extend(new_projectiles)`. Resets `AimingTimer` to begin the next cycle.
- **Movement System (`movement_system.py`):** Iterates over `Transform` + `Physics` signatures to update spatial coordinates.
- **Collision System (`collision_system.py`):** Evaluates squared distance overlaps between `Collider` components. Handles combat attrition and currency spawning.
- **Particle System (`particle_system.py`):** Manages the `LifespanTimer` of visual effects and updates `Graphics.alpha` to fade objects.
- **Particle Trigger Hooks:** `CollisionSystem` and `SpawnerSystem` receive an `on_particle_spawned(effect_type, x, y)` callback to trigger lightweight vector generation via a decoupled `ParticleEmitter` factory. The factory utilizes native `math.cos` and `math.sin` functions to generate allocation-free directional velocity vectors, maintaining the 60 FPS standard in WebAssembly.
- **Render System (`render_system.py`):** Draws pixel art, primitive shapes, and UI overlays (including dynamic timer texts for enemies) to the Pygame display surface.

## 5. Optimization Layer (`utils/`)

- **SpatialHash Grid (`spatial_hash.py`):** Divides the screen into a 2D grid matrix. Limits system processing queries strictly to adjacent cells to maintain 60 FPS.
- **Math Utilities (`math_utils.py`):** Provides fast vector normalization, squared distance calculations, and angle-to-direction mapping (`velocity_to_direction`) to map 2D velocities into 8 directional sectors (45° each).
- **Asset Loader (`asset_loader.py`):** Centralized caching utility that loads multiple distinct sprite folders (e.g., `"skeleton"`, `"skeleton_archer"`) at startup, keeping sprites at native 1.0x scale (16x16 canvas) to maintain the 60 FPS standard by eliminating disk I/O and real-time pixel modifications during the render loop.

## 6. UI Layer (`ui/`)

- **MenuController (`menu_controller.py`):** Handles static UI drawing and state signals for the Main Menu and Game Over screens. Uses primitive Pygame shapes for placeholders.
- **ShopController (`shop_controller.py`):** Manages rendering the Dark Altar overlay, multi-purchase logic, and player currency validation. Upgrades are displayed in a responsive grid layout (up to 3 columns) calculated by `_compute_layout()`. Each upgrade dict carries an `is_purchased` boolean flag; purchased items are rendered with a gray-out tint overlay and are skipped by click-detection logic. Mouse position is polled via `pygame.mouse.get_pos()` on every `draw()` call; collision against pre-computed `pygame.Rect` card bounds triggers a floating tooltip rendered above all other UI elements. A "Continue" button is always rendered at the bottom of the grid and is the sole exit path for the shop phase.

## 7. Deployment & Packaging

- **Web Assembly (pygbag):** The project is packaged for the web using `pygbag`.
- **Asynchronous Execution:** The top-level controller in `main.py` utilizes the `asyncio` library. The primary game loop is wrapped in an asynchronous function containing `await asyncio.sleep(0)` to yield execution back to the browser, preventing the tab from locking up during gameplay.

## 8. Upgrades Logic

- **Skeletal Archers:** Equips the `RangedAttack` component to a subset of existing boids upon purchase and sets `has_skeletal_archers` on `PlayerState`, ensuring that minions resurrected at glowing graves continue to spawn archers.
- **Grave Robber's Yield:** Modify the `Resource` class within `entities/powerups.py` and the associated logic in `collision_system.py` to scale the yield multiplier upon collision per upgrade tier.
- **Evasion Mastery:** Reduce the 3.0 second cooldown threshold on the `ScatterTimer` component attached to the Player entity.
- **Bone Shrapnel:** Add a secondary micro-collision damage check to the ECS logic in `collision_system.py` when Grunts and minions pop during a 1-to-1 collision.
- **Necrotic Momentum:** Increase the `max_speed` limit within the `Physics` component so the boids can condense significantly faster.
- **Multi-Purchase & Gray-Out Logic:** Upon a successful purchase in `main.py`, the selected upgrade's `is_purchased` flag is set to `True` inside the `available_upgrades` list. The upgrade is never removed from the collection. During rendering, `ShopController.draw()` evaluates `is_purchased` for each card: flagged items receive a semi-transparent dark surface blit (gray-out tint) and an "ACQUIRED" label, and are excluded from click-detection iteration. The shop state remains active until the player clicks "Continue", at which point `handle_event` returns the string `"CONTINUE"` and `main.py` transitions to `GameState.PLAYING`. Calling `refresh_upgrades()` at the start of each new shop visit resets all `is_purchased` flags to `False` without re-randomising the pool.

## 9. Pacing & Threat Level Architecture

- **Global Timer:** `current_survival_time` (float) in `main.py` accumulates `dt` every frame while `current_state == GameState.PLAYING`.
- **Non-Linear Threat Derivation:** `THREAT_THRESHOLDS = [20.0, 45.0, 75.0, 120.0, 180.0, 255.0, 330.0, 420.0, 510.0]` is defined in `main.py`. The `current_threat_level` is calculated by determining how many thresholds have been exceeded. This is passed to systems via the `threat_level` keyword argument.
- **Spawner Escalation:** `SpawnerSystem.update(entities, dt, threat_level)` heavily mutates its internal timers and spawn routines based on the level tier:
  - Spawn rates dynamically adjust according to a lookup matrix.
  - At Level 7+, `Grunt(x, y)` instantiation is modified to override the default `max_speed` of the generated `Physics` component, ensuring the change remains data-driven and avoids inheritance.
  - At Level 8+, the `spawn_grunt` method loops multiple times, adding random coordinate offsets to create swarm clusters.
- **Shop Trigger Logic:** Four milestone targets (`SHOP_MILESTONES = [75.0, 180.0, 330.0, 510.0]`) are tracked via a pointer in `main.py`. When `current_survival_time >= next_shop_milestone`, the loop enters `GameState.SHOP`.
- **Grave Spawn Rate:** `resource_timer_threshold` in `main.py` is set to `3.0` for `threat_level < 6` and `5.0` for `threat_level >= 6`.
- **InquisitionMarksman Spawn Rate:** `SpawnerSystem` introduces Marksmen at `threat_level >= 6` with a 20-second interval (`_get_marksman_spawn_rate`), reduced to 12 seconds at Level 10.
- **Elite Laser Tracking:** `BehaviorSystem.update(entities, dt, threat_level)` performs Y-axis interpolation (`lerp` toward `target_pos.y`) for `laser_drone` entities during telegraphing when `threat_level >= 9`.

## 10. Victory State

- **GameState.VICTORY** is added to `utils/state.py` as a new enum value.
- **Transition:** In `main.py`, after incrementing `current_survival_time`, the check `if current_survival_time >= 600.0 and current_state == GameState.PLAYING` transitions to `GameState.VICTORY` and records the final time.
- **Spawner Guard:** `SpawnerSystem.update()` is not called when the state is `VICTORY`, naturally halting all spawning.
- **VictoryController (MenuController):** `draw_victory(screen, final_time, souls)` renders the Victory screen. `handle_event` is extended to return `"MAIN_MENU"` when the menu button is clicked while `current_state == GameState.VICTORY`.

## 11. Static Arena Rendering

- **Background Caching:** The static arena floor (`background.jpg`) is preloaded and cached by the `AssetLoader` utility at initialization. It is loaded using Pygame's `.convert()` method to maximize opaque blitting speed. Any required dimensional scaling occurs only once at startup to prevent frame drops during gameplay.
- **ECS Decoupling:** Adhering to SOLID principles, the background is not processed as an ECS Entity. It bypasses the spatial `Transform` and `Graphics` component architecture entirely. Instead, it is blitted directly to the display surface at the very beginning of the main rendering loop (`main.py`), acting as the global base layer.
