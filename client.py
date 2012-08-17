#! /usr/bin/python

import sys, pygame, time
import socket
try:
    import cPickle as pickle
except:
    import pickle
from math import sin, cos, pi
from operator import mod


class Heli:
    def __init__(self, l):
        self.heli = pygame.image.load(l[5])
        self.path = l[5]
        self.speed = [0.0, 0.0]
        self.helirect = self.heli.get_rect()
        self.helirect = self.helirect.move(l[2], l[3])
        self.rots = l[4]
        self.rot('left')
        self.rot('right')
        self.ID = l[1]
        self.hits = 0
        # tip, ID, x, y, rot, path

    # val is used to see from what heli the move() method has beed called
    # 1 means from this client's heli, 0 means the other client's heli
    # Hope will fix this too.
    def move(self, key_list, val = 1):
        var = 0
        if key_list[0]:
            self.accel(MAX_SPEED)
        else:
            self.slow_down(MAX_SPEED)

        if key_list[1]:
            self.rot('left', val)
            var = 1

        if key_list[2]:
            self.rot('right', val)
            var = 1

        self.check()
        self.helirect = self.helirect.move(self.speed)
        if val:
            screen.blit(self.heli, self.helirect)
        elif not var:
            screen.blit(self.heli, self.helirect)

    def accel(self, v):
        if self.helirect.left > 0 or self.helirect.right < width:
            self.speed[0] = v * cos(mod(self.rots, 36) /18 * pi)
        else:
            self.speed[0] = 0.0

        if self.helirect.top > 0 or self.helirect.bottom < height:
            self.speed[1] = -v * sin(mod(self.rots, 36) /18 * pi)
        else:
            self.speed[1] = 0.0

    def slow_down(self, v):
        self.accel(v/2)

    def rot(self, direction, val = 1):
        blittedRect = screen.blit(self.heli, self.helirect)
        oldCenter = blittedRect.center
        self.heli = pygame.image.load(self.path)
        if direction == 'left':
            rotHeli = pygame.transform.rotate(self.heli, ANGLE * self.rots)
            self.rots += 1
        else:
            rotHeli = pygame.transform.rotate(self.heli, ANGLE * (self.rots
                -1))
            self.rots -= 1

        rotRect = rotHeli.get_rect()
        rotRect.center = oldCenter
        if val:
            screen.blit(rotHeli, rotRect)
        self.heli= rotHeli
        self.helirect = rotRect

    def check(self):
        if self.helirect.left < 0 or self.helirect.right > width:
            self.speed[0] = 0.0
        if self.helirect.top < 0 or self.helirect.bottom > height:
            self.speed[1] = 0.0

    def fire(self):
        bullet = Bullet('bullet.png', self)
        return bullet

class Bullet:
    def __init__(self, path, heli):
        self.heli = heli
        self.path = path
        self.bullet = pygame.image.load(path)
        self.speed = [0.0, 0.0]
        self.bulletrect = self.bullet.get_rect()
        center = heli.helirect.center
        self.bulletrect = self.bulletrect.move(center[0], center[1])
        self.rots = self.heli.rots

    def move(self):
        self.accel(BULLET_SPEED)
        value = self.check()
        self.bulletrect = self.bulletrect.move(self.speed)
        screen.blit(self.bullet, self.bulletrect)
        return value

    def accel(self, v):
        if self.bulletrect.left > 0 or self.bulletrect.right < width:
            self.speed[0] = v * cos(mod(self.rots, 36) / 18 * pi)
        if self.bulletrect.top > 0 or self.bulletrect.bottom < height:
            self.speed[1] = -v * sin(mod(self.rots, 36) / 18 * pi)

    def check(self):
        if self.bulletrect.left < 0 or self.bulletrect.right > width:
            return 0
        if self.bulletrect.top < 0 or self.bulletrect.bottom > height:
            return 0
        return 1

MAX_SPEED = 10
BULLET_SPEED = 15
ANGLE = 10

if len(sys.argv) != 3:
    sys.exit(sys.argv[0] + ' HOST PORT')

SERVER_HOST = sys.argv[1]
SERVER_PORT = int(sys.argv[2])
MAX_SIZE = 4096

sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd.connect((SERVER_HOST, SERVER_PORT))

pygame.init()
pygame.display.set_caption('Sky Warriors@IPW2012')
background = pygame.image.load("cer.jpg")
backgroundRect = background.get_rect()
size = width, height = background.get_size()
screen = pygame.display.set_mode(size)
bullet_list = []
player_list = []

answer = sockfd.recv(MAX_SIZE)
tmp_list = pickle.loads(answer)
my_heli = Heli(tmp_list)

# This should receive the list with all players already connected to the
# server and create a Heli() object for each one of them, but it doesn't
# work quite ok so far.
#
#answer = sockfd.recv(MAX_SIZE)
#tmp_list2 = pickle.loads(answer)
#print '2 - recv', tmp_list2

#for elem in tmp_list2:
#    print elem
#    if elem != tmp_list:
#        new_player = Heli(elem)
#        player_list.append(new_player)

prev_bullet = pygame.time.get_ticks() # this is used to measure the time
                                      # between consecutive bullets
var = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sockfd.sendall('QUIT' + str(my_heli.ID))
            sys.exit()

    key_list = [0, 0, 0]
    key_list[0] = pygame.key.get_pressed()[pygame.K_UP]
    key_list[1] = pygame.key.get_pressed()[pygame.K_LEFT]
    key_list[2] = pygame.key.get_pressed()[pygame.K_RIGHT]

    # This is how it should work:
    #if key_list != [0, 0, 0]:
    my_heli.move(key_list, 1)

    # sending our data
    tmp_list = [1, my_heli.ID, key_list]
    str_to_send = pickle.dumps(tmp_list)
    sockfd.sendall(str_to_send)

    heli_center = my_heli.helirect.center

    if pygame.key.get_pressed()[pygame.K_SPACE]:
        crt_bullet = pygame.time.get_ticks()

        if crt_bullet - prev_bullet > 700:
            bullet = my_heli.fire()
            tmp_l = [2, my_heli.ID]
            tmp = pickle.dumps(tmp_l)
            sockfd.sendall(tmp)
            bullet_list.append(bullet)
            prev_bullet = crt_bullet

    # other helis' data
    answer = sockfd.recv(MAX_SIZE)
    tmp_list2 = pickle.loads(answer)
    screen.blit(background, backgroundRect)

    if tmp_list2[0] == 0: # new player joined; this isn't working atm
        new_player = Heli(tmp_list2)
        player_list.append(new_player)

    elif tmp_list2[0] == 1: # some player changed his rotation or speed
                            # (pressed some keys)
        # A problem here is that we receive data from the first player, but
        # not the actual first [0] message, right before the main loop. So,
        # the temporary solution was to look for that player.ID and if it's
        # not already in our list to add it now.
        for player in player_list:
            if player.ID == tmp_list2[1] and my_heli.ID != tmp_list2[1]:
                player_key_list = tmp_list2[2]
                player.move(player_key_list, 0)
                break
        else:
            tmp_l = [0, tmp_list2[1], 500, 500, 10.0, 'img1.png']
            new_player = Heli(tmp_l)
            player_list.append(new_player)

    elif tmp_list2[0] == -1: # some player disconnected
        for player in player_list[:]:
            if player.ID == tmp_list2[1]:
                player_list.remove(player)

    elif tmp_list2[0] == 2: # some player fired a bullet
        for player in player_list:
            if player.ID == tmp_list2[1]:
                bullet = player.fire()
                bullet_list.append(bullet)

    for obj in bullet_list[:]:
        value = obj.move()
        for player in player_list:
            if player.helirect.colliderect(obj.bulletrect) and obj.heli.ID != player.ID:
                player.hits += 1
                bullet_list.remove(obj)

                if player.hits == 3:
                    myfont = pygame.font.SysFont("Arial", 30)
                    label = myfont.render("YOU WON!", 1, black)
                    screen.blit(label, (300, 300))
                    pygame.display.flip()
                    time.sleep(10)

        if my_heli.helirect.colliderect(obj.bulletrect) and obj.heli.ID != my_heli.ID:
            my_heli.hits += 1
            bullet_list.remove(obj)

            if my_heli.hits == 3:
                myfont = pygame.font.SysFont("Arial", 30)
                label = myfont.render("YOU LOST!", 1, black)
                screen.blit(label, (300, 300))
                pygame.display.flip()
                time.sleep(10)

        if value == 0: # if the bullet got beyond borders
           bullet_list.remove(obj)
        else:
            screen.blit(obj.bullet, obj.bulletrect)

    screen.blit(my_heli.heli, my_heli.helirect)
    pygame.display.flip()
    pygame.time.delay(20)

