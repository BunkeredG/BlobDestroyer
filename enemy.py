import pygame
from pygame.sprite import Sprite
import random

class Enemy(Sprite):
    def __init__(self, game, size, x_pos, y_pos):
        super().__init__()

        self.screen = game.screen
        self.settings = game.settings

        self.dead = False

        self.size = size
        if size == "s":
            self.speed = self.settings.s_enemy_speed
            self.width, self.height = self.settings.enemy_width, self.settings.s_enemy_height

            self.health = 1
        elif size == "l":
            self.speed = self.settings.l_enemy_speed
            self.width, self.height = self.settings.enemy_width, self.settings.l_enemy_height

            self.og_health = 3
            self.health = 3

        self.color = self.settings.enemy_color
        
        # self.image = pygame.Surface((self.width, self.height))
        # self.image.fill(self.settings.enemy_color)
        # self.rect = self.image.get_rect()
        self.rect = pygame.Rect(x_pos, y_pos, self.width, self.height)


    def draw(self):
        pygame.draw.rect(self.screen, self.color, self.rect)

    def decrease_health(self, ohk):
       if ohk:
           self.health = 0
       elif self.health > 0:
           self.health -= 1