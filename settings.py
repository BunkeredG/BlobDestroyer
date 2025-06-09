import pygame

class Settings:
    def __init__(self):
        # Spawn timer
        self.time_between_spawns = 60 # spawns start at 5 seconds per interval
        self.spawn_time_change = 1
        self.probability_spawn_large = 0 # probability to spawn a large enemy - first spawn cannot be large

        # Upgrade
        # PlayerSpeed, BulletSpeed, Regeneration, BulletSize, MultiBullet, BulletFireSpeed, OneHitKill
        self.upgrade_weights = (30, 30, 20, 30, 10, 80, 0)

        # Player
        self.player_color = (255, 255, 255)
        self.player_speed = 8
        self.post_hit_invuln = 30

        # Health loss
        self.s_health_loss = 0.1
        self.l_health_loss = 0.2

        # XP gain
        self.s_xp_gain = 1
        self.l_xp_gain = 2

        # Enemy
        self.enemy_color = (255, 0, 0)
        self.s_enemy_speed = 4
        self.l_enemy_speed = 2

        # Enemy dimensions
        self.enemy_width = 20
        self.s_enemy_height = 20
        self.l_enemy_height = 40

        # Bullet
        self.bullet_color = (255, 255, 255)
        self.bullet_speed = 10
        self.fire_bullet_ticks = 30

        # list of chocies
        self.upgrade_choices = ["PlayerSpeed", "BulletSpeed", "Regeneration", "BulletSize", "MultiBullet", "BulletFireSpeed", "OneHitKill"]
        self.upgrade_scale = (150, 150)

        # import all images
        self.playerspeed_image = pygame.transform.scale(pygame.image.load("./assets/PlayerSpeed.png"), self.upgrade_scale)
        self.bulletspeed_image = pygame.transform.scale(pygame.image.load("./assets/BulletSpeed.png"), self.upgrade_scale)
        self.regeneration_image = pygame.transform.scale(pygame.image.load("./assets/Regeneration.png"), self.upgrade_scale)
        self.bulletsize_image = pygame.transform.scale(pygame.image.load("./assets/BulletSize.png"), self.upgrade_scale)
        self.multibullet_image = pygame.transform.scale(pygame.image.load("./assets/MultiBullet.png"), self.upgrade_scale)
        self.bulletfirespeed_image = pygame.transform.scale(pygame.image.load("./assets/BulletFireSpeed.png"), self.upgrade_scale)
        self.onehitkill_image = pygame.transform.scale(pygame.image.load("./assets/OneHitKill.png"), self.upgrade_scale)
        self.upgrade_images = [self.playerspeed_image, self.bulletspeed_image, self.regeneration_image, self.bulletsize_image, self.multibullet_image, self.bulletfirespeed_image, self.onehitkill_image]

        # upgrade variables
        self.playerspeed_upgrade = 1
        self.bulletspeed_upgrade = 2
        self.regeneration_upgrade = 0.4
        self.bulletsize_upgrade = 2
        self.multibullet_time_amount = 300 # in ticks
        self.bulletfirespeed_upgrade = 1
        self.onehitkill_time_amount = 180 # in ticks

        #self.upgrade_images = dict(zip(self.upgrade_choices, self.upgrade_images))

        # alpha channels & colors
        self.bar_transparency = 50
        self.armor_transparency = 75
        self.bezel_color = (150, 150, 150, self.bar_transparency)
        self.heath_color = (255, 0, 0, self.bar_transparency)
        self.armor_color = (200, 200, 200, self.armor_transparency)
        self.xp_color = (0, 0, 255, self.bar_transparency)