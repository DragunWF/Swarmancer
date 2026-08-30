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
from utils.state import GameState
from ui.shop_controller import ShopController
from components.combat import RangedAttack
from systems.combat_system import CombatSystem

async def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Swarmancer")
    clock = pygame.time.Clock()
    
    # Initialize Entities
    entities = []
    player_x = SCREEN_WIDTH / 2
    player_y = SCREEN_HEIGHT / 2
    player = Player(player_x, player_y)
    entities.append(player)
    
    # Spawn 50 Boids around the initial player position
    for _ in range(50):
        boid = Boid(player_x + random.uniform(-60, 60), player_y + random.uniform(-60, 60))
        entities.append(boid)
        
    def on_resource_collected(x, y):
        # Spawn 3 new boids slightly offset from the grave
        for _ in range(3):
            entities.append(Boid(x + random.uniform(-20, 20), y + random.uniform(-20, 20)))

    # Initialize Systems
    behavior_system = BehaviorSystem()
    movement_system = MovementSystem()
    collision_system = CollisionSystem(on_resource_collected=on_resource_collected)
    render_system = RenderSystem()
    spawner_system = SpawnerSystem(SCREEN_WIDTH, SCREEN_HEIGHT)
    
    combat_system = CombatSystem()
    
    systems = [spawner_system, behavior_system, combat_system, movement_system, collision_system, render_system]
    
    resource_timer = 0.0
    shop_timer = 0.0
    current_state = GameState.PLAYING
    shop_controller = ShopController(SCREEN_WIDTH, SCREEN_HEIGHT)
    hud_font = pygame.font.SysFont(None, 36)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if current_state == GameState.SHOP:
                selected_upgrade = shop_controller.handle_event(event)
                if selected_upgrade is not None:
                    if selected_upgrade == 0:
                        if player.souls >= 10:
                            player.souls -= 10
                            
                            # Apply Archer Upgrade
                            boids = [e for e in entities if isinstance(e, Boid) and not hasattr(e, 'ranged_attack')]
                            upgrade_count = min(10, len(boids))
                            if upgrade_count > 0:
                                for b in random.sample(boids, upgrade_count):
                                    b.ranged_attack = RangedAttack(fire_rate=1.0, attack_range=150.0, projectile_speed=300.0)
                                    b.graphics.color = (100, 100, 255) # Tint blue
                                    
                            current_state = GameState.PLAYING
                        else:
                            print("Not enough souls!")
                    else:
                        if player.souls >= 10:
                            player.souls -= 10
                            current_state = GameState.PLAYING
                        else:
                            print("Not enough souls!")

        screen.fill(BG_COLOR)

        if current_state == GameState.PLAYING:
            resource_timer += dt
            shop_timer += dt
            
            if resource_timer > 3.0: # Spawn a grave every 3 seconds
                entities.append(Resource(random.uniform(50, SCREEN_WIDTH - 50), random.uniform(50, SCREEN_HEIGHT - 50)))
                resource_timer = 0.0
                
            if shop_timer > 30.0: # Enter shop every 30 seconds
                current_state = GameState.SHOP
                shop_timer = 0.0
                player.souls += 20 # Passive stipend as per Functional Spec

            # Systems update logic
            for system in systems:
                system.update(entities, dt)
                
            # Cleanup deleted entities
            entities = [e for e in entities if not getattr(e, 'marked_for_deletion', False)]
            
            # Draw HUD
            time_until_shop = max(0.0, 30.0 - shop_timer)
            timer_text = hud_font.render(f"Next Shop: {time_until_shop:.1f}s", True, (255, 255, 255))
            screen.blit(timer_text, (SCREEN_WIDTH // 2 - timer_text.get_width() // 2, 10))
            
            souls_text = hud_font.render(f"Souls: {player.souls}", True, (255, 215, 0))
            screen.blit(souls_text, (SCREEN_WIDTH // 2 - souls_text.get_width() // 2, 45))
            
        elif current_state == GameState.SHOP:
            render_system.update(entities, 0)
            shop_controller.draw(screen, player.souls)
        
        pygame.display.flip()
        
        # Required for pygbag / async web compatibility
        await asyncio.sleep(0)

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
