from os.path import abspath, dirname
from pygame import *
import sys

FirstPath = dirname(__file__)
FontsPath = FirstPath + '/fonts/'
ImagesPath = FirstPath + '/images/'

White = (255, 255, 255)

Height = 800
Width = 600
screen = display.set_mode((Height, Width))

Font = FontsPath + 'alien_invasion.ttf'

EnemyInitiaPlace = 65 
Attack = 35 

class Text(object):
    def __init__(self, textFont, size, message, color, xcord, ycord):
        self.font = font.Font(textFont, size)
        self.surface = self.font.render(message, True, color)
        self.rect = self.surface.get_rect(topleft=(xcord, ycord))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

class Bullet(sprite.Sprite):
    def __init__(self, xpos, ypos, direction, speed, side):
        sprite.Sprite.__init__(self)
        self.image = image.load(ImagesPath + 'shot.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(xpos, ypos))
        self.speed = speed
        self.direction = direction
        self.side = side

    def update(self, keys, *args):
        start.screen.blit(self.image, self.rect)
        self.rect.y += self.speed * self.direction
        if self.rect.y < 15 or self.rect.y > 600:
            self.kill()

class Alien(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.images = []
        self.load_images()
        self.image = self.images[0]
        self.rect = self.image.get_rect()

    def update(self, *args):
        start.screen.blit(self.image, self.rect)

    def load_images(self):
        img1, img2 = (image.load(ImagesPath + 'enemy.png').convert_alpha() for i in
                      range(2))
        self.images.append(transform.scale(img1, (40, 35)))
        
class Ship(sprite.Sprite):
    def __init__(self):
        sprite.Sprite.__init__(self)
        self.image = image.load(ImagesPath + 'ship.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(375, 540))
        self.speed = 10

    def update(self, keys, *args):
        if keys[K_LEFT] and self.rect.x > 10:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < 740:
            self.rect.x += self.speed
        start.screen.blit(self.image, self.rect)
        
class AliensGroup(sprite.Group):
    def __init__(self, columns, rows):
        sprite.Group.__init__(self)
        self.aliens = [[None] * columns for _ in range(rows)]
        self.columns = columns
        self.rows = rows
        self.leftAddMove = 0
        self.rightAddMove = 0
        self.moveTime = 600
        self.moveNumber = 15
        self.direction = 1
        self.rightMoves = 30
        self.leftMoves = 30
        self.timer = time.get_ticks()
        self.bottom = start.enemyPosition + ((rows - 1) * 45) + 35
        self._aliveColumns = list(range(columns))
        self._leftAliveColumn = 0
        self._rightAliveColumn = columns - 1

    def update(self, current_time):
        if current_time - self.timer > self.moveTime:
            if self.direction == 1:
                max_move = self.rightMoves + self.rightAddMove
            else:
                max_move = self.leftMoves + self.leftAddMove

            if self.moveNumber >= max_move:
                self.leftMoves = 30 + self.rightAddMove
                self.rightMoves = 30 + self.leftAddMove
                self.direction *= -1
                self.moveNumber = 0
                self.bottom = 0
                for enemy in self:
                    enemy.rect.y += Attack
                    if self.bottom < enemy.rect.y + 35:
                        self.bottom = enemy.rect.y + 35
            else:
                velocity = 10 if self.direction == 1 else -10
                for enemy in self:
                    enemy.rect.x += velocity
                self.moveNumber += 1
                
            self.timer += self.moveTime

    def column_dead(self, col):
        return not any(self.aliens[row][col]
                       for row in range(self.rows))

    def kill(self, alien):
        self.aliens[alien.row][alien.column] = None
        column_dead = self.column_dead(enemy.column)
        if column_dead:
            self._aliveColumns.remove(alien.column)

        if alien.column == self._rightAliveColumn:
            while self._rightAliveColumn > 0 and column_dead:
                self._rightAliveColumn -= 1
                self.rightAddMove += 5
                column_dead = self.column_dead(self._rightAliveColumn)

        elif enemy.column == self._leftAliveColumn:
            while self._leftAliveColumn < self.columns and column_dead:
                self._leftAliveColumn += 1
                self.leftAddMove += 5
                column_dead = self.column_dead(self._leftAliveColumn)


class ShipExplosion(sprite.Sprite):
    def __init__(self, ship, *groups):
        super(ShipExplosion, self).__init__(*groups)
        self.image = image.load(ImagesPath + 'ship.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=(ship.rect.x, ship.rect.y))
        self.timer = time.get_ticks()

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if 300 < passed <= 600:
            start.screen.blit(self.image, self.rect)
        elif 900 < passed:
            self.kill()

class AlienInvasion(object):
    def __init__(self):
        init()
        self.caption = display.set_caption('Alien Invasion')
        self.clock = time.Clock()
        self.screen = screen
        self.background = image.load(ImagesPath + 'space.jpg').convert()
        self.enemyPosition = 65
        self.Title = Text(Font, 50, 'Alien Invasion', White, 164, 155)
        self.PressKey = Text(Font, 25, 'Press a key to continue', White, 201, 225)
        self.nextRoundText = Text(Font, 50, 'Next Wave', White, 240, 270)
        self.startGame = False
        self.mainScreen = True
        self.gameOver = False

    def reset(self):
        self.explosionsGroup = sprite.Group()
        self.bullets = sprite.Group()
        self.player = Ship()
        self.playerGroup = sprite.Group(self.player)
        self.Make_Aliens()
        self.allSprites = sprite.Group(self.player, self.aliens)
        self.keys = key.get_pressed()
        self.noteTimer = time.get_ticks()
        self.timer = time.get_ticks()
        self.shipTimer = time.get_ticks()
        self.shipAlive = True
        self.makeNewShip = False

    @staticmethod
    def Exit(evt):
        return evt.type == QUIT or (evt.type == KEYUP and evt.key == K_ESCAPE)

    def Ch_Input(self):
        self.keys = key.get_pressed()
        for e in event.get():
            if self.Exit(e):
                sys.exit()
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    bullet = Bullet(self.player.rect.x + 23,
                                    self.player.rect.y + 5, -1,
                                    15, 'center')
                    self.bullets.add(bullet)
                    self.allSprites.add(self.bullets)

    def Make_Aliens(self):
        aliens = AliensGroup(10, 6)
        for row in range(6):
            for col in range(10):
                alien = Alien()
                x_shift = 50
                y_shift = 40
                alien.rect.x = 157 + (col * x_shift)
                alien.rect.y = self.enemyPosition + (row * y_shift)
                aliens.add(alien)
        self.aliens = aliens

    def Collisions(self):
        for enemy in sprite.groupcollide(self.aliens, self.bullets,
                                         True, True).keys():
            self.gameTimer = time.get_ticks()

        if self.aliens.bottom >= 540:
            sprite.groupcollide(self.aliens, self.playerGroup, True, True)
            if not self.player.alive() or self.aliens.bottom >= 600:
                self.gameOver = True
                self.startGame = False

    def Ship_New(self, createShip, currentTime):
        if createShip and (currentTime - self.shipTimer > 900):
            self.player = Ship()
            self.allSprites.add(self.player)
            self.playerGroup.add(self.player)
            self.makeNewShip = False
            self.shipAlive = True

    def You_Lost(self, currentTime):
        self.mainScreen = True

    def main(self):
        while True:
            if self.mainScreen:
                self.screen.blit(self.background, (0, 0))
                self.Title.draw(self.screen)
                self.PressKey.draw(self.screen)
                for e in event.get():
                    if self.Exit(e):
                        sys.exit()
                    if e.type == KEYUP:
                        self.reset()
                        self.startGame = True
                        self.mainScreen = False

            elif self.startGame:
                if not self.aliens and not self.explosionsGroup:
                    currentTime = time.get_ticks()
                    if currentTime - self.gameTimer < 3000:
                        self.screen.blit(self.background, (0, 0))
                        self.nextRoundText.draw(self.screen)
                        self.Ch_Input()
                    elif currentTime - self.gameTimer > 3000:
                        self.enemyPosition += Attack
                        self.reset()
                        self.gameTimer += 3000
                else:
                    currentTime = time.get_ticks()
                    self.screen.blit(self.background, (0, 0))
                    self.Ch_Input()
                    self.aliens.update(currentTime)
                    self.allSprites.update(self.keys, currentTime)
                    self.explosionsGroup.update(currentTime)
                    self.Collisions()
                    self.Ship_New(self.makeNewShip, currentTime)

            elif self.gameOver:
                currentTime = time.get_ticks()
                self.enemyPosition = 65
                self.You_Lost(currentTime)

            display.update()
            self.clock.tick(60)

if __name__ == '__main__':
    start = AlienInvasion()
    start.main()
