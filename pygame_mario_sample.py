import sys
import numpy as np
import pygame
from pygame.locals import *
from pygame.sprite import AbstractGroup
from pathlib import Path
from itertools import cycle
from pyLegoMario import PygameMario, AsyncClock, ACC_EVENT, RGB_EVENT, PANTS_EVENT

pygame.init()
WIDTH, HEIGHT = 1200, 600
WHITE = (255,255,255)
BLACK = (0,0,0)
BACKGROUND_COLOR = (64, 71, 109)
DATA_DIR = Path(__file__).parent
FONT = pygame.font.SysFont(None, 70)
TEXT_EVENT = pygame.event.custom_type()
BUTTON_EVENT = pygame.event.custom_type()

class Wall(pygame.sprite.Sprite):
    def __init__(self, *groups: tuple[AbstractGroup],
                 rect: pygame.Rect = None, 
                 color: tuple[int, int, int] = (254, 205, 170),
                 static: bool = True,
                 no_spawn_areas: list[pygame.Rect] = []) -> None:
        super().__init__(*groups)
        if not rect:
            self.init_randomly()
            while self.rect.collidelist(no_spawn_areas) != -1:
                self.init_randomly()
        else:
            self.rect = rect
            if self.rect.collidelist(no_spawn_areas) != -1:
                raise ValueError('The provided rect intersects with an object')
        rand_direction = np.random.random(2)
        # normalize initial direction
        self.direction = rand_direction / np.linalg.norm(rand_direction)
        self.speed = np.random.randint(2, 5)
        self.static = static
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(color)

    def update(self, frame: int = None, players: list['Player'] = [], **kwargs
        ) -> None:
        """Moves the wall by speed * direction if it's not static. Bounces off
           screen boundaries. Moves any players in the players argument on
           collision. 10% chance to increase speed on every 300ths frame.
           
        Args:
            frame (int, optional): frame of the current game.
            players: list of Player objects to check collision for (and move)"""
        if self.static:
            return
        if frame:
            if (frame % 300) == 0:
                if np.random.randint(11) == 10:
                    self.speed += 1
        if self.rect.left < 0 or self.rect.right > WIDTH:
            self.direction[0] = -self.direction[0]
        elif self.rect.top < 0 or self.rect.bottom > HEIGHT:
            self.direction[1] = -self.direction[1]
        step = self.direction * self.speed
        self.rect.move_ip(step[0], step[1])
        for player in players:
            if self.rect.colliderect(player.rect):
                move_x = player.rect.move(step[0], 0)
                if self.rect.colliderect(move_x):
                    step[0] = 0
                    player.move(step)
                else:
                    step[1] = 0
                    player.move(step)

    def init_randomly(self) -> None:
        """Randomly sets size and coordinates respecting screen boundaries
           and min/max sizes."""
        seed = np.random.random(4)
        x, y = seed[:2] * (WIDTH, HEIGHT)
        # limit width, height to their distance to screen
        min_size = np.array((10, 10))
        max_size = np.array((min(WIDTH - x, 100), min(HEIGHT - y, 75)))
        width, height = min_size + seed[2:4] * (max_size - min_size)
        self.rect = pygame.Rect(x, y, width, height)

    def SCREEN_WALLS() -> list['Wall']:
        """Creates wall objects around the screen.

        Returns:
            list[Wall]: A list of wall objects around the screen.
        """
        SCREEN_WALLS = [(0, -1, WIDTH, 1),
                        (-1, 0, 1, HEIGHT),
                        (0, HEIGHT + 1, WIDTH, 1),
                        (WIDTH + 1, 0, 1, HEIGHT)]
        return [Wall(rect=pygame.Rect(wall)) for wall in SCREEN_WALLS]


class Player(pygame.sprite.Sprite):
    """Represents a single player in the game. Handles movement and updates.

        Attributes
        ----------
        id: int
            unique identifier, starting at 1
        mario: PygameMario
            object representing bluetooth connection to a Lego Mario
        image: pygame.Surface
            Contains an image representing the player visually.
            Required for interaction with pygame.sprite's functions
        target: np.ndarray
            currently unused, previously used for movement.
        direction: np.ndarray
            2-D array representing the direction the players is moving
        rect: pygame.Rect
            rectangle object representing the player's current position.
        precise_coors: np.ndarray
            2-D array representing the player's position with sub-pixel
            accuracy"""

    player_counter = (x for x in range(1,30))
    PLAYER_COLORS = cycle(((244, 134, 134),
                          (97, 231, 160),
                          (243, 151, 214),
                          (128, 192, 244)))

    def __init__(self, *groups: tuple[AbstractGroup]) -> None:
        super().__init__(*groups)
        self.id = next(Player.player_counter)
        self.mario = PygameMario()
        # player icon
        self.image = pygame.Surface((50,50))
        self.image.fill(next(self.PLAYER_COLORS))
        # rectangle and coordinates
        self.reset()
        # movement variables
        self.manual_speed = False
        self.target = np.array(self.rect.center)
        self.direction = np.array((0,0))

    def reset(self) -> None:
        """Places the player on a random spot inside the screen by assigning
           self.precise_coords and self.rect."""
        max_x, max_y = np.array((WIDTH, HEIGHT)) - self.image.get_size()
        self.precise_coords = np.random.random(2) * (max_x, max_y)
        self.rect = self.image.get_rect(topleft = self.precise_coords)

    def update(self, sender=None, mario_acc=None, *args,
               **kwargs) -> None:
        """Checks kwargs for a new direction from Mario, calculates step, and
           calls self.move to move."""
        if (sender == self.mario) and mario_acc:
            mario_acc = np.array(mario_acc)
            length = np.linalg.norm(mario_acc)
            length = max(length, 0.01)  # prevent zerodivision
            self.direction = mario_acc / length
            self.speed = length * 7 / 50
        step = self.direction * self.speed
        self.move(step, **kwargs)

    def move(self, step: np.ndarray, collision_sprites: AbstractGroup = None,
             **kwargs) -> None:
        """Moves self by step. Prevents collision with the provided sprites.

        Args:
            step (np.ndarray): The direction and distance to move as a vector
            wall_sprite_group (AbstractGroup, optional): Sprites to check
                collision with. Defaults to None.
        """
        if not np.any(step):
            # no move
            return
        elif not collision_sprites:
            # no collision
            self.precise_coords += step
            self.rect.x, self.rect.y = self.precise_coords
            return
        # try moving
        new_pos = self.precise_coords + step
        self.rect.x, self.rect.y = new_pos
        if pygame.sprite.spritecollideany(self, collision_sprites):
            # move wasn't possible without collision, reset rect
            self.rect.x, self.rect.y = self.precise_coords
            # try moving in the directions independently
            if np.all(step):
                only_y = step.copy()
                only_x = step.copy()
                only_y[0] = 0
                only_x[1] = 0
                self.move(only_y, collision_sprites)
                self.move(only_x, collision_sprites)
                return
            # try smaller step sizes
            if np.linalg.norm(step) > 1:
                self.move(step / 2, collision_sprites=collision_sprites)
                self.move(step / 2, collision_sprites=collision_sprites)
                return
        else: #  moved without collisions
            self.precise_coords = new_pos
            return

    @property
    def target_direction(self) -> np.ndarray:
        """2D Unit vector from self.center to self.target"""
        to_target = self.target - self.rect.center
        distance = np.linalg.norm(to_target)
        if distance > self.speed:
            return (to_target / distance)
        return np.ndarray((0,0))

    @property
    def speed(self) -> float:
        if self.manual_speed:
            return self._speed
        distance = np.linalg.norm(self.target - self.rect.center)
        return (distance + 60) ** 1.25 / 100
    
    @speed.setter
    def speed(self, value):
        self.manual_speed = True
        self._speed = value

    @speed.deleter
    def speed(self):
        self.manual_speed = False


class Game:
    """Object to represent a single game. Handles logic and holds underlying
       players, walls, and game loop"""
    def __init__(self, target_surface: pygame.Surface,
                 player_num: int) -> None:
        self.surface = target_surface
        self.players = [Player() for _ in range(player_num)]
        self.clock = AsyncClock()
        self.text = None
        self.rect = self.surface.get_rect()
        self.new_game()
        self.run_game()
    
    def wait_for_marios(self) -> None:
        """Checks connection with all players' Marios and pauses if necessary."""
        if not self.all_marios_connected:
            for player in self.players:
                self.communicate(f'Waiting for player {player.id}\'s Mario')
                while not player.mario.is_connected:
                    self.clock.tick(60)
                    self.draw_frame()
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            pygame.quit()
                            sys.exit()
            self.countdown()

    def countdown(self, seconds: int = 3) -> None:
        """Pauses the game and counts down on the screen before un-pausing.

        Args:
            seconds (int, optional): Number to count from. Defaults to 3.
        """
        for i in range(seconds,0,-1):
            start = pygame.time.get_ticks()
            self.communicate(str(i))
            while pygame.time.get_ticks() - start < 1000:
                self.draw_frame()
                for event in pygame.event.get():
                    if event.type == QUIT:
                        pygame.quit()
                        sys.exit()
                self.clock.tick(60)
        self.communicate('Go!', 500)

    def new_game(self) -> None:
        """Sets up new game by 'reviving' players, initializing new walls,
           and resetting the frame counter."""
        self.game_timer = 0
        self.active_player_group = pygame.sprite.Group(self.players)
        [player.reset() for player in self.players]
        self.walls = Wall.SCREEN_WALLS()[:]
        player_rects = [player.rect for player in self.players]
        num_walls = np.random.randint(3,16) + np.random.randint(3,16)
        for _ in range(num_walls):
            self.walls.append(Wall(static=False, no_spawn_areas=player_rects))
        self.walls = pygame.sprite.Group(self.walls)
        self.draw_frame()
        self.frame_counter = 0

    def run_game(self) -> None:
        """Loops the game until all players are dead, then starts new game."""
        if self.all_marios_connected:
            self.countdown()
        while True:
            self.wait_for_marios()
            self.frame_counter += 1
            self.game_timer += self.clock.get_time()
            kwargs = {'collision_sprites': self.walls,
                      'frame': self.frame_counter,
                      'players': self.active_player_group}

            # event handling
            for event in pygame.event.get():
                if event.type == ACC_EVENT:
                    kwargs['mario_acc'] = event.value[::2]
                    kwargs['sender'] = event.sender
                elif event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == TEXT_EVENT:
                    self.text = None

            # game logic
            self.active_player_group.update(**kwargs)
            self.walls.update(**kwargs)
            for player in self.active_player_group:
                if pygame.sprite.spritecollideany(player, self.walls):
                    self.communicate(f'Player {player.id} died', 400)
                    self.active_player_group.remove(player)

            # execution
            self.draw_frame()
            self.clock.tick(60)
            if not self.active_player_group:
                break
        self.new_game()
        self.run_game()

    def draw_frame(self) -> None:
        """Fills background, draws walls, active players, and active text,
           then updates the display."""
        self.surface.fill(BACKGROUND_COLOR)
        self.walls.draw(self.surface)
        self.active_player_group.draw(self.surface)
        if self.text:
            rect = self.text.get_rect(center=self.rect.center)
            self.surface.blit(self.text, rect)
        # render timer
        timer_text = FONT.render(str(self.game_timer // 1000), True, BLACK)
        timer_rect = timer_text.get_rect(topright=(WIDTH, 0))
        self.surface.blit(timer_text, timer_rect)
        pygame.display.update()

    def communicate(self, text: str, duration: float = None):
        """Call to communicate message to user.

        Args:
            text (str): Text to communicate.
            duration (float, optional): Number of milliseconds the message
                will stay on the screen. By default, will remain there until
                method is called again."""
        if duration:
            pygame.time.set_timer(TEXT_EVENT, duration)
        self.text = FONT.render(text, True, BLACK)

    @property
    def all_marios_connected(self):
        """True if all players' Marios are currently connected."""
        return all([player.mario.is_connected for player in self.players])

class Button(pygame.sprite.Sprite):
    def __init__(self, rect: pygame.Rect, text: str,
                 back_color: tuple[int, int, int], *groups: AbstractGroup
                 ) -> None:
        super().__init__(*groups)
        self.rect = rect
        text_surface = FONT.render(text, True, WHITE)
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(back_color)
        target_rect = text_surface.get_rect().fit(self.image.get_rect())
        text_surface = pygame.transform.scale(text_surface, (target_rect.size))
        self.image.blit(text_surface, target_rect)

window = pygame.display.set_mode((WIDTH, HEIGHT))
one_button = Button(pygame.Rect(300,250,200,100), 'One', (97, 231, 160))
two_button = Button(pygame.Rect(600,250,200,100), 'Two', (243, 151, 214))
buttons = pygame.sprite.Group(one_button, two_button)

window.fill(BACKGROUND_COLOR)
buttons.draw(window)
question = FONT.render('How many players?', True, WHITE)
window.blit(question, (320,180))

player_num = None
while not player_num:
    for event in pygame.event.get():
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            if one_button.rect.collidepoint(event.pos):
                player_num = 1
            elif two_button.rect.collidepoint(event.pos):
                player_num = 2
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()
game = Game(window, player_num)