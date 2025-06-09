import pygame
from pygame.sprite import Sprite

class Bullet(Sprite):
    def __init__(self, game, x, y, width, height):
        super().__init__()

        self.screen = game.screen
        self.settings = game.settings
        self.screen_rect = self.screen.get_rect()

        self.width, self.height = width, height
        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.change_x, self.change_y = None, None

    
    def draw(self):
        pygame.draw.rect(self.screen, self.settings.bullet_color, self.rect, border_radius=2)