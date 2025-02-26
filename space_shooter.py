import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Set up the screen
screen_width = 1024
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()

# Set up the player
player = pygame.Rect(482, 354, 60, 60)  # Centered at (512, 384) with 60x60 size
angle = 0.0  # Ship's rotation angle in degrees (0 = up)
ship_local_points = [(0, -30), (-20, 20), (20, 20)]  # Triangle shape relative to center

# Lists for game objects
enemies = []
bullets = []

# Game variables
spawn_timer = 0
shoot_cooldown = 0
score = 0
font = pygame.font.Font(None, 36)
enemy_speed = 3.0
rotation_speed = 5.0
thruster_speed = 5.0
bullet_speed = 10.0

# On-screen buttons for touch input
rotate_left_button = pygame.Rect(10, 700, 100, 50)
rotate_right_button = pygame.Rect(120, 700, 100, 50)
thrusters_button = pygame.Rect(230, 700, 100, 50)
shoot_button = pygame.Rect(800, 700, 100, 50)

# Input flags for continuous actions
rotating_left = False
rotating_right = False
thrusters_on = False

# Create a starry background
stars = [(random.randint(0, screen_width), random.randint(0, screen_height)) for _ in range(100)]

# Main game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if rotate_left_button.collidepoint(pos):
                rotating_left = True
            elif rotate_right_button.collidepoint(pos):
                rotating_right = True
            elif thrusters_button.collidepoint(pos):
                thrusters_on = True
            elif shoot_button.collidepoint(pos) and shoot_cooldown <= 0:
                theta = math.radians(angle)
                bullet_vx = bullet_speed * math.sin(theta)
                bullet_vy = -bullet_speed * math.cos(theta)
                bullets.append([player.centerx, player.centery, bullet_vx, bullet_vy])
                shoot_cooldown = 30
        elif event.type == pygame.MOUSEBUTTONUP:
            pos = event.pos
            if rotate_left_button.collidepoint(pos):
                rotating_left = False
            elif rotate_right_button.collidepoint(pos):
                rotating_right = False
            elif thrusters_button.collidepoint(pos):
                thrusters_on = False

    # Keyboard input
    keys = pygame.key.get_pressed()
    
    # Rotation
    if keys[pygame.K_LEFT] or rotating_left:
        angle -= rotation_speed
    if keys[pygame.K_RIGHT] or rotating_right:
        angle += rotation_speed
    angle %= 360

    # Thrusters
    if keys[pygame.K_w] or thrusters_on:
        theta = math.radians(angle)
        dx = thruster_speed * math.sin(theta)
        dy = -thruster_speed * math.cos(theta)
        player.x += int(dx)
        player.y += int(dy)

    # Shooting
    if keys[pygame.K_SPACE] and shoot_cooldown <= 0:
        theta = math.radians(angle)
        bullet_vx = bullet_speed * math.sin(theta)
        bullet_vy = -bullet_speed * math.cos(theta)
        bullets.append([player.centerx, player.centery, bullet_vx, bullet_vy])
        shoot_cooldown = 30

    # Clamp player position to screen
    player.x = max(0, min(player.x, screen_width - player.width))
    player.y = max(0, min(player.y, screen_height - player.height))

    # Update shoot cooldown
    shoot_cooldown = max(0, shoot_cooldown - 1)

    # Spawn enemies
    spawn_timer += 1
    if spawn_timer >= 60:
        spawn_timer = 0
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            x = random.uniform(0, screen_width)
            y = -60.0
        elif side == 'bottom':
            x = random.uniform(0, screen_width)
            y = screen_height
        elif side == 'left':
            x = -60.0
            y = random.uniform(0, screen_height)
        else:
            x = screen_width
            y = random.uniform(0, screen_height)
        target_x = player.centerx
        target_y = player.centery
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        vx = enemy_speed * dx / distance if distance > 0 else 0
        vy = enemy_speed * dy / distance if distance > 0 else 0
        enemies.append([x, y, vx, vy])

    # Update bullets
    for bullet in bullets:
        bullet[0] += bullet[2]
        bullet[1] += bullet[3]

    # Update enemies
    for enemy in enemies:
        enemy[0] += enemy[2]
        enemy[1] += enemy[3]

    # Remove off-screen objects
    bullets = [b for b in bullets if -10 < b[0] < screen_width + 10 and -10 < b[1] < screen_height + 10]
    enemies = [e for e in enemies if -60 < e[0] < screen_width + 60 and -60 < e[1] < screen_height + 60]

    # Check collisions
    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(int(bullet[0] - 5), int(bullet[1] - 5), 10, 10)
        for enemy in enemies[:]:
            enemy_rect = pygame.Rect(int(enemy[0]), int(enemy[1]), 60, 60)
            if bullet_rect.colliderect(enemy_rect):
                bullets.remove(bullet)
                enemies.remove(enemy)
                score += 1
                break

    # Draw everything
    screen.fill((0, 0, 0))  # Black background

    # Draw stars
    for star in stars:
        pygame.draw.circle(screen, (255, 255, 255), star, 2)

    # Draw ship
    theta = math.radians(angle)
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    rotated_points = []
    for x, y in ship_local_points:
        rot_x = x * cos_theta - y * sin_theta
        rot_y = x * sin_theta + y * cos_theta
        screen_x = player.centerx + rot_x
        screen_y = player.centery + rot_y
        rotated_points.append((screen_x, screen_y))
    pygame.draw.polygon(screen, (0, 0, 255), rotated_points)  # Blue ship

    # Draw enemies
    for enemy in enemies:
        pygame.draw.rect(screen, (255, 0, 0), (int(enemy[0]), int(enemy[1]), 60, 60))

    # Draw bullets
    for bullet in bullets:
        pygame.draw.circle(screen, (255, 255, 0), (int(bullet[0]), int(bullet[1])), 5)

    # Draw on-screen buttons with labels
    pygame.draw.rect(screen, (100, 100, 100), rotate_left_button)
    pygame.draw.rect(screen, (100, 100, 100), rotate_right_button)
    pygame.draw.rect(screen, (100, 100, 100), thrusters_button)
    pygame.draw.rect(screen, (100, 100, 100), shoot_button)
    small_font = pygame.font.Font(None, 24)
    screen.blit(small_font.render("Left", True, (255, 255, 255)), (30, 715))
    screen.blit(small_font.render("Right", True, (255, 255, 255)), (135, 715))
    screen.blit(small_font.render("Thrust", True, (255, 255, 255)), (245, 715))
    screen.blit(small_font.render("Shoot", True, (255, 255, 255)), (820, 715))

    # Draw score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    # Update display
    pygame.display.flip()
    clock.tick(60)