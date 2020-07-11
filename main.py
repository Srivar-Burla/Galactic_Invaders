# Importing relevant libraries
import pygame
import os
import random

# To use font objects, we need to initialize fonts in Pygame before creating Font Objects.
# Further Explanation about font Objects in PyGame is given where it is first used
pygame.font.init()

# Defining the size of the Game Window and setting a Caption
length,breadth = 900,900
Window = pygame.display.set_mode((length, breadth))
pygame.display.set_caption("Galactic Invasion")

# Setting the Screen refresh Rate (FPS)
FPS = 120

# Loading Images
red_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
green_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
blue_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Loading Player modelImage
yellow_space_ship = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

#Loading Laser Images
red_laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
green_laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
blue_laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
yellow_laser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# Loading the Background Image and Scaling it to fit the Game Window
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (length,breadth))

# Defining an abstract Ship Class. It wont be used Directly.
# Instead, we will be inheriting this class's properties to build our enemy as well as Player Ships.
# This is because all the ships in this game will have properties that are mostly common.
class Ship:
    COOLDOWN = FPS * 0.25

    def __init__(self, x, y, health = 100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self,velocity,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(breadth):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)



    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1


    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.ship_img.get_width()//2, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1


    def get_dimension(self):
        return self.ship_img.get_width(),self.ship_img.get_height()

class Player(Ship):
    def __init__(self,x,y,Score = 0,health = 100):
        # super() is used to load up attributes and methods of the main class into the derived class
        super().__init__(x, y, health)
        self.ship_img = yellow_space_ship
        self.laser_img = yellow_laser
        self.Score = Score
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self,velocity,objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(velocity)
            if laser.off_screen(breadth):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        self.Score += 1
                        self.lasers.remove(laser)

    def healthbar(self,window):
        pygame.draw.rect(window,(255,0,0),(self.x,self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window,(0,255,0),(self.x,self.y + self.ship_img.get_height() + 10, int(self.ship_img.get_width()*(self.health/self.max_health)), 10))

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)


class Enemy(Ship):
    Colour_Map = {
                    "red"   : (red_space_ship,red_laser),
                    "green" : (green_space_ship,green_laser),
                    "blue"  : (blue_space_ship,blue_laser)
                 }

    def __init__(self, x, y, colour, health = 100):
        super().__init__(x,y,health)
        self.ship_img, self.laser_img = self.Colour_Map[colour]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move(self,velocity):
        self.y += velocity

class Laser:
    def __init__(self,x,y,img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self,window):
        window.blit(self.img,(self.x,self.y))

    def move(self,velocity):
        self.y += velocity

    def off_screen(self,height):
        return not(self.y<=breadth and self.y >= 0)

    def collision(self,obj):
        return collide(obj,self)

def collide(obj1,obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask,(offset_x,offset_y)) != None #returns (x,y) where they collide

def main():

    '''
    This is the Main Function that will should be run to start the game.
    It will contain all the required Function calls when required.
    Also, other Game Variables will be defined here.
    '''

    run = True

    # Other Game Variables
    level = 0
    lives = 5
    player_velocity = 3
    enemy_velocity = 1
    laser_velocity = 4
    enemies = []
    wave_length = 5
    prob_enemy_shot = 0.5 # Probability of the enemy firing a laser in each second

    player = Player((length - yellow_space_ship.get_width())//2,breadth - yellow_space_ship.get_height() - 15)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    # Inorder to Display Text in Pygame, We need to first create a font object and the use it to display font on the Game Window
    main_font = pygame.font.SysFont("comicsans",50)
    lost_font = pygame.font.SysFont("comicsans",50)

    def redraw_window():
        '''
         redraw_window() is the function responsible for redrawing the entire game window once for every new frame.

         Every new Frame will Start by Drawing the Background, level and lives labels,
         followed by the various ships and their lasers to be displayed at their updated positions.

        '''

        # blit method is used to paste Images on the Game Window at the given location.
        # Subsequent blits paste images over the previous blit
        # Note: In Pygame, x coordinate increases rightward as usual.
        #       But the y coordinate increases Downward
        Window.blit(BG, (0, 0))

        # Blitting labels and lives text
        offset = 10
        lives_label = main_font.render(f"Lives: {lives}",1,(255,255,255))
        level_label = main_font.render(f"Level: {level}",1,(255,255,255))
        Score_label = main_font.render(f"Score: {player.Score}",1,(255,255,255))



        for enemy in enemies:
            enemy.draw(Window)

        player.draw(Window)

        Window.blit(lives_label, (offset, offset))
        Window.blit(level_label, (length - level_label.get_width() - offset, offset))
        Window.blit(Score_label, ((length - Score_label.get_width()) // 2, offset))

        if lost:
            lost_label = lost_font.render("Your Civilization has been Annihilated !!!",1,(255,0,0))
            Window.blit(lost_label,((length - lost_label.get_width())//2,(breadth - lost_font.get_height())//2))


        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if (lives <= 0) or (player.health <= 0):
            lost = True
            lost_count += 1

        for enemy in enemies:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)
            
            if random.randrange(0, FPS/prob_enemy_shot) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)
            elif enemy.y + enemy.get_dimension()[1]>breadth:
                lives-=1
                enemies.remove(enemy)



        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue


        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50,length - 50),random.randrange(-1500 - level*250,-100), random.choice(["red","green","blue"]))
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            else:
                pass
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_velocity > 0: # Move Left
            player.x -= player_velocity
        if keys[pygame.K_RIGHT] and player.x + player_velocity + player.get_dimension()[0]< length: # Move Right
            player.x += player_velocity
        if keys[pygame.K_UP] and player.y - player_velocity - main_font.get_height() > 0: # Move Up
            player.y -= player_velocity
        if keys[pygame.K_DOWN] and player.y + player_velocity + player.get_dimension()[1] + 15 < breadth: # Move Down
            player.y += player_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()
            
            
        player.move_lasers(-laser_velocity,enemies)


def Intro_Screen():
    title_font = pygame.font.SysFont("comicsans",70)
    run = True
    while run:
        Window.blit(BG,(0,0))
        title_label = title_font.render("Welcome to the Galactic Invaders",1,(0,255,255))
        Intro_label = title_font.render("Click the Mouse to Begin...",1,(255,255,255))
        Window.blit(title_label,(length/2 - title_label.get_width()//2, breadth/2 - title_font.get_height()))
        Window.blit(Intro_label,(length/2 - Intro_label.get_width()//2, breadth/2))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()

Intro_Screen()
