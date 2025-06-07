import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Constants - Format vertical TikTok
SCREEN_WIDTH = 405  # 9:16 aspect ratio (405x720)
SCREEN_HEIGHT = 720
WORLD_HEIGHT = 4000  # Course très longue
FPS = 60
GRAVITY = 0.4
FRICTION = 0.96
BOUNCE_DAMPING = 0.7
MAX_SPEED = 5

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (173, 216, 230)

# Sample TikTok followers
SAMPLE_FOLLOWERS = [
    "user123", "dancequeen", "tiktoker_pro", "funny_guy", "music_lover",
    "art_creator", "foodie_life", "travel_addict", "gamer_girl", "fashion_icon",
    "comedy_king", "pet_lover", "sports_fan", "bookworm", "tech_geek",
    "nature_lover", "fitness_guru", "movie_buff", "photographer", "singer_star",
    "vlogger", "meme_lord", "DIY_queen", "workout_king", "chef_master"
]

class Marble:
    def __init__(self, x, y, follower_name, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-0.5, 0.5)
        self.vy = 0
        self.radius = 10
        self.follower_name = follower_name
        self.color = color
        self.finished = False
        self.finish_time = None
        self.position_rank = None
        
    def update(self, obstacles, other_marbles):
        if self.finished:
            return
            
        # Apply gravity
        self.vy += GRAVITY
        
        # Apply friction
        self.vx *= FRICTION
        
        # Limit velocities
        if abs(self.vx) > MAX_SPEED:
            self.vx = MAX_SPEED if self.vx > 0 else -MAX_SPEED
        if abs(self.vy) > MAX_SPEED:
            self.vy = MAX_SPEED if self.vy > 0 else -MAX_SPEED
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off screen edges
        if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
            self.vx *= -BOUNCE_DAMPING
            self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        
        # Check collision with other marbles
        for other_marble in other_marbles:
            if other_marble != self and not other_marble.finished:
                if self.check_marble_collision(other_marble):
                    self.handle_marble_collision(other_marble)
        
        # Check collision with obstacles
        for obstacle in obstacles:
            if self.check_collision(obstacle):
                self.handle_collision(obstacle)
        
        # Check if reached bottom (finish line)
        if self.y > WORLD_HEIGHT - 100:
            if not self.finished:
                self.finished = True
                self.finish_time = time.time()
    
    def check_marble_collision(self, other_marble):
        dx = self.x - other_marble.x
        dy = self.y - other_marble.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < (self.radius + other_marble.radius)
    
    def handle_marble_collision(self, other_marble):
        dx = self.x - other_marble.x
        dy = self.y - other_marble.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            dx, dy = 1, 0
            distance = 1
        
        nx = dx / distance
        ny = dy / distance
        
        # Separate marbles
        overlap = (self.radius + other_marble.radius) - distance
        if overlap > 0:
            self.x += nx * overlap * 0.5
            self.y += ny * overlap * 0.5
            other_marble.x -= nx * overlap * 0.5
            other_marble.y -= ny * overlap * 0.5
        
        # Calculate collision response
        dvx = self.vx - other_marble.vx
        dvy = self.vy - other_marble.vy
        dvn = dvx * nx + dvy * ny
        
        if dvn > 0:
            return
        
        impulse = 2 * dvn / 2
        
        self.vx -= impulse * nx * 0.8
        self.vy -= impulse * ny * 0.8
        other_marble.vx += impulse * nx * 0.8
        other_marble.vy += impulse * ny * 0.8
    
    def check_collision(self, obstacle):
        closest_x = max(obstacle['x'], min(self.x, obstacle['x'] + obstacle['width']))
        closest_y = max(obstacle['y'], min(self.y, obstacle['y'] + obstacle['height']))
        
        distance = math.sqrt((self.x - closest_x)**2 + (self.y - closest_y)**2)
        return distance < self.radius
    
    def handle_collision(self, obstacle):
        center_x = obstacle['x'] + obstacle['width'] / 2
        center_y = obstacle['y'] + obstacle['height'] / 2
        
        dx = self.x - center_x
        dy = self.y - center_y
        
        if abs(dx) > abs(dy):
            self.vx *= -BOUNCE_DAMPING
            if dx > 0:
                self.x = obstacle['x'] + obstacle['width'] + self.radius
            else:
                self.x = obstacle['x'] - self.radius
        else:
            self.vy *= -BOUNCE_DAMPING
            if dy > 0:
                self.y = obstacle['y'] + obstacle['height'] + self.radius
            else:
                self.y = obstacle['y'] - self.radius
        
        # Add randomness
        self.vx += random.uniform(-1, 1)
    
    def draw(self, screen, font, camera_y):
        screen_y = self.y - camera_y
        
        # Only draw if marble is visible on screen
        if -50 <= screen_y <= SCREEN_HEIGHT + 50:
            pygame.draw.circle(screen, self.color, (int(self.x), int(screen_y)), self.radius)
            pygame.draw.circle(screen, BLACK, (int(self.x), int(screen_y)), self.radius, 2)
            
            # Draw follower name
            if self.radius > 8:  # Only show name if marble is big enough
                text = font.render(self.follower_name[:6], True, BLACK)
                text_rect = text.get_rect(center=(self.x, screen_y - self.radius - 15))
                screen.blit(text, text_rect)

class Camera:
    def __init__(self):
        self.y = 0
        self.target_y = 0
        self.smooth_factor = 0.1
    
    def update(self, marbles):
        # Find the marble that's furthest down (leading the race)
        active_marbles = [m for m in marbles if not m.finished]
        if active_marbles:
            leading_marble = max(active_marbles, key=lambda m: m.y)
            # Center camera on leading marble with some offset
            self.target_y = leading_marble.y - SCREEN_HEIGHT // 2
        else:
            # If all marbles finished, focus on finish line
            finished_marbles = [m for m in marbles if m.finished]
            if finished_marbles:
                self.target_y = WORLD_HEIGHT - SCREEN_HEIGHT + 50
        
        # Smooth camera movement
        self.y += (self.target_y - self.y) * self.smooth_factor
        
        # Keep camera within bounds
        self.y = max(0, min(WORLD_HEIGHT - SCREEN_HEIGHT, self.y))

class MarbleRaceGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TikTok Followers Marble Race - Vertical Format")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 20)
        self.big_font = pygame.font.Font(None, 32)
        
        # Camera for following marbles
        self.camera = Camera()
        
        # Create marbles
        self.marbles = []
        self.create_marbles()
        
        # Create long vertical maze
        self.obstacles = self.create_long_maze()
        
        # Game state
        self.start_time = time.time()
        self.race_finished = False
        self.winners = []
        
    def create_marbles(self):
        colors = [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE, PINK, CYAN]
        
        followers = SAMPLE_FOLLOWERS[:12]  # 12 marbles for better performance
        
        for i, follower in enumerate(followers):
            x = 50 + (i % 6) * 50  # 6 marbles per row
            y = 50 + (i // 6) * 30
            color = colors[i % len(colors)]
            marble = Marble(x, y, follower, color)
            self.marbles.append(marble)
    
    def create_long_maze(self):
        obstacles = []
        
        # Create a long vertical maze with multiple sections
        current_y = 200
        
        while current_y < WORLD_HEIGHT - 200:
            # Random platform sections
            if random.random() < 0.7:
                # Left or right platform
                if random.random() < 0.5:
                    # Left platform
                    width = random.randint(100, 200)
                    obstacles.append({
                        'x': 20,
                        'y': current_y,
                        'width': width,
                        'height': 15
                    })
                else:
                    # Right platform
                    width = random.randint(100, 200)
                    obstacles.append({
                        'x': SCREEN_WIDTH - 20 - width,
                        'y': current_y,
                        'width': width,
                        'height': 15
                    })
            
            # Add some center obstacles
            if random.random() < 0.4:
                width = random.randint(60, 120)
                obstacles.append({
                    'x': SCREEN_WIDTH // 2 - width // 2 + random.randint(-30, 30),
                    'y': current_y + 50,
                    'width': width,
                    'height': 15
                })
            
            # Add funnel sections occasionally
            if random.random() < 0.3:
                # Funnel walls
                obstacles.append({
                    'x': 80,
                    'y': current_y + 80,
                    'width': 15,
                    'height': 60
                })
                obstacles.append({
                    'x': SCREEN_WIDTH - 95,
                    'y': current_y + 80,
                    'width': 15,
                    'height': 60
                })
            
            # Add zigzag pattern
            if random.random() < 0.5:
                for i in range(3):
                    side = i % 2
                    if side == 0:
                        obstacles.append({
                            'x': 30,
                            'y': current_y + 100 + i * 40,
                            'width': 150,
                            'height': 12
                        })
                    else:
                        obstacles.append({
                            'x': SCREEN_WIDTH - 180,
                            'y': current_y + 100 + i * 40,
                            'width': 150,
                            'height': 12
                        })
            
            current_y += random.randint(150, 250)
        
        return obstacles
    
    def update(self):
        # Update marbles
        for marble in self.marbles:
            marble.update(self.obstacles, self.marbles)
        
        # Update camera
        self.camera.update(self.marbles)
        
        # Check race completion
        finished_marbles = [m for m in self.marbles if m.finished]
        if finished_marbles and not self.race_finished:
            finished_marbles.sort(key=lambda m: m.finish_time)
            for i, marble in enumerate(finished_marbles):
                if marble.position_rank is None:
                    marble.position_rank = i + 1
            
            if len(finished_marbles) >= 3 or len(finished_marbles) == len(self.marbles):
                self.race_finished = True
                self.winners = finished_marbles[:3]
    
    def draw(self):
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(135 + (200 - 135) * color_ratio)
            g = int(206 + (220 - 206) * color_ratio)
            b = int(235 + (255 - 235) * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # Draw obstacles (maze) - only visible ones
        for obstacle in self.obstacles:
            screen_y = obstacle['y'] - self.camera.y
            if -50 <= screen_y <= SCREEN_HEIGHT + 50:
                pygame.draw.rect(self.screen, DARK_GRAY, 
                               (obstacle['x'], screen_y, obstacle['width'], obstacle['height']))
                pygame.draw.rect(self.screen, BLACK, 
                               (obstacle['x'], screen_y, obstacle['width'], obstacle['height']), 2)
        
        # Draw finish line
        finish_screen_y = WORLD_HEIGHT - 100 - self.camera.y
        if -50 <= finish_screen_y <= SCREEN_HEIGHT + 50:
            pygame.draw.rect(self.screen, GREEN, (0, finish_screen_y, SCREEN_WIDTH, 100))
            finish_text = self.font.render("FINISH", True, BLACK)
            finish_rect = finish_text.get_rect(center=(SCREEN_WIDTH // 2, finish_screen_y + 50))
            self.screen.blit(finish_text, finish_rect)
        
        # Draw marbles
        for marble in self.marbles:
            marble.draw(self.screen, self.font, self.camera.y)
        
        # Draw race info overlay
        elapsed_time = time.time() - self.start_time
        time_text = self.font.render(f"Time: {elapsed_time:.1f}s", True, WHITE)
        time_bg = pygame.Rect(5, 5, time_text.get_width() + 10, time_text.get_height() + 5)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), time_bg)
        self.screen.blit(time_text, (10, 8))
        
        # Draw mini leaderboard
        finished_marbles = [m for m in self.marbles if m.finished and m.position_rank]
        if finished_marbles:
            finished_marbles.sort(key=lambda m: m.position_rank)
            for i, marble in enumerate(finished_marbles[:3]):
                rank_text = self.font.render(f"{marble.position_rank}. {marble.follower_name[:8]}", True, WHITE)
                rank_bg = pygame.Rect(5, 35 + i * 25, rank_text.get_width() + 10, rank_text.get_height() + 5)
                pygame.draw.rect(self.screen, (0, 0, 0, 128), rank_bg)
                self.screen.blit(rank_text, (10, 38 + i * 25))
        
        # Draw winner announcement
        if self.race_finished and self.winners:
            winner_text = self.big_font.render(f"WINNER: {self.winners[0].follower_name}!", True, YELLOW)
            winner_bg = pygame.Rect(SCREEN_WIDTH // 2 - winner_text.get_width() // 2 - 10, 
                                  SCREEN_HEIGHT // 2 - 20, 
                                  winner_text.get_width() + 20, 
                                  winner_text.get_height() + 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 200), winner_bg)
            pygame.draw.rect(self.screen, YELLOW, winner_bg, 3)
            self.screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - 15))
        
        # Draw progress indicator
        if not self.race_finished:
            active_marbles = [m for m in self.marbles if not m.finished]
            if active_marbles:
                leading_marble = max(active_marbles, key=lambda m: m.y)
                progress = min(leading_marble.y / WORLD_HEIGHT, 1.0)
                
                # Progress bar
                bar_width = SCREEN_WIDTH - 20
                bar_height = 8
                bar_x = 10
                bar_y = SCREEN_HEIGHT - 30
                
                pygame.draw.rect(self.screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, bar_width * progress, bar_height))
                
                progress_text = self.font.render(f"Progress: {progress*100:.1f}%", True, WHITE)
                progress_bg = pygame.Rect(bar_x, bar_y - 20, progress_text.get_width() + 10, progress_text.get_height() + 5)
                pygame.draw.rect(self.screen, (0, 0, 0, 128), progress_bg)
                self.screen.blit(progress_text, (bar_x + 5, bar_y - 17))
        
        # Instructions
        if elapsed_time < 5:  # Show for first 5 seconds
            instruction_text = self.font.render("TikTok Marble Race!", True, WHITE)
            inst_bg = pygame.Rect(SCREEN_WIDTH // 2 - instruction_text.get_width() // 2 - 10, 
                                SCREEN_HEIGHT - 80, 
                                instruction_text.get_width() + 20, 
                                instruction_text.get_height() + 10)
            pygame.draw.rect(self.screen, (0, 0, 0, 150), inst_bg)
            self.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, SCREEN_HEIGHT - 75))
        
        pygame.display.flip()
    
    def restart_race(self):
        self.__init__()
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.restart_race()
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    print("TikTok Followers Marble Race Game - Vertical Format")
    print("="*50)
    print("Format: 9:16 vertical (405x720) - Perfect for TikTok!")
    print("Features:")
    print("- Long vertical race course")
    print("- Camera follows leading marbles")
    print("- Smooth scrolling")
    print("- Progress indicator")
    print("- Real-time leaderboard")
    print("\nControls:")
    print("- R: Restart race")
    print("- ESC: Quit game")
    print("="*50)
    
    game = MarbleRaceGame()
    game.run()