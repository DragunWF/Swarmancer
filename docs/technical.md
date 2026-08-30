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
- **Timers:** `ScatterTimer` (float, defaults to 3.0), `AimingTimer` (float), `LifespanTimer` (float for particle/pickup decay).
- **Value:** `soul_amount` (int for currency drops).

## 3. Entity Prefabs (`entities/`)

Entities are OOP classes that act as initialization containers. They automatically instantiate and attach the required components to themselves upon creation.

- **Player (`player.py`):** Holds the central `Transform` (mapped to cursor position) and `ScatterTimer`.
- **Boid (`swarm.py`):** Represents a skeleton minion. Contains `Transform`, `Physics`, `Graphics`, `Collider` (small radius).
- **Grunt (`enemies.py`):** The peasant militia. Contains `Transform`, `Physics` (tracking logic), `Graphics`, `Collider` (1-to-1 popping).
- **Boomer (`enemies.py`):** The dwarf sapper. Contains `Transform`, `Physics` (slow speed), `Graphics`, `Collider` (large blast radius trigger).
- **LaserDrone (`enemies.py`):** The wizard tower. Contains `Transform` (static), `Graphics`, `AimingTimer` (controls telegraph state).
- **SoulPickup (`powerups.py`):** Dropped currency. Contains `Transform`, `Graphics`, `Collider`, `LifespanTimer`, `Value`.

## 4. System Layer (`systems/`)

Systems iterate over the entity pool every frame (60 FPS), targeting only entities possessing specific component signatures.

- **Behavior System (`behavior_system.py`):** Reads mouse inputs, calculates Boids AI rules, and updates enemy telegraph timers.
- **Movement System (`movement_system.py`):** Iterates over `Transform` + `Physics` signatures to update spatial coordinates.
- **Collision System (`collision_system.py`):** Evaluates squared distance overlaps between `Collider` components. Handles combat attrition and currency spawning.
- **Particle System (`particle_system.py`):** Manages the `LifespanTimer` of visual effects and updates `Graphics.alpha` to fade objects.
- **Render System (`render_system.py`):** Draws pixel art, primitive shapes, and UI overlays to the Pygame display surface.

## 5. Optimization Layer (`utils/`)

- **SpatialHash Grid (`spatial_hash.py`):** Divides the screen into a 2D grid matrix. Limits system processing queries strictly to adjacent cells to maintain 60 FPS.
- **Math Utilities (`math_utils.py`):** Provides fast vector normalization and squared distance calculations.

## 6. Deployment & Packaging

- **Web Assembly (pygbag):** The project is packaged for the web using `pygbag`.
- **Asynchronous Execution:** The top-level controller in `main.py` utilizes the `asyncio` library. The primary game loop is wrapped in an asynchronous function containing `await asyncio.sleep(0)` to yield execution back to the browser, preventing the tab from locking up during gameplay.
