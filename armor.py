import pygame
import random
from pygame.sprite import Sprite

class Armor(Sprite):
    def __init__(self, game):
        super().__init__()

        self.screen = game.screen
        self.screen_width = game.screen_width
        self.screen_height = game.screen_height

        self.image = pygame.transform.scale(pygame.image.load("./assets/Armor.png"), (100, 100))

        self.rect = self.image.get_rect()

        self.rect.x = random.randint(50, self.screen_width-50)
        self.rect.y = random.randint(50, self.screen_height-50)