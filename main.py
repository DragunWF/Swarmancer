import asyncio
import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, BG_COLOR
from entities.player import Player
from entities.boid import Boid
from entities.powerups import Resource
from systems.behavior_system import BehaviorSystem
from systems.movement_system import MovementSystem
from systems.render_system import RenderSystem
from systems.collision_system import CollisionSystem
from systems.spawner_system import SpawnerSystem
from systems.particle_system import ParticleSystem
from utils.state import GameState
from ui.shop_controller import ShopController
from ui.menu_controller import MenuController
from ui.pause_controller import PauseController
from components.combat import RangedAttack
from systems.combat_system import CombatSystem

async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Swarmancer")
    clock = pygame.time.Clock()
    
    entities = []
    
    # Session state
    high_score = 0.0
    current_survival_time = 0.0
    player = None
    current_boid_max_speed = 350.0
    
    # External closures needed for systems
    def on_resource_collected(resource):
        # Spawn boids slightly offset from the grave based on yield amount
        has_archers = player and getattr(player.state, 'has_skeletal_archers', False)
        for i in range(resource.yield_amount):
            boid = Boid(resource.transform.x + random.uniform(-20, 20), resource.transform.y + random.uniform(-20, 20), max_speed=current_boid_max_speed)
            if has_archers and (i == 0 or random.random() < 0.25):
                boid.ranged_attack = RangedAttack(fire_rate=1.0, attack_range=150.0, projectile_speed=300.0)
                boid.graphics.color = (100, 100, 255) # Tint blue
            entities.append(boid)

    def on_currency_collected(amount):
        if player:
            player.souls += amount

    def on_entity_spawned(entity):
        entities.append(entity)
        
    # Initialize Systems
    behavior_system = BehaviorSystem()
    movement_system = MovementSystem()
    collision_system = CollisionSystem(
        on_resource_collected=on_resource_collected,
        on_currency_collected=on_currency_collected,
        on_entity_spawned=on_entity_spawned
    )
    particle_system = ParticleSystem()
    render_system = RenderSystem()
    spawner_system = SpawnerSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
    combat_system = CombatSystem()
    
    systems = [spawner_system, behavior_system, combat_system, movement_system, collision_system, particle_system, render_system]
    
    # Controllers
    shop_controller = ShopController(SCREEN_WIDTH, SCREEN_HEIGHT)
    menu_controller = MenuController(SCREEN_WIDTH, SCREEN_HEIGHT)
    pause_controller = PauseController(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    current_state = GameState.MENU
    hud_font = pygame.font.SysFont(None, 36)
    
    resource_timer = 0.0
    shop_timer = 0.0

    def reset_game():
        nonlocal player, resource_timer, shop_timer, current_survival_time, current_boid_max_speed
        entities.clear()
        
        player_x = SCREEN_WIDTH / 2
        player_y = SCREEN_HEIGHT / 2
        player = Player(player_x, player_y)
        entities.append(player)
        
        current_boid_max_speed = 350.0
        Resource.yield_amount = 3
        shop_controller.available_upgrades = shop_controller.all_upgrades.copy()
        shop_controller.refresh_upgrades()

        for _ in range(50):
            boid = Boid(player_x + random.uniform(-60, 60), player_y + random.uniform(-60, 60), max_speed=current_boid_max_speed)
            entities.append(boid)
            
        resource_timer = 0.0
        shop_timer = 0.0
        current_survival_time = 0.0

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if current_state == GameState.PLAYING and event.type == pygame.KEYDOWN and event.key == pygame.K_p:
                current_state = GameState.PAUSED
                continue
                
            if current_state in (GameState.MENU, GameState.GAME_OVER):
                action = menu_controller.handle_event(event, current_state)
                if action == "PLAY":
                    reset_game()
                    current_state = GameState.PLAYING
                elif action == "MAIN_MENU":
                    current_state = GameState.MENU
                    
            elif current_state == GameState.SHOP:
                selected_upgrade = shop_controller.handle_event(event)
                if selected_upgrade == "CONTINUE":
                    current_state = GameState.PLAYING
                elif selected_upgrade is not None:
                    upgrade_data = next((u for u in shop_controller.all_upgrades if u["id"] == selected_upgrade), None)
                    if upgrade_data and player.souls >= upgrade_data["cost"]:
                        player.souls -= upgrade_data["cost"]
                        
                        if selected_upgrade == 0:
                            # Apply Archer Upgrade
                            player.state.has_skeletal_archers = True
                            boids = [e for e in entities if isinstance(e, Boid) and not hasattr(e, 'ranged_attack')]
                            upgrade_count = min(10, len(boids))
                            if upgrade_count > 0:
                                for b in random.sample(boids, upgrade_count):
                                    b.ranged_attack = RangedAttack(fire_rate=1.0, attack_range=150.0, projectile_speed=300.0)
                                    b.graphics.color = (100, 100, 255) # Tint blue
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
                                
                        shop_controller.remove_upgrade(selected_upgrade)
                        current_state = GameState.PLAYING
                    elif upgrade_data:
                        print("Not enough souls!")
                            
            elif current_state == GameState.PAUSED:
                action = pause_controller.handle_event(event)
                if action == "RESUME":
                    current_state = GameState.PLAYING
                elif action == "MAIN_MENU":
                    current_state = GameState.MENU

        screen.fill(BG_COLOR)

        if current_state == GameState.PLAYING:
            current_survival_time += dt
            resource_timer += dt
            shop_timer += dt
            
            if resource_timer > 3.0: # Spawn a grave every 3 seconds
                entities.append(Resource(random.uniform(50, SCREEN_WIDTH - 50), random.uniform(50, SCREEN_HEIGHT - 50)))
                resource_timer = 0.0
                
            if shop_timer > 30.0: # Enter shop every 30 seconds
                current_state = GameState.SHOP
                shop_controller.refresh_upgrades()
                shop_timer = 0.0
                player.souls += 20 # Passive stipend as per Functional Spec

            # Systems update logic
            for system in systems:
                system.update(entities, dt)
                
            # Cleanup deleted entities
            entities = [e for e in entities if not getattr(e, 'marked_for_deletion', False)]
            
            # Check for Game Over condition
            active_boids = [e for e in entities if isinstance(e, Boid)]
            if len(active_boids) == 0:
                high_score = max(high_score, current_survival_time)
                current_state = GameState.GAME_OVER
            
            # Draw HUD
            time_until_shop = max(0.0, 30.0 - shop_timer)
            timer_text = hud_font.render(f"Next Shop: {time_until_shop:.1f}s", True, (255, 255, 255))
            screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 10))
            
            souls_text = hud_font.render(f"Souls: {player.souls}", True, (255, 215, 0))
            screen.blit(souls_text, (SCREEN_WIDTH // 2 - souls_text.get_width() // 2, 45))
            
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
        
        pygame.display.flip()
        
        # Required for pygbag / async web compatibility
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
