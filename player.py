import pygame
from pygame.sprite import Sprite

class Player(Sprite):
    def __init__(self, game):
        super().__init__()

        self.screen = game.screen
        self.settings = game.settings
        self.screen_rect = self.screen.get_rect()

        self.width, self.height = 25, 25
        self.rect = pygame.Rect(game.screen_width/2, game.screen_height/2, self.width, self.height)

        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False

        self.health_remaining = 1
        self.armor = 0
        self.xp = 0
        self.level = 1

        self.onehitkill = False


    def update_position(self):
        if self.moving_left == True and self.rect.left > self.screen_rect.left:
            self.rect.x -= self.settings.player_speed

        if self.moving_right == True and self.rect.right < self.screen_rect.right:
            self.rect.x += self.settings.player_speed

        if self.moving_up == True and self.rect.top > self.screen_rect.top:
            self.rect.y -= self.settings.player_speed

        if self.moving_down == True and self.rect.bottom < self.screen_rect.bottom:
            self.rect.y += self.settings.player_speed
    

    def draw(self):
        pygame.draw.rect(self.screen, self.settings.player_color, self.rect)