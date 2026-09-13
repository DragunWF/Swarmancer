import asyncio
import pygame
import random
import math
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR
from entities.player import Player
from entities.boid import Boid
from entities.powerups import Resource
from systems.behavior_system import BehaviorSystem
from systems.movement_system import MovementSystem
from systems.render_system import RenderSystem
from systems.collision_system import CollisionSystem
from systems.spawner_system import SpawnerSystem
from systems.particle_system import ParticleSystem, ParticleEmitter

from utils.state import GameState
from ui.hud_controller import HUDController
from ui.shop_controller import ShopController
from ui.menu_controller import MenuController
from ui.pause_controller import PauseController
from components.combat import RangedAttack
from components.combat import PlagueCaster
from systems.combat_system import CombatSystem
from utils.asset_loader import AssetLoader
from config import DEBUG_START_THREAT_LEVEL, DEBUG_START_SOULS, DEBUG_START_SWARM_COUNT, DEBUG_START_UPGRADES, DEBUG_OPEN_SHOP_AT_START

# Explicit time thresholds (seconds) for Threat Levels 2 through 10
THREAT_THRESHOLDS = [20.0, 45.0, 75.0, 120.0, 180.0, 255.0, 330.0, 420.0, 510.0]

# Ordered list of survival-time milestones (seconds) that trigger automatic shop pauses.
SHOP_MILESTONES = [75.0, 180.0, 330.0, 510.0]

# Survival time (seconds) at which the game is won.
VICTORY_DURATION = 600.0

# Grave spawn interval (seconds) by Threat Level tier.
_GRAVE_RATE_EARLY = 3.0   # Levels 1–4
_GRAVE_RATE_LATE = 5.0    # Levels 5–10

async def main():
    pygame.init()
    
    # Audio Playlist Setup
    TRACK_END_EVENT = pygame.USEREVENT + 1
    PLAYLIST = [
        "audio/music/desert_dawn.ogg",
        "audio/music/oasis_quest.ogg",
        "audio/music/desert_dash.ogg",
        "audio/music/desert_storm.ogg"
    ]
    current_track_index = 0
    try:
        pygame.mixer.init()
        pygame.mixer.set_num_channels(16)
        pygame.mixer.music.set_endevent(TRACK_END_EVENT)
        pygame.mixer.music.load(PLAYLIST[current_track_index])
        # Game starts in MENU, so we don't play() here.
    except Exception as e:
        print(f"Warning: Audio system failed to initialize: {e}")
        PLAYLIST = []

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Swarmancer")
    AssetLoader().initialize()
    clock = pygame.time.Clock()
    
    entities = []
    
    # Session state
    high_score = 0.0
    current_survival_time = 0.0
    player = None
    current_boid_max_speed = 350.0
    current_threat_level = 1
    next_shop_milestone_index = 0  # Pointer into SHOP_MILESTONES
    victory_souls = 0              # Captured at the moment of victory for display
    shop_warning_shown = False     # Tracks if the pre-shop warning has been shown
    
    # External closures needed for systems
    def on_resource_collected(resource):
        # Spawn ShatterParticles
        if on_particle_spawned:
            on_particle_spawned("skeleton_shatter", resource.transform.x, resource.transform.y)

        # Spawn boids slightly offset from the grave based on yield amount
        has_archers = player and getattr(player.state, 'has_skeletal_archers', False)
        has_plague = player and getattr(player.state, 'has_plague_wizard', False)
        for i in range(resource.yield_amount):
            new_boid = Boid(resource.transform.x + random.uniform(-20, 20), resource.transform.y + random.uniform(-20, 20), max_speed=current_boid_max_speed)
            
            # Apply Ranged mutations randomly
            if has_archers and (i == 0 or random.random() < 0.25):
                new_boid.ranged_attack = RangedAttack(fire_rate=1.0, attack_range=150.0, projectile_speed=300.0)
                new_boid.graphics.sprite_ref = "skeleton_archer"
            elif has_plague and random.random() < 0.25:
                from components.combat import PlagueCaster
                new_boid.plague_caster = PlagueCaster(cooldown=3.0, blast_radius=80.0, attack_range=150.0, projectile_speed=300.0)
                new_boid.graphics.sprite_ref = "plague_wizard"
                
            entities.append(new_boid)

    def on_currency_collected(amount, x, y):
        # Spawn ShatterParticles for currency
        if on_particle_spawned:
            on_particle_spawned("skeleton_shatter", x, y)
            
        if player:
            player.souls += amount
            
        # Spawn Floating Text
        from entities.particles import FloatingText
        entities.append(FloatingText(x, y, f"+{amount}"))

    def on_entity_spawned(entity):
        entities.append(entity)
        
    def on_particle_spawned(effect_type, x, y):
        particles = ParticleEmitter.emit(effect_type, x, y)
        entities.extend(particles)
        
    # Initialize Systems
    behavior_system = BehaviorSystem()
    movement_system = MovementSystem()
    collision_system = CollisionSystem(
        on_resource_collected=on_resource_collected,
        on_currency_collected=on_currency_collected,
        on_entity_spawned=on_entity_spawned,
        on_particle_spawned=on_particle_spawned
    )
    particle_system = ParticleSystem(on_particle_spawned=on_particle_spawned)
    render_system = RenderSystem()
    spawner_system = SpawnerSystem(SCREEN_WIDTH, SCREEN_HEIGHT, on_particle_spawned=on_particle_spawned)
    combat_system = CombatSystem()
    
    systems = [spawner_system, behavior_system, combat_system, movement_system, collision_system, particle_system, render_system]
    
    # Controllers
    hud_controller = HUDController(SCREEN_WIDTH, SCREEN_HEIGHT)
    shop_controller = ShopController(SCREEN_WIDTH, SCREEN_HEIGHT)
    menu_controller = MenuController(SCREEN_WIDTH, SCREEN_HEIGHT)
    pause_controller = PauseController(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    current_state = GameState.MENU
    
    resource_timer = 0.0
    shop_timer = 0.0

    def reset_game():
        nonlocal player, resource_timer, shop_timer, current_survival_time, current_boid_max_speed
        nonlocal current_threat_level, next_shop_milestone_index, victory_souls, shop_warning_shown
        nonlocal current_track_index
        entities.clear()
        
        if PLAYLIST:
            current_track_index = 0
            try:
                pygame.mixer.music.load(PLAYLIST[current_track_index])
                pygame.mixer.music.play()
            except Exception:
                pass

        player_x = SCREEN_WIDTH / 2
        player_y = SCREEN_HEIGHT / 2
        player = Player(player_x, player_y)
        player.souls = DEBUG_START_SOULS
        entities.append(player)

        current_boid_max_speed = 350.0
        Resource.yield_amount = 3
        # Rebuild available_upgrades with is_purchased flags reset to False.
        # We never remove items mid-run; purchases are tracked via the flag.
        shop_controller.available_upgrades = [
            {**upg, "is_purchased": False} for upg in shop_controller.all_upgrades
        ]
        shop_controller._compute_layout()
        
        current_threat_level = DEBUG_START_THREAT_LEVEL
        if current_threat_level > 1:
            offset_idx = min(current_threat_level - 2, len(THREAT_THRESHOLDS) - 1)
            current_survival_time = THREAT_THRESHOLDS[offset_idx]
        else:
            current_survival_time = 0.0
            
        next_shop_milestone_index = 0
        shop_warning_shown = False
        while next_shop_milestone_index < len(SHOP_MILESTONES) and current_survival_time >= SHOP_MILESTONES[next_shop_milestone_index]:
            next_shop_milestone_index += 1
            
        victory_souls = 0

        for _ in range(DEBUG_START_SWARM_COUNT):
            boid = Boid(player_x + random.uniform(-60, 60), player_y + random.uniform(-60, 60), max_speed=current_boid_max_speed)
            entities.append(boid)
            
        upgrade_map = {
            "skeletal_archers": 0,
            "grave_robbers_yield": 1,
            "evasion_mastery": 2,
            "bone_shrapnel": 3,
            "necrotic_momentum": 4,
            "plague_wizard": 5
        }
        for upgrade_name in DEBUG_START_UPGRADES:
            upgrade_id = upgrade_map.get(upgrade_name)
            if upgrade_id is not None:
                if upgrade_id == 0:
                    player.state.has_skeletal_archers = True
                    boids = [e for e in entities if isinstance(e, Boid) and not hasattr(e, 'ranged_attack')]
                    upgrade_count = min(10, len(boids))
                    if upgrade_count > 0:
                        for b in random.sample(boids, upgrade_count):
                            b.ranged_attack = RangedAttack(fire_rate=1.0, attack_range=150.0, projectile_speed=300.0)
                            b.graphics.sprite_ref = "skeleton_archer"
                elif upgrade_id == 1:
                    Resource.yield_amount += 1
                elif upgrade_id == 2:
                    player.scatter_timer.cooldown_duration = max(1.0, player.scatter_timer.cooldown_duration - 0.5)
                elif upgrade_id == 3:
                    setattr(player.state, 'has_bone_shrapnel', True)
                elif upgrade_id == 4:
                    current_boid_max_speed += 50.0
                    for b in [e for e in entities if isinstance(e, Boid)]:
                        b.physics.max_speed = current_boid_max_speed
                elif upgrade_id == 5:
                    player.state.has_plague_wizard = True
                    boids = [e for e in entities if isinstance(e, Boid) and not hasattr(e, 'plague_caster') and not hasattr(e, 'ranged_attack')]
                    upgrade_count = min(10, len(boids))
                    if upgrade_count > 0:
                        for b in random.sample(boids, upgrade_count):
                            b.plague_caster = PlagueCaster(cooldown=3.0, blast_radius=80.0, attack_range=150.0, projectile_speed=300.0)
                            b.graphics.color = (0, 255, 150) # Tinge them green
                shop_controller.remove_upgrade(upgrade_id)

        resource_timer = 0.0
        shop_timer = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if PLAYLIST and event.type == TRACK_END_EVENT:
                # Only automatically load and play the next track if we are in an active state.
                # When pygame.mixer.music.stop() is called on game over, it triggers this event,
                # and without this check, it would instantly restart music on the Game Over screen.
                if current_state in (GameState.PLAYING, GameState.PAUSED, GameState.SHOP):
                    current_track_index += 1
                    if current_track_index >= len(PLAYLIST):
                        current_track_index = 1  # Loop back to oasis_quest.ogg (Index 1)
                    try:
                        pygame.mixer.music.load(PLAYLIST[current_track_index])
                        pygame.mixer.music.play()
                    except Exception as e:
                        print(f"Warning: Could not load track {current_track_index}: {e}")
                    
            if current_state == GameState.PLAYING and event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                current_state = GameState.PAUSED
                continue
                
            if current_state in (GameState.MENU, GameState.GAME_OVER, GameState.VICTORY):
                action = menu_controller.handle_event(event, current_state)
                if action == "PLAY":
                    reset_game()
                    if DEBUG_OPEN_SHOP_AT_START:
                        current_state = GameState.SHOP
                        shop_controller.refresh_upgrades()
                    else:
                        current_state = GameState.PLAYING
                elif action == "MAIN_MENU":
                    current_state = GameState.MENU
                    if PLAYLIST: pygame.mixer.music.stop()
                    
            elif current_state == GameState.SHOP:
                selected_upgrade = shop_controller.handle_event(event)
                if selected_upgrade == "CONTINUE":
                    AssetLoader().play_sound("ui_click")
                    current_state = GameState.PLAYING
                elif selected_upgrade is not None:
                    upgrade_data = next((u for u in shop_controller.all_upgrades if u["id"] == selected_upgrade), None)
                    if upgrade_data and player.souls >= upgrade_data["cost"]:
                        AssetLoader().play_sound("ui_click")
                        player.souls -= upgrade_data["cost"]
                        
                        if selected_upgrade == 0:
                            # Apply Archer Upgrade
                            player.state.has_skeletal_archers = True
                            boids = [e for e in entities if isinstance(e, Boid) and not hasattr(e, 'ranged_attack')]
                            upgrade_count = min(10, len(boids))
                            if upgrade_count > 0:
                                for b in random.sample(boids, upgrade_count):
                                    b.ranged_attack = RangedAttack(fire_rate=1.0, attack_range=150.0, projectile_speed=300.0)
                                    b.graphics.sprite_ref = "skeleton_archer"
                        elif selected_upgrade == 1:
                            # Grave Robber's Yield
                            Resource.yield_amount += 1
                        elif selected_upgrade == 2:
                            # Evasion Mastery
                            player.scatter_timer.cooldown_duration = max(1.0, player.scatter_timer.cooldown_duration - 0.5)
                        elif selected_upgrade == 3:
                            # Bone Shrapnel
                            setattr(player.state, 'has_bone_shrapnel', True)
                        elif selected_upgrade == 4:
                            # Necrotic Momentum
                            current_boid_max_speed += 50.0
                            for b in [e for e in entities if isinstance(e, Boid)]:
                                b.physics.max_speed = current_boid_max_speed
                        elif selected_upgrade == 5:
                            # Plague Wizard
                            player.state.has_plague_wizard = True
                            boids = [e for e in entities if isinstance(e, Boid) and not hasattr(e, 'plague_caster') and not hasattr(e, 'ranged_attack')]
                            upgrade_count = min(10, len(boids))
                            if upgrade_count > 0:
                                for b in random.sample(boids, upgrade_count):
                                    b.plague_caster = PlagueCaster(cooldown=3.0, blast_radius=80.0, attack_range=150.0, projectile_speed=300.0)
                                    b.graphics.sprite_ref = "plague_wizard"
                                
                        # Flag the upgrade as purchased (gray-out) instead of
                        # removing it.  The shop remains open for further purchases.
                        for upg in shop_controller.available_upgrades:
                            if upg["id"] == selected_upgrade:
                                upg["is_purchased"] = True
                                break
                    elif upgrade_data:
                        AssetLoader().play_sound("ui_error")
                        print("Not enough souls!")
                            
            elif current_state == GameState.PAUSED:
                action = pause_controller.handle_event(event)
                if action == "RESUME":
                    current_state = GameState.PLAYING
                elif action == "MAIN_MENU":
                    current_state = GameState.MENU
                    if PLAYLIST: pygame.mixer.music.stop()
        bg = AssetLoader().get_background()
        if bg:
            screen.blit(bg, (0, 0))
        else:
            screen.fill(BG_COLOR)

        if current_state == GameState.PLAYING:
            current_survival_time += dt
            resource_timer += dt

            # --- Threat Level Derivation ---
            # Derived by counting how many thresholds have been exceeded.
            current_threat_level = sum(current_survival_time >= t for t in THREAT_THRESHOLDS) + 1

            # --- Victory Check (10 minutes) ---
            if current_survival_time >= VICTORY_DURATION:
                victory_souls = player.souls
                high_score = max(high_score, current_survival_time)
                current_state = GameState.VICTORY
                AssetLoader().play_sound("win")
                if PLAYLIST: pygame.mixer.music.stop()

            # --- Automatic Shop Milestone Trigger ---
            # Opens the Dark Altar at the exact start times of Threat Levels 4, 6, 8, and 10.
            # The index guard ensures each milestone fires exactly once per run.
            if next_shop_milestone_index < len(SHOP_MILESTONES):
                target_time = SHOP_MILESTONES[next_shop_milestone_index]
                
                # Pre-Shop Warning
                if not shop_warning_shown and current_survival_time >= target_time - 3.0:
                    shop_warning_shown = True
                    from entities.particles import FloatingText
                    warning_text = FloatingText(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 4, "The Dark Altar Approaches...", color=(255, 100, 100), duration=2.5)
                    entities.append(warning_text)
                    
                if current_survival_time >= target_time:
                    next_shop_milestone_index += 1
                    shop_warning_shown = False
                    current_state = GameState.SHOP
                    # Reset is_purchased flags for upgrades still in the pool
                    # so each visit starts with a clean visual state.
                    shop_controller.refresh_upgrades()
                    shop_timer = 0.0
                    player.souls += 20  # Passive stipend as per Functional Spec

            # --- Grave Spawn Rate (tightens at Threat Level 6+) ---
            grave_rate = _GRAVE_RATE_EARLY if current_threat_level < 6 else _GRAVE_RATE_LATE
            if resource_timer > grave_rate:
                entities.append(Resource(random.uniform(50, SCREEN_WIDTH - 50), random.uniform(50, SCREEN_HEIGHT - 50)))
                resource_timer = 0.0

            # Systems update logic — pass threat_level into the systems that need it
            for system in systems:
                if system is spawner_system or system is behavior_system:
                    system.update(entities, dt, threat_level=current_threat_level)
                else:
                    system.update(entities, dt)

            # Cleanup deleted entities
            entities = [e for e in entities if not getattr(e, 'marked_for_deletion', False)]

            # Check for Game Over condition
            active_boids = [e for e in entities if isinstance(e, Boid)]
            if len(active_boids) == 0:
                high_score = max(high_score, current_survival_time)
                current_state = GameState.GAME_OVER
                AssetLoader().play_sound("lose")
                if PLAYLIST: pygame.mixer.music.stop()

            # --- HUD ---
            hud_controller.draw(screen, player, len(active_boids), current_survival_time, current_threat_level)
            
        elif current_state == GameState.SHOP:
            render_system.update(entities, 0)
            shop_controller.draw(screen, player.souls)

        elif current_state == GameState.PAUSED:
            render_system.update(entities, 0)
            pause_controller.draw(screen)

        elif current_state == GameState.MENU:
            menu_controller.draw_main_menu(screen, high_score)

        elif current_state == GameState.GAME_OVER:
            menu_controller.draw_game_over(screen, current_survival_time, high_score)

        elif current_state == GameState.VICTORY:
            menu_controller.draw_victory(screen, current_survival_time, victory_souls)
        
        pygame.display.flip()
        
        # Required for pygbag / async web compatibility
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
