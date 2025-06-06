import pygame
import random
import math
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
GRAVITY = 0.3
FRICTION = 0.95
BOUNCE_DAMPING = 0.7

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

# Sample TikTok followers (replace with real data if available)
SAMPLE_FOLLOWERS = [
    "user123", "dancequeen", "tiktoker_pro", "funny_guy", "music_lover",
    "art_creator", "foodie_life", "travel_addict", "gamer_girl", "fashion_icon",
    "comedy_king", "pet_lover", "sports_fan", "bookworm", "tech_geek",
    "nature_lover", "fitness_guru", "movie_buff", "photographer", "singer_star"
]

class Marble:
    def __init__(self, x, y, follower_name, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = 0
        self.radius = 8
        self.follower_name = follower_name
        self.color = color
        self.finished = False
        self.finish_time = None
        self.position_rank = None
        
    def update(self, obstacles):
        if self.finished:
            return
            
        # Apply gravity
        self.vy += GRAVITY
        
        # Apply friction
        self.vx *= FRICTION
        
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Bounce off screen edges
        if self.x - self.radius <= 0 or self.x + self.radius >= SCREEN_WIDTH:
            self.vx *= -BOUNCE_DAMPING
            self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        
        # Check collision with obstacles
        for obstacle in obstacles:
            if self.check_collision(obstacle):
                self.handle_collision(obstacle)
        
        # Check if reached bottom (finish line)
        if self.y > SCREEN_HEIGHT - 50:
            if not self.finished:
                self.finished = True
                self.finish_time = time.time()
    
    def check_collision(self, obstacle):
        # Simple rectangle-circle collision
        closest_x = max(obstacle['x'], min(self.x, obstacle['x'] + obstacle['width']))
        closest_y = max(obstacle['y'], min(self.y, obstacle['y'] + obstacle['height']))
        
        distance = math.sqrt((self.x - closest_x)**2 + (self.y - closest_y)**2)
        return distance < self.radius
    
    def handle_collision(self, obstacle):
        # Simple bounce off obstacles
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
        
        # Add some randomness to make it more interesting
        self.vx += random.uniform(-0.5, 0.5)
    
    def draw(self, screen, font):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        # Draw follower name near marble
        text = font.render(self.follower_name[:8], True, BLACK)
        screen.blit(text, (self.x - 30, self.y - 25))

class MarbleRaceGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("TikTok Followers Marble Race")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        
        # Create marbles for followers
        self.marbles = []
        self.create_marbles()
        
        # Create maze obstacles
        self.obstacles = self.create_maze()
        
        # Game state
        self.start_time = time.time()
        self.race_finished = False
        self.winners = []
        
    def create_marbles(self):
        colors = [RED, BLUE, GREEN, YELLOW, PURPLE, ORANGE, PINK, CYAN]
        
        # Use sample followers (replace with real TikTok data if available)
        followers = SAMPLE_FOLLOWERS[:15]  # Limit to 15 for performance
        
        for i, follower in enumerate(followers):
            x = 100 + (i % 5) * 40  # Spread marbles across the top
            y = 50 + (i // 5) * 20
            color = colors[i % len(colors)]
            marble = Marble(x, y, follower, color)
            self.marbles.append(marble)
    
    def create_maze(self):
        obstacles = []
        
        # Create a series of platforms and barriers to form a maze
        # Left and right barriers
        for y in range(150, SCREEN_HEIGHT - 100, 120):
            if random.random() < 0.8:  # 80% chance to place obstacle
                side = random.choice(['left', 'right'])
                if side == 'left':
                    obstacles.append({
                        'x': 50,
                        'y': y,
                        'width': random.randint(150, 300),
                        'height': 20
                    })
                else:
                    width = random.randint(150, 300)
                    obstacles.append({
                        'x': SCREEN_WIDTH - 50 - width,
                        'y': y,
                        'width': width,
                        'height': 20
                    })
        
        # Add some central obstacles
        for y in range(200, SCREEN_HEIGHT - 100, 150):
            if random.random() < 0.6:
                obstacles.append({
                    'x': SCREEN_WIDTH // 2 - 100 + random.randint(-50, 50),
                    'y': y,
                    'width': random.randint(100, 200),
                    'height': 20
                })
        
        # Add some funnel shapes
        for y in range(300, SCREEN_HEIGHT - 100, 200):
            # Left funnel wall
            obstacles.append({
                'x': 200,
                'y': y,
                'width': 20,
                'height': 80
            })
            # Right funnel wall
            obstacles.append({
                'x': SCREEN_WIDTH - 220,
                'y': y,
                'width': 20,
                'height': 80
            })
        
        return obstacles
    
    def update(self):
        for marble in self.marbles:
            marble.update(self.obstacles)
        
        # Check for race completion
        finished_marbles = [m for m in self.marbles if m.finished]
        if finished_marbles and not self.race_finished:
            # Sort by finish time and assign ranks
            finished_marbles.sort(key=lambda m: m.finish_time)
            for i, marble in enumerate(finished_marbles):
                if marble.position_rank is None:
                    marble.position_rank = i + 1
            
            # Check if race is complete (top 5 finished or all finished)
            if len(finished_marbles) >= 5 or len(finished_marbles) == len(self.marbles):
                self.race_finished = True
                self.winners = finished_marbles[:5]
    
    def draw(self):
        self.screen.fill(WHITE)
        
        # Draw obstacles (maze)
        for obstacle in self.obstacles:
            pygame.draw.rect(self.screen, DARK_GRAY, 
                           (obstacle['x'], obstacle['y'], obstacle['width'], obstacle['height']))
            pygame.draw.rect(self.screen, BLACK, 
                           (obstacle['x'], obstacle['y'], obstacle['width'], obstacle['height']), 2)
        
        # Draw finish line
        pygame.draw.rect(self.screen, GREEN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        finish_text = self.font.render("FINISH LINE", True, BLACK)
        self.screen.blit(finish_text, (SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 30))
        
        # Draw marbles
        for marble in self.marbles:
            marble.draw(self.screen, self.font)
        
        # Draw race info
        elapsed_time = time.time() - self.start_time
        time_text = self.font.render(f"Race Time: {elapsed_time:.1f}s", True, BLACK)
        self.screen.blit(time_text, (10, 10))
        
        # Draw leaderboard
        finished_marbles = [m for m in self.marbles if m.finished and m.position_rank]
        if finished_marbles:
            leaderboard_title = self.font.render("LEADERBOARD:", True, BLACK)
            self.screen.blit(leaderboard_title, (SCREEN_WIDTH - 250, 10))
            
            finished_marbles.sort(key=lambda m: m.position_rank)
            for i, marble in enumerate(finished_marbles[:5]):
                rank_text = self.font.render(f"{marble.position_rank}. {marble.follower_name}", True, marble.color)
                self.screen.blit(rank_text, (SCREEN_WIDTH - 250, 40 + i * 25))
        
        # Draw winner announcement
        if self.race_finished and self.winners:
            winner_text = self.big_font.render(f"WINNER: {self.winners[0].follower_name}!", True, RED)
            text_rect = winner_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
            pygame.draw.rect(self.screen, WHITE, text_rect.inflate(20, 10))
            pygame.draw.rect(self.screen, BLACK, text_rect.inflate(20, 10), 3)
            self.screen.blit(winner_text, text_rect)
        
        # Draw instructions
        if not self.race_finished:
            instruction_text = self.font.render("Watch the marble race! Each marble represents a TikTok follower.", True, BLACK)
            self.screen.blit(instruction_text, (10, SCREEN_HEIGHT - 90))
            restart_text = self.font.render("Press R to restart the race", True, BLACK)
            self.screen.blit(restart_text, (10, SCREEN_HEIGHT - 70))
        
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
    print("TikTok Followers Marble Race Game")
    print("="*40)
    print("Each marble represents a TikTok follower racing through the maze!")
    print("Controls:")
    print("- R: Restart race")
    print("- ESC: Quit game")
    print("\nNote: Using sample follower names. Replace SAMPLE_FOLLOWERS with real data if available.")
    print("="*40)
    
    game = MarbleRaceGame()
    game.run()
