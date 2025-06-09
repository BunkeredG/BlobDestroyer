import pygame
import pygame.font
import pygame.time
import sys
import math
import random

from armor import Armor
from bullet import Bullet
from player import Player
from settings import Settings
from enemy import Enemy

show_title_screen = True

class BlobDestroyer:
    def __init__(self):
        pygame.init()

        # creates the screen with given width and height. vsync is enabled to prevent screentear
        self.screen = pygame.display.set_mode((1920, 1200), pygame.FULLSCREEN | pygame.DOUBLEBUF, vsync=1)
        # self.screen = pygame.display.set_mode((1920, 1200), pygame.FULLSCREEN | pygame.SCALED | pygame.DOUBLEBUF, vsync=1)
        self.screen_width = self.screen.get_rect().width
        self.screen_height = self.screen.get_rect().height

        self.title_font = pygame.font.SysFont(None, 300)
        self.medium_font = pygame.font.SysFont(None, 100)
        self.small_font = pygame.font.SysFont(None, 50)
        self.tiny_font = pygame.font.SysFont(None, 30)

        if show_title_screen == True:
            self.title_screen()

        self.settings = Settings()
        self.player = Player(self)
        self.armor = None

        self.bullets = pygame.sprite.Group()
        self.bullet_width = 10
        self.bullet_height = 10
        self.multibullet_timer = 0
        
        self.enemies = pygame.sprite.Group()

        self.xp_to_level_up = 10*self.player.level

        self.clock = pygame.time.Clock()
        self.check_collisions_timer = 0
        self.player_collision_timer = 0
        self.bullet_timer = 0
        self.spawn_timer = 0
        self.onehitkill_timer = 0
        self.timer_to_change_spawn_rate = 0

        self.num_upgrades = 0

        self.num_spawns = 0

        self.start_time = pygame.time.get_ticks()
        self.elapsed_time = 0

        self.restart = False

    def run_game(self):
        while True:
            self.check_events()
            self.player.update_position()
            self.spawn_new_enemies()
            self.update_enemy_position()
            self.update_bullet_position()
            self.fire_bullets()

            self.check_enemy_collisions()
            self.check_player_collisions()
            self.check_bullet_collisions()
            self.check_armor_collisions()

            self.remove_offscreen_bullets()
            self.draw_all()

            if self.player.health_remaining <= 0:
                self.restart = self.death_screen()

            if not self.armor and self.player.armor != 1 and self.elapsed_time > 90:
                if random.randint(1, 1800) == 1:
                    self.armor = Armor(self)

            if self.player.xp >= (self.xp_to_level_up*self.player.level):
                self.level_up()

            self.clock.tick(60)
            self.player_collision_timer += 1
            self.bullet_timer += 1
            self.spawn_timer += 1
            self.timer_to_change_spawn_rate += 1

            self.check_collisions_timer += 1

            if self.multibullet_timer != 0:
                self.multibullet_timer -= 1

            if self.onehitkill_timer != 0:
                self.onehitkill_timer -= 1
            else:
                self.player.onehitkill = False

            self.elapsed_time = int((pygame.time.get_ticks() - self.start_time)/1000) # Gets elapsed time in seconds (get_ticks() -> ms)
            self.draw_time()

            if self.restart == True:
                show_title_screen = False
                self.__init__()

            pygame.display.flip()



    def spawn_new_enemies(self):
        if self.spawn_timer == self.settings.time_between_spawns:
            self.num_spawns += 1 # increases variable with number of spawns at current time_between_spawns

            # randomly chooses whether to spawn small or large enemy
            rand_size = random.choices([0, 1], [200, self.settings.probability_spawn_large])[0] # weights depending on probability to spawn large enemy
            if rand_size == 0:
                size = "s"
            else:
                size = "l"

            # spawns enemy at random place on the edge of the screen
            rand_axis = random.randint(0, 1)
            if rand_axis == 0:
                enemy_x = random.randint(0, self.screen_width)
                enemy_y = random.choice([0, self.screen_height])
            else:
                enemy_x = random.choice((0, self.screen_width))
                enemy_y = random.randint(0, self.screen_height)

            # adds enemy
            new_enemy = Enemy(self, size, enemy_x, enemy_y)
            self.enemies.add(new_enemy)

            # runs after 5 spawns at current time_between_spawns
            if self.timer_to_change_spawn_rate == 180:
                # reduces time_between_spawns by spawn_time_change as long as time_between_spawns is larger than 1 tick
                if self.settings.time_between_spawns > 1:
                    self.settings.time_between_spawns -= self.settings.spawn_time_change

                # reset number of spawns at current time_between_spawns
                self.timer_to_change_spawn_rate = 0

            # increase probability to spawn a large enemy by 1 every spawn
            if self.settings.probability_spawn_large <= 100:
                self.settings.probability_spawn_large += 1

            # resets spawn timer
            self.spawn_timer = 0



    def update_enemy_position(self):
        for enemy in self.enemies:
            enemy_x = enemy.rect.x
            enemy_y = enemy.rect.y

            player_x = self.player.rect.x
            player_y = self.player.rect.y

            path_x = player_x - enemy_x
            path_y = player_y - enemy_y

            hypotenuse = math.sqrt(path_x**2 + path_y**2)

            if hypotenuse != 0:
                move_x = path_x/hypotenuse
                move_y = path_y/hypotenuse

                enemy.rect.x += enemy.speed*move_x
                enemy.rect.y += enemy.speed*move_y


    def update_bullet_position(self):
        for bullet in self.bullets:
            bullet.rect.x += bullet.change_x
            bullet.rect.y += bullet.change_y


    def fire_bullets(self):
        if self.bullet_timer >= self.settings.fire_bullet_ticks:
            mouse_x, mouse_y = pygame.mouse.get_pos() # get mouse position and split it into x and y
            player_x, player_y = self.player.rect.x, self.player.rect.y # get player x and y position

            # gets both legs of a triangle
            path_x = mouse_x - player_x
            path_y = mouse_y - player_y

            hypotenuse = math.sqrt(path_x**2 + path_y**2) # finds the hypotenuse between player pos and mouse pos

            if hypotenuse != 0:
                # scales move amounts down to 1 so the bullet continues traveling at a standard rate
                move_x = path_x/hypotenuse
                move_y = path_y/hypotenuse
                
                # create new bullet at player position
                new_bullet = Bullet(self, player_x, player_y, self.bullet_width, self.bullet_height)
                self.bullets.add(new_bullet)

                # gives the bullet the calculated move amounts
                new_bullet.change_x = self.settings.bullet_speed*move_x
                new_bullet.change_y = self.settings.bullet_speed*move_y
            else:
                return
            
            self.bullet_timer = 0 # resets bullet timer
        
            if self.multibullet_timer > 0:
                angle_offset = math.radians(10)
                
                # Angle a bullet 10 degrees to the left
                move_x_left = move_x * math.cos(angle_offset) - move_y * math.sin(angle_offset)
                move_y_left = move_x * math.sin(angle_offset) + move_y * math.cos(angle_offset)

                # create new bullet at player position
                left_bullet = Bullet(self, player_x, player_y, self.bullet_width, self.bullet_height)
                self.bullets.add(left_bullet)

                # gives the bullet the calculated move amounts
                left_bullet.change_x = self.settings.bullet_speed*move_x_left
                left_bullet.change_y = self.settings.bullet_speed*move_y_left

                # Angle a bullet 10 degrees to the right
                move_x_right = move_x * math.cos(-angle_offset) - move_y * math.sin(-angle_offset)
                move_y_right = move_x * math.sin(-angle_offset) + move_y * math.cos(-angle_offset)

                # create new bullet at player position
                right_bullet = Bullet(self, player_x, player_y, self.bullet_width, self.bullet_height)
                self.bullets.add(right_bullet)

                # gives the bullet the calculated move amounts
                right_bullet.change_x = self.settings.bullet_speed*move_x_right
                right_bullet.change_y = self.settings.bullet_speed*move_y_right



    def check_enemy_collisions(self):
        if self.check_collisions_timer >= max(5, (len(self.enemies)//25)+1): # Reduces number of collisions checked per increase of enemies
            for enemy in self.enemies:
                enemies_copy = self.enemies.copy()

                enemies_copy.remove(enemy)

                collisions = pygame.sprite.spritecollide(enemy, enemies_copy, False)
                if collisions:
                    for collided_enemy in collisions:
                        if enemy.rect.x < collided_enemy.rect.x:
                            enemy.rect.x -= (collided_enemy.width/2)
                        else:
                            enemy.rect.x += (collided_enemy.width/2)+1

                        if enemy.rect.y < collided_enemy.rect.y:
                            enemy.rect.y -= (collided_enemy.height/2)
                        else:
                            enemy.rect.y += (collided_enemy.height/2)+1

            self.check_collisions_timer = 0


    
    def check_player_collisions(self):
        if self.player_collision_timer > self.settings.post_hit_invuln: # Grants set amount of invincibility after player is hit
            collisions = pygame.sprite.spritecollide(self.player, self.enemies, False)
            if collisions:
                self.settings.player_color = (233, 124, 65) # invincibility color

                if collisions[0].size == "s":
                    if self.player.armor > 0:
                        self.player.armor -= self.settings.s_health_loss
                    else:
                        self.player.health_remaining -= self.settings.s_health_loss

                elif collisions[0].size == "l":
                    if self.player.armor > 0:
                        self.player.armor -= self.settings.l_health_loss
                    else:
                        self.player.health_remaining -= self.settings.l_health_loss

                self.player.health_remaining = round(self.player.health_remaining, 2)

                self.player_collision_timer = 0
            else:
                self.settings.player_color = (255, 255, 255)


    def check_armor_collisions(self):
        if self.armor:
            collision = pygame.sprite.collide_rect(self.player, self.armor)
            if collision:
                self.armor = None
                self.player.armor += 0.2


    def check_bullet_collisions(self):
        collisions = pygame.sprite.groupcollide(self.bullets, self.enemies, True, False)
        if collisions:
            # for each collision between a bullet and enemies
            for collision in collisions.values():
                # for each enemy in that collision
                for enemy in collision:
                    # removes 1 health if above 0
                    enemy.decrease_health(self.player.onehitkill)
                    
                    # if enemy health is 0 and xp has not been gained
                    if enemy.health == 0 and enemy.dead == False:
                        if enemy.size == "s":
                            self.player.xp += self.settings.s_xp_gain # grants small xp gain for killing a small enemy
                        elif enemy.size == "l":
                            self.player.xp += self.settings.l_xp_gain # grants large xp gain for killing a large enemy
                        
                        enemy.dead = True # Removes ability to gain additional xp from the same enemy (double bullet hit)
                        enemy.kill() # removes enemy

                    elif enemy.size != "s":
                        r,g,b = enemy.color # seperates enemy's rgb values

                        
                        try:
                            r -= 255/enemy.og_health # reduces lightness of red to indicate damage
                        except AttributeError:
                            
                            import pdb; pdb.set_trace() # "breakpoint"

                            # IF ERROR:
                            # check if enemy object exists
                            # dir(enemy)  ... see the attributes and method of enemy
                            # enemy.og_health  ... see if it's None or if it exists at all
                            
                            # "n"  - next line 
                            # "s"  - step 
                            # "bt"  - stack trace 
                            # "q"  - quit the debugger
                            # "c"  - continue
                        
                        enemy.color = (r,g,b) # sets enemy's color to new values


    def remove_offscreen_bullets(self):
        for bullet in self.bullets:
            if bullet.rect.x > self.screen_width + 100 or bullet.rect.x < -100 or bullet.rect.y > self.screen_height + 100 or bullet.rect.y < -100:
                self.bullets.remove(bullet)

    
    
    def check_events(self):
        # handle key press events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # if key pressed
            if event.type == pygame.KEYDOWN:
                self.check_keydown_events(event)

            # if key unpressed        
            elif event.type == pygame.KEYUP:
                self.check_keyup_events(event)



    def check_keydown_events(self, event):
        # check for player movements
        if event.key == pygame.K_w or event.key == pygame.K_UP:
            self.player.moving_up = True
        
        if event.key == pygame.K_a or event.key == pygame.K_LEFT:
            self.player.moving_left = True
        
        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
            self.player.moving_down = True
        
        if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
            self.player.moving_right = True

        # quits game if Q pressed
        if event.key == pygame.K_q:
            pygame.quit()
            sys.exit()

    
    def check_keyup_events(self, event):
        if event.key == pygame.K_w or event.key == pygame.K_UP:
            self.player.moving_up = False
        
        if event.key == pygame.K_a or event.key == pygame.K_LEFT:
            self.player.moving_left = False
        
        if event.key == pygame.K_s or event.key == pygame.K_DOWN:
            self.player.moving_down = False
        
        if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
            self.player.moving_right = False


    def level_up(self):
        # Reset player xp and level up player
        self.player.xp = 0
        self.player.level += 1

        # Stop player movement
        self.player.moving_up = False
        self.player.moving_left = False
        self.player.moving_down = False
        self.player.moving_right = False

        # Create and draw surface for level up tiles
        surface = pygame.Surface((self.screen_width/2, self.screen_height/4))
        pygame.draw.rect(surface, (0, 100, 150), pygame.Rect(0, 0, surface.get_width(), surface.get_height()))

        # Draw level up tiles
        upgrades = self.draw_level_up_tiles(surface)

        # While player has not clicked an upgrade
        is_upgrade_chosen = False
        while not is_upgrade_chosen:
            # Draw the surface with level up tiles and flip display to show it
            self.screen.blit(surface, (self.screen_width/4, 3*self.screen_height/8))
            self.draw_time()
            pygame.display.flip()

            # Check all events
            for event in pygame.event.get():
                is_upgrade_chosen = self.level_up_events(event, upgrades)

        self.num_upgrades += 1

    # def draw_level_up_tiles(self, surface):
    #     upgrades_chosen = {}
    #     positions = [(50, 50), (250, 50), (450, 50)]
    #     for i, upgrade in enumerate(random.sample(self.settings.upgrade_choices, 3)):
    #         # load and position the image
    #         upgrade_image = self.settings.upgrade_images[upgrade]
    #         upgrade_rect = upgrade_image.get_rect(topleft=positions[i])
    #         # blit image onto surface
    #         surface.blit(upgrade_image, upgrade_rect.topleft)
    #         upgrades_chosen[upgrade] = upgrade_rect
    #         return upgrades_chosen
        

    def draw_level_up_tiles(self, surface):
        temp_upgrade_choices = self.settings.upgrade_choices.copy()

        # PlayerSpeed, BulletSpeed, Regeneration, BulletSize, MultiBullet, BulletFireSpeed, OneHitKill
        # (30, 30, 20, 30, 10, 80, 0) - Original weights
        if self.num_upgrades == 5:
            self.settings.upgrade_weights = (30, 30, 40, 30, 20, 50, 10) # Weights adjusted after 5 upgrades
        elif self.num_upgrades == 10:
            self.settings.upgrade_weights = (30, 30, 30, 30, 20, 30, 10) # Weights adjusted after 10 upgrades
        
        # Removes the bullet fire speed upgrade from being shown if the tick number is too low
        if self.settings.fire_bullet_ticks <= 1:
            temp_upgrade_choices.remove("BulletFireSpeed")
            self.settings.upgrade_weights = (30, 30, 30, 30, 20, 10) # re-defines the weights without the BulletFireSpeed upgrade

        upgrade_choices_list = [] # Creates an empty list for upgrades
        # Creates weighted upgrade choices until there are 4 unique upgrades chosen
        while len(upgrade_choices_list) <= 4:
            temp_upgrade_choice = random.choices(temp_upgrade_choices, weights=self.settings.upgrade_weights)[0]
            
            # Adds weighted choice to upgrades list if it has not been chosen before
            if temp_upgrade_choice not in upgrade_choices_list:
                upgrade_choices_list.append(temp_upgrade_choice)

        upgrades_chosen = {} # Creates an empty dictionary
        for i in range(4):
            upgrade = upgrade_choices_list[i] # Sets upgrade equal to ith chosen upgrade
        
            upgrades_chosen[upgrade] = None # Populates dictionary to {upgrade: None}

        upgrades = list(upgrades_chosen.keys()) # List of names of upgrades chosen

        # Loads images
        surface1 = self.settings.upgrade_images[self.settings.upgrade_choices.index(upgrades[0])]
        surface2 = self.settings.upgrade_images[self.settings.upgrade_choices.index(upgrades[1])]
        surface3 = self.settings.upgrade_images[self.settings.upgrade_choices.index(upgrades[2])]
        
        # Creates rectangle at positions for images to be blitted on
        tile1 = surface1.get_rect(center=(surface.get_width()/4, surface.get_height()/2)) # Left
        tile2 = surface2.get_rect(center=(surface.get_width()/2, surface.get_height()/2)) # Center
        tile3 = surface3.get_rect(center=(3*surface.get_width()/4, surface.get_height()/2)) # Right
        
        # Blits three surfaces to the given tiles
        surface.blit(surface1, tile1.topleft)
        surface.blit(surface2, tile2.topleft)
        surface.blit(surface3, tile3.topleft)

        upgrades_chosen[upgrades[0]] = tile1 # Sets first upgrade's value to tile1
        upgrades_chosen[upgrades[1]] = tile2 # Sets second upgrade's value to tile2
        upgrades_chosen[upgrades[2]] = tile3 # Sets third upgrade's value to tile3

        # Creates surface, tile, and blits bonus upgrade if there have been less than 10 upgrades
        if self.num_upgrades <= 10:
            surface4 = pygame.transform.scale(self.settings.upgrade_images[self.settings.upgrade_choices.index(upgrades[3])], (75, 75))
            tile4 = surface4.get_rect(topleft=(10, 10))
            surface.blit(surface4, tile4.topleft)
            upgrades_chosen[upgrades[3]] = tile4

        return upgrades_chosen # {upgrade[0]: tile1, upgrade[1]: tile2, etc.}
    

    def remove_values_from_list(self, list, exclude):
        return [value for value in list if value != exclude] # return value in list if value isn't equal to wanted exclusion value


    def level_up_events(self, event, choices):
        # If player clicked with mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Get position of mouse and divide position to get the same values as within the surface
            mouse_pos_x, mouse_pos_y = pygame.mouse.get_pos()
            mouse_pos_x -= self.screen_width/4
            mouse_pos_y -= 3*self.screen_height/8

            # Creates the bonus upgrade if there have been less than 10 upgrades
            if self.num_upgrades <= 10:
                bonus_upgrade = list(choices.keys())[3] # Gets key of bonus upgrades
                choices.pop(bonus_upgrade) # Removes bonus upgrade from dictionary
                
                if bonus_upgrade == "PlayerSpeed":
                    self.settings.player_speed += self.settings.playerspeed_upgrade
                elif bonus_upgrade == "BulletSpeed":
                    self.settings.bullet_speed += self.settings.bulletspeed_upgrade
                elif bonus_upgrade == "Regeneration":
                    # Increase health by set amount with a cap at 1
                    if self.player.health_remaining <= (1-self.settings.regeneration_upgrade):
                        self.player.health_remaining += self.settings.regeneration_upgrade
                    else:
                        self.player.health_remaining = 1
                elif bonus_upgrade == "BulletSize":
                    self.bullet_width += self.settings.bulletsize_upgrade
                    self.bullet_height += self.settings.bulletsize_upgrade
                elif bonus_upgrade == "BulletFireSpeed":
                    self.settings.fire_bullet_ticks -= self.settings.bulletfirespeed_upgrade

            # If the mouse clicked a choice, give powerup and exit while loop
            for key, value in choices.items():
                if value.collidepoint(mouse_pos_x, mouse_pos_y):
                    if key == "PlayerSpeed":
                        self.settings.player_speed += self.settings.playerspeed_upgrade
                    elif key == "BulletSpeed":
                        self.settings.bullet_speed += self.settings.bulletspeed_upgrade
                    elif key == "Regeneration":
                        # Increase health by set amount with a cap at 1
                        if self.player.health_remaining <= (1-self.settings.regeneration_upgrade):
                            self.player.health_remaining += self.settings.regeneration_upgrade
                        else:
                            self.player.health_remaining = 1
                    elif key == "BulletSize":
                        self.bullet_width += self.settings.bulletsize_upgrade
                        self.bullet_height += self.settings.bulletsize_upgrade
                    elif key == "MultiBullet":
                        self.multibullet_timer += self.settings.multibullet_time_amount
                    elif key == "BulletFireSpeed":
                        self.settings.fire_bullet_ticks -= self.settings.bulletfirespeed_upgrade
                    elif key == "OneHitKill":
                        self.player.onehitkill = True
                        self.onehitkill_timer = self.settings.onehitkill_time_amount
                    return True
        
        # Quit game event check
        elif event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_q):
            pygame.quit()
            sys.exit()




    def draw_health_bar(self):
        bezel_size = 5

        surface = pygame.Surface((self.screen_width/2, self.screen_height/4), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.settings.bezel_color, pygame.Rect(0, 0, surface.get_width(), surface.get_height())) # Draw gray bezels
        pygame.draw.rect(surface, self.settings.heath_color, pygame.Rect(bezel_size, bezel_size, (surface.get_width() - bezel_size * 2) * self.player.health_remaining, surface.get_height() - bezel_size * 2)) # Draw health
        pygame.draw.rect(surface, self.settings.armor_color, pygame.Rect(bezel_size, bezel_size, (surface.get_width() - bezel_size * 2) * self.player.armor, surface.get_height() - bezel_size * 2)) # Draw armor on top
        self.screen.blit(surface, (self.screen_width/4, self.screen_height/4))


    
    def draw_xp_bar(self):
        bezel_size = 5

        surface = pygame.Surface((self.screen_width/2, self.screen_height/4), pygame.SRCALPHA)
        pygame.draw.rect(surface, self.settings.bezel_color, pygame.Rect(0, 0, surface.get_width(), surface.get_height()))
        pygame.draw.rect(surface, self.settings.xp_color, pygame.Rect(bezel_size, bezel_size, (surface.get_width() - bezel_size * 2) * self.player.xp/((self.xp_to_level_up*self.player.level)), surface.get_height() - bezel_size * 2))
        self.screen.blit(surface, (self.screen_width/4, self.screen_height/2))



    def draw_all(self):
        self.screen.fill((0, 0, 0))

        self.draw_health_bar()
        self.draw_xp_bar()

        if self.armor:
            self.screen.blit(self.armor.image, self.armor.rect)

        self.player.draw()
        for enemy in self.enemies:
            enemy.draw()
        for bullet in self.bullets:
            bullet.draw()

    def calculate_time(self):
        minutes = self.elapsed_time // 60 # Gets minutes by floor division
        seconds = self.elapsed_time % 60 # Gets seconds by finding remainder
        return f"{minutes:02}:{seconds:02}" # Formats minutes and seconds - 0 forces leading zero, 2 forces two characters
        
    def draw_time(self):
        time_str = self.calculate_time() # Calculates time

        # Draws time
        time = self.medium_font.render(time_str, True, (255, 255, 255))
        time_rect = time.get_rect(center=(self.screen_width/2, self.screen_height/8))
        self.screen.blit(time, time_rect.topleft)


    def title_screen(self):
        # Creates title
        title = self.title_font.render("Blob Destroyer", True, (255, 0, 0))
        title_rect = title.get_rect(center=(self.screen_width/2, self.screen_height/4))
        self.screen.blit(title, title_rect.topleft)

        # Creates medium text telling player how to start the game
        start_info = self.medium_font.render("Click anywhere to start", True, (255, 255, 255))
        start_info_rect = start_info.get_rect(center=(self.screen_width/2, 3*self.screen_height/4))
        self.screen.blit(start_info, start_info_rect.topleft)

        # Creates small text telling player how to play the game below the start game text
        keystroke_info = self.small_font.render("Use WASD or arrow keys to move", True, (255, 255, 255))
        mouse_info = self.small_font.render("Move your mouse to control where bullets are fired", True, (255, 255, 255))
        upgrade_info = self.small_font.render("Collect XP from killing enemies to level up your player", True, (255, 255, 255))
        goal_info = self.small_font.render("You have one life, survive for as long as you can!", True, (255, 255, 255))

        keystroke_rect = keystroke_info.get_rect(midtop=(self.screen_width/2, start_info_rect.midbottom[1]+50))
        mouse_rect = mouse_info.get_rect(midtop=(self.screen_width/2, keystroke_rect.midbottom[1]))
        upgrade_rect = upgrade_info.get_rect(midtop=(self.screen_width/2, mouse_rect.midbottom[1]))
        goal_rect = goal_info.get_rect(midtop=(self.screen_width/2, upgrade_rect.midbottom[1]))

        self.screen.blit(keystroke_info, keystroke_rect.topleft)
        self.screen.blit(mouse_info, mouse_rect.topleft)
        self.screen.blit(upgrade_info, upgrade_rect.topleft)
        self.screen.blit(goal_info, goal_rect.topleft)

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                # If X is clicked, quit game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # If Q is pressed, quit game
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()

                # If mouse button is pressed, leave function and start game
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1: # 1 = left mouse button
                        return

    
    def death_screen(self):
        death_background_surface = pygame.Surface((self.screen_width, self.screen_height))
        death_background_surface.set_alpha(150)
        death_background_surface.fill((0, 0, 0))
        self.screen.blit(death_background_surface, (0, 0))

        you_died = self.title_font.render("You Died", True, (255, 0, 0))
        you_died_rect = you_died.get_rect(center=(self.screen_width/2, self.screen_height/4))
        self.screen.blit(you_died, you_died_rect.topleft)

        retry = self.small_font.render("Press 'R' to retry", True, (255, 255, 255))
        retry_rect = retry.get_rect(center=(self.screen_width/2, 3*self.screen_height/4))
        self.screen.blit(retry, retry_rect.topleft)

        quit = self.small_font.render("Press 'Q' to quit", True, (255, 255, 255))
        quit_rect = quit.get_rect(midtop=(self.screen_width/2, retry_rect.bottom))
        self.screen.blit(quit, quit_rect.topleft)

        self.draw_time()
        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_r:
                        return True

            

# calls class and runs program
if __name__ == '__main__':
    game = BlobDestroyer()
    game.run_game()