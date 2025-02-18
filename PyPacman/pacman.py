import copy
from board import boards
import pygame
import math

pygame.init()

#Cargar los sprites (sustituye por la ruta absoluta de la carpeta de assets (selecciona la carpeta de assets y presiona: Shift+Alt+C))

relative_player = r"C:\Users\mgur2\OneDrive\Documentos\URU\11trim\Videojuegos\Basic-Pacman\PyPacman\assets\player_images"
relative_ghost = r"C:\Users\mgur2\OneDrive\Documentos\URU\11trim\Videojuegos\Basic-Pacman\PyPacman\assets\ghost_images"

# relative_player = r"tu\ruta\definitiva\Basic-Pacman\PyPacman\assets\player_images"
# relative_ghost = r"tu\ruta\definitiva\Basic-Pacman\PyPacman\assets\ghost_images"

#Dimensiones de la pantalla y velocidad de animación
WIDTH = 900
HEIGHT = 950
screen = pygame.display.set_mode([WIDTH, HEIGHT])
timer = pygame.time.Clock()
fps = 60
font = pygame.font.Font('freesansbold.ttf', 20)

#Copia del tablero y color del mismo
level = copy.deepcopy(boards)
color = 'blue'
PI = math.pi

#Carga de las imagenes del juego (Pacman y Fantasmas)
player_images = []
for i in range(1, 5):
    player_images.append(pygame.transform.scale(pygame.image.load(f'{relative_player}\{i}.png'), (45, 45)))
blinky_img = pygame.transform.scale(pygame.image.load(rf'{relative_ghost}\red.png'), (45, 45))
pinky_img = pygame.transform.scale(pygame.image.load(rf'{relative_ghost}\pink.png'), (45, 45))
inky_img = pygame.transform.scale(pygame.image.load(rf'{relative_ghost}\blue.png'), (45, 45))
clyde_img = pygame.transform.scale(pygame.image.load(rf'{relative_ghost}\orange.png'), (45, 45))
spooked_img = pygame.transform.scale(pygame.image.load(rf'{relative_ghost}\powerup.png'), (45, 45))
dead_img = pygame.transform.scale(pygame.image.load(rf'{relative_ghost}\dead.png'), (45, 45))

#Posición inicial del Pacman y los fantasmas
player_x = 450
player_y = 663
direction = 0
blinky_x = 56
blinky_y = 58
blinky_direction = 0
inky_x = 440
inky_y = 388
inky_direction = 2
pinky_x = 440
pinky_y = 438
pinky_direction = 2
clyde_x = 440
clyde_y = 438
clyde_direction = 2
counter = 0
flicker = False

# Variables para controlar el movimiento del Pacman y los fantasmas
# Conjunto de movimientos permitidos (Derecha, Izquierda, Arriba y Abajo)
turns_allowed = [False, False, False, False]
direction_command = 0
player_speed = 2
score = 0
powerup = False
power_counter = 0

# Variables para controlar la muerte y la victoria del juego
eaten_ghost = [False, False, False, False]
targets = [(player_x, player_y), (player_x, player_y), (player_x, player_y), (player_x, player_y)]
blinky_dead = False
inky_dead = False
clyde_dead = False
pinky_dead = False
blinky_box = False
inky_box = False
clyde_box = False
pinky_box = False
moving = False
ghost_speeds = [2, 2, 2, 2]
startup_counter = 0
lives = 3
game_over = False
game_won = False


class Ghost:
    def __init__(self, x_coord, y_coord, target, speed, img, direct, dead, box, id):
        self.x_pos = x_coord
        self.y_pos = y_coord
        self.center_x = self.x_pos + 22
        self.center_y = self.y_pos + 22
        self.target = target
        self.speed = speed
        self.img = img
        self.direction = direct
        self.dead = dead
        self.in_box = box
        self.id = id
        self.turns, self.in_box = self.check_collisions()
        self.rect = self.draw()

#Metodo para dibujar al fantasma segun su estado (normal, superpastilla, comido)
    def draw(self):
        if (not powerup and not self.dead) or (eaten_ghost[self.id] and powerup and not self.dead):
            screen.blit(self.img, (self.x_pos, self.y_pos))
        elif powerup and not self.dead and not eaten_ghost[self.id]:
            screen.blit(spooked_img, (self.x_pos, self.y_pos))
        else:
            screen.blit(dead_img, (self.x_pos, self.y_pos))
        ghost_rect = pygame.rect.Rect((self.center_x - 18, self.center_y - 18), (36, 36))
        return ghost_rect

    def check_collisions(self):
        # Ancho y alto de cada celda del mapa
        num1 = ((HEIGHT - 50) // 32)
        num2 = (WIDTH // 30)
        # Margen de la hitbox
        num3 = 15
        self.turns = [False, False, False, False]
        # Verificar que el fantasma este dentro del mapa
        if 0 < self.center_x // 30 < 29:
            # Verifica si puede moverse hacia arriba
            if level[(self.center_y - num3) // num1][self.center_x // num2] == 9:
                self.turns[2] = True
            # Verifica si puede moverse hacia la izquierda
            if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[1] = True
            # Verifica si puede moverse hacia la derecha
            if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                    or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[0] = True
            # Verifica si puede moverse hacia abajo
            if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[3] = True
            if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                    or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                    self.in_box or self.dead)):
                self.turns[2] = True
            # Verificar giros adicionales basados en la direccion actual
            if self.direction == 2 or self.direction == 3: #Si se mueve hacia arriba o abajo
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num2) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num2) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True

            if self.direction == 0 or self.direction == 1: #Si se mueve a la derecha o la izquierda
                if 12 <= self.center_x % num2 <= 18:
                    if level[(self.center_y + num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y + num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[3] = True
                    if level[(self.center_y - num3) // num1][self.center_x // num2] < 3 \
                            or (level[(self.center_y - num3) // num1][self.center_x // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[2] = True
                if 12 <= self.center_y % num1 <= 18:
                    if level[self.center_y // num1][(self.center_x - num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x - num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[1] = True
                    if level[self.center_y // num1][(self.center_x + num3) // num2] < 3 \
                            or (level[self.center_y // num1][(self.center_x + num3) // num2] == 9 and (
                            self.in_box or self.dead)):
                        self.turns[0] = True
        else:
            self.turns[0] = True
            self.turns[1] = True
        # Si el fantasma está en la caja central 
        if 350 < self.x_pos < 550 and 370 < self.y_pos < 480:
            self.in_box = True
        else:
            self.in_box = False
        return self.turns, self.in_box

    def move_clyde(self):
        # r, l, u, d (right, left, up, down)
        # Clyde se moverá siempre y cuando sea favorable para la persecución
        if self.direction == 0:  # Si Clyde se mueve a la derecha
            if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                self.x_pos += self.speed
            elif not self.turns[0]:  # Si no puede moverse a la derecha
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:  # Si puede moverse a la derecha
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:  # Si Clyde se mueve a la izquierda
            if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                self.x_pos -= self.speed
            elif not self.turns[1]:  # Si no puede moverse a la izquierda
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:  # Si puede moverse a la izquierda
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:  # Si Clyde se mueve hacia arriba
            if self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:  # Si no puede moverse hacia arriba
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:  # Si puede moverse hacia arriba
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:  # Si Clyde se mueve hacia abajo
            if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                self.y_pos += self.speed
            elif not self.turns[3]:  # Si no puede moverse hacia abajo
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:  # Si puede moverse hacia abajo
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed

        # Si Clyde sale del borde izquierdo de la pantalla, reaparece en el borde derecho
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:  # Si Clyde sale del borde derecho de la pantalla, reaparece en el borde izquierdo
            self.x_pos = -30

        return self.x_pos, self.y_pos, self.direction

    def move_blinky(self):
        # r, l, u, d (right, left, up, down)
        # Blinky va a girar siempre que choque con paredes, de lo contrario continuará recto
        if self.direction == 0:  # Si Blinky se mueve a la derecha
            if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                self.x_pos += self.speed
            elif not self.turns[0]:  # Si no puede moverse a la derecha
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:  # Si puede moverse a la derecha
                self.x_pos += self.speed
        elif self.direction == 1:  # Si Blinky se mueve a la izquierda
            if self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                self.x_pos -= self.speed
            elif not self.turns[1]:  # Si no puede moverse a la izquierda
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:  # Si puede moverse a la izquierda
                self.x_pos -= self.speed
        elif self.direction == 2:  # Si Blinky se mueve hacia arriba
            if self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:  # Si no puede moverse hacia arriba
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[2]:  # Si puede moverse hacia arriba
                self.y_pos -= self.speed
        elif self.direction == 3:  # Si Blinky se mueve hacia abajo
            if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                self.y_pos += self.speed
            elif not self.turns[3]:  # Si no puede moverse hacia abajo
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[3]:  # Si puede moverse hacia abajo
                self.y_pos += self.speed

        # Si Blinky sale del borde izquierdo de la pantalla, reaparece en el borde derecho
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:  # Si Blinky sale del borde derecho de la pantalla, reaparece en el borde izquierdo
            self.x_pos = -30

        return self.x_pos, self.y_pos, self.direction

    def move_inky(self):
        # r, l, u, d (right, left, up, down)
        # Inky gira hacia arriba o hacia abajo en cualquier momento para perseguir al jugador, pero a la izquierda y derecha solo en colisión
        if self.direction == 0:  # Si Inky se mueve a la derecha
            if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                self.x_pos += self.speed
            elif not self.turns[0]:  # Si no puede moverse a la derecha
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:  # Si puede moverse a la derecha
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos += self.speed
        elif self.direction == 1:  # Si Inky se mueve a la izquierda
            if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                self.x_pos -= self.speed
            elif not self.turns[1]:  # Si no puede moverse a la izquierda
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:  # Si puede moverse a la izquierda
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                if self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                else:
                    self.x_pos -= self.speed
        elif self.direction == 2:  # Si Inky se mueve hacia arriba
            if self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:  # Si no puede moverse hacia arriba
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:  # Si puede moverse hacia arriba
                self.y_pos -= self.speed
        elif self.direction == 3:  # Si Inky se mueve hacia abajo
            if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                self.y_pos += self.speed
            elif not self.turns[3]:  # Si no puede moverse hacia abajo
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:  # Si puede moverse hacia abajo
                self.y_pos += self.speed

        # Si Inky sale del borde izquierdo de la pantalla, reaparece en el borde derecho
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:  # Si Inky sale del borde derecho de la pantalla, reaparece en el borde izquierdo
            self.x_pos = -30

        return self.x_pos, self.y_pos, self.direction

    def move_pinky(self):
        # r, l, u, d (right, left, up, down)
        # Pinky va a girar a la izquierda o derecha siempre que sea ventajoso, pero solo hacia arriba o abajo en colisión
        if self.direction == 0:  # Si Pinky se mueve a la derecha
            if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                self.x_pos += self.speed
            elif not self.turns[0]:  # Si no puede moverse a la derecha
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
            elif self.turns[0]:  # Si puede moverse a la derecha
                self.x_pos += self.speed
        elif self.direction == 1:  # Si Pinky se mueve a la izquierda
            if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                self.direction = 3
            elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                self.x_pos -= self.speed
            elif not self.turns[1]:  # Si no puede moverse a la izquierda
                if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[1]:  # Si puede moverse a la izquierda
                self.x_pos -= self.speed
        elif self.direction == 2:  # Si Pinky se mueve hacia arriba
            if self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                self.direction = 1
                self.x_pos -= self.speed
            elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                self.direction = 2
                self.y_pos -= self.speed
            elif not self.turns[2]:  # Si no puede moverse hacia arriba
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[3]:  # Si puede moverse hacia abajo
                    self.direction = 3
                    self.y_pos += self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[2]:  # Si puede moverse hacia arriba
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos -= self.speed
        elif self.direction == 3:  # Si Pinky se mueve hacia abajo
            if self.target[1] > self.y_pos and self.turns[3]:  # Si el objetivo está abajo y puede moverse hacia abajo
                self.y_pos += self.speed
            elif not self.turns[3]:  # Si no puede moverse hacia abajo
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.target[1] < self.y_pos and self.turns[2]:  # Si el objetivo está arriba y puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[2]:  # Si puede moverse hacia arriba
                    self.direction = 2
                    self.y_pos -= self.speed
                elif self.turns[1]:  # Si puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                elif self.turns[0]:  # Si puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
            elif self.turns[3]:  # Si puede moverse hacia abajo
                if self.target[0] > self.x_pos and self.turns[0]:  # Si el objetivo está a la derecha y puede moverse a la derecha
                    self.direction = 0
                    self.x_pos += self.speed
                elif self.target[0] < self.x_pos and self.turns[1]:  # Si el objetivo está a la izquierda y puede moverse a la izquierda
                    self.direction = 1
                    self.x_pos -= self.speed
                else:
                    self.y_pos += self.speed

        # Si Pinky sale del borde izquierdo de la pantalla, reaparece en el borde derecho
        if self.x_pos < -30:
            self.x_pos = 900
        elif self.x_pos > 900:  # Si Pinky sale del borde derecho de la pantalla, reaparece en el borde izquierdo
            self.x_pos = -30

        return self.x_pos, self.y_pos, self.direction


#Esta funcion dibuja la UI del juego
def draw_misc():
    score_text = font.render(f'Score: {score}', True, 'white')
    screen.blit(score_text, (10, 90))
    if powerup:
        pygame.draw.circle(screen, 'blue', (140, 930), 15)
    for i in range(lives):
        screen.blit(pygame.transform.scale(player_images[0], (30, 30)), (650 + i * 40, 90))
    if game_over:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Game over! Space bar to restart!', True, 'red')
        puntuation_text = font.render(f"Your Score: {score} points!", True, "blue")
        screen.blit(puntuation_text, (100, 350))
        screen.blit(gameover_text, (100, 300))
    if game_won:
        pygame.draw.rect(screen, 'white', [50, 200, 800, 300],0, 10)
        pygame.draw.rect(screen, 'dark gray', [70, 220, 760, 260], 0, 10)
        gameover_text = font.render('Victory! Space bar to restart!', True, 'green')
        screen.blit(gameover_text, (100, 300))
        screen.blit(puntuation_text, (100, 350))

#Chequea
def check_collisions(scor, power, power_count, eaten_ghosts):
    num1 = (HEIGHT - 50) // 32
    num2 = WIDTH // 30
    if 0 < player_x < 870:
        if level[center_y // num1][center_x // num2] == 1:
            level[center_y // num1][center_x // num2] = 0
            scor += 10
        if level[center_y // num1][center_x // num2] == 2:
            level[center_y // num1][center_x // num2] = 0
            scor += 50
            power = True
            power_count = 0
            eaten_ghosts = [False, False, False, False]
    return scor, power, power_count, eaten_ghosts

#Dibuja el tablero dependiendo del tipo de Celda
def draw_board():
    #Alto y ancho de la celda
    num1 = ((HEIGHT - 50) // 32)
    num2 = (WIDTH // 30)

    #itera sobre cada celda del nivel y dependiendo del tipo de celda
    for i in range(len(level)):
        for j in range(len(level[i])):
            if level[i][j] == 1: #pellets
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 4)
            if level[i][j] == 2 and not flicker: # Super Pellets
                pygame.draw.circle(screen, 'white', (j * num2 + (0.5 * num2), i * num1 + (0.5 * num1)), 10)
            if level[i][j] == 3: #pared
                pygame.draw.line(screen, color, (j * num2 + (0.5 * num2), i * num1),
                                 (j * num2 + (0.5 * num2), i * num1 + num1), 3)
            if level[i][j] == 4: #pared
                pygame.draw.line(screen, color, (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)
            if level[i][j] == 5: #esquina
                pygame.draw.arc(screen, color, [(j * num2 - (num2 * 0.4)) - 2, (i * num1 + (0.5 * num1)), num2, num1],
                                0, PI / 2, 3)
            if level[i][j] == 6: #esquina
                pygame.draw.arc(screen, color,
                                [(j * num2 + (num2 * 0.5)), (i * num1 + (0.5 * num1)), num2, num1], PI / 2, PI, 3)
            if level[i][j] == 7: #esquina
                pygame.draw.arc(screen, color, [(j * num2 + (num2 * 0.5)), (i * num1 - (0.4 * num1)), num2, num1], PI,
                                3 * PI / 2, 3)
            if level[i][j] == 8: #esquina
                pygame.draw.arc(screen, color,
                                [(j * num2 - (num2 * 0.4)) - 2, (i * num1 - (0.4 * num1)), num2, num1], 3 * PI / 2,
                                2 * PI, 3)
            if level[i][j] == 9: #puerta
                pygame.draw.line(screen, 'white', (j * num2, i * num1 + (0.5 * num1)),
                                 (j * num2 + num2, i * num1 + (0.5 * num1)), 3)


def draw_player():
    # 0-RIGHT, 1-LEFT, 2-UP, 3-DOWN
    if direction == 0:
        screen.blit(player_images[counter // 5], (player_x, player_y))
    elif direction == 1:
        screen.blit(pygame.transform.flip(player_images[counter // 5], True, False), (player_x, player_y))
    elif direction == 2:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 90), (player_x, player_y))
    elif direction == 3:
        screen.blit(pygame.transform.rotate(player_images[counter // 5], 270), (player_x, player_y))


def check_position(centerx, centery):
    turns = [False, False, False, False]
    num1 = (HEIGHT - 50) // 32
    num2 = (WIDTH // 30)
    num3 = 15

    # Verifica colisiones basadas en el centro x y centro y del jugador +/- un número de ajuste
    if centerx // 30 < 29:
        if direction == 0:  # Si el jugador se mueve a la derecha
            if level[centery // num1][(centerx - num3) // num2] < 3:
                turns[1] = True  # Puede girar a la izquierda
        if direction == 1:  # Si el jugador se mueve a la izquierda
            if level[centery // num1][(centerx + num3) // num2] < 3:
                turns[0] = True  # Puede girar a la derecha
        if direction == 2:  # Si el jugador se mueve hacia arriba
            if level[(centery + num3) // num1][centerx // num2] < 3:
                turns[3] = True  # Puede girar hacia abajo
        if direction == 3:  # Si el jugador se mueve hacia abajo
            if level[(centery - num3) // num1][centerx // num2] < 3:
                turns[2] = True  # Puede girar hacia arriba

        if direction == 2 or direction == 3:  # Si el jugador se mueve hacia arriba o hacia abajo
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num3) // num1][centerx // num2] < 3:
                    turns[3] = True  # Puede girar hacia abajo
                if level[(centery - num3) // num1][centerx // num2] < 3:
                    turns[2] = True  # Puede girar hacia arriba
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num2) // num2] < 3:
                    turns[1] = True  # Puede girar a la izquierda
                if level[centery // num1][(centerx + num2) // num2] < 3:
                    turns[0] = True  # Puede girar a la derecha

        if direction == 0 or direction == 1:  # Si el jugador se mueve a la derecha o a la izquierda
            if 12 <= centerx % num2 <= 18:
                if level[(centery + num1) // num1][centerx // num2] < 3:
                    turns[3] = True  # Puede girar hacia abajo
                if level[(centery - num1) // num1][centerx // num2] < 3:
                    turns[2] = True  # Puede girar hacia arriba
            if 12 <= centery % num1 <= 18:
                if level[centery // num1][(centerx - num3) // num2] < 3:
                    turns[1] = True  # Puede girar a la izquierda
                if level[centery // num1][(centerx + num3) // num2] < 3:
                    turns[0] = True  # Puede girar a la derecha
    else:
        turns[0] = True  # Puede girar a la derecha
        turns[1] = True  # Puede girar a la izquierda

    return turns

#Funcion que proporciona el movimiento de Pacman
def move_player(play_x, play_y):
    # r, l, u, d
    if direction == 0 and turns_allowed[0]:
        play_x += player_speed
    elif direction == 1 and turns_allowed[1]:
        play_x -= player_speed
    if direction == 2 and turns_allowed[2]:
        play_y -= player_speed
    elif direction == 3 and turns_allowed[3]:
        play_y += player_speed
    return play_x, play_y


def get_targets(blink_x, blink_y, ink_x, ink_y, pink_x, pink_y, clyd_x, clyd_y):
    # Determina la posición de huida en el eje x
    if player_x < 450:
        runaway_x = 900
    else:
        runaway_x = 0

    # Determina la posición de huida en el eje y
    if player_y < 450:
        runaway_y = 900
    else:
        runaway_y = 0

    # Posición de retorno por defecto
    return_target = (380, 400)

    # Si el poder de la superpastilla está activo
    if powerup:
        # Determina el objetivo de Blinky
        if not blinky.dead and not eaten_ghost[0]:
            blink_target = (runaway_x, runaway_y)
        elif not blinky.dead and eaten_ghost[0]:
            if 340 < blink_x < 560 and 340 < blink_y < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target

        # Determina el objetivo de Inky
        if not inky.dead and not eaten_ghost[1]:
            ink_target = (runaway_x, player_y)
        elif not inky.dead and eaten_ghost[1]:
            if 340 < ink_x < 560 and 340 < ink_y < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target

        # Determina el objetivo de Pinky
        if not pinky.dead:
            pink_target = (player_x, runaway_y)
        elif not pinky.dead and eaten_ghost[2]:
            if 340 < pink_x < 560 and 340 < pink_y < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target

        # Determina el objetivo de Clyde
        if not clyde.dead and not eaten_ghost[3]:
            clyd_target = (450, 450)
        elif not clyde.dead and eaten_ghost[3]:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                clyd_target = (400, 100)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target
    else:
        # Si el poder de la superpastilla no está activo
        # Determina el objetivo de Blinky
        if not blinky.dead:
            if 340 < blink_x < 560 and 340 < blink_y < 500:
                blink_target = (400, 100)
            else:
                blink_target = (player_x, player_y)
        else:
            blink_target = return_target

        # Determina el objetivo de Inky
        if not inky.dead:
            if 340 < ink_x < 560 and 340 < ink_y < 500:
                ink_target = (400, 100)
            else:
                ink_target = (player_x, player_y)
        else:
            ink_target = return_target

        # Determina el objetivo de Pinky
        if not pinky.dead:
            if 340 < pink_x < 560 and 340 < pink_y < 500:
                pink_target = (400, 100)
            else:
                pink_target = (player_x, player_y)
        else:
            pink_target = return_target

        # Determina el objetivo de Clyde
        if not clyde.dead:
            if 340 < clyd_x < 560 and 340 < clyd_y < 500:
                clyd_target = (400, 100)
            else:
                clyd_target = (player_x, player_y)
        else:
            clyd_target = return_target

    # Retorna los objetivos de todos los fantasmas
    return [blink_target, ink_target, pink_target, clyd_target]


run = True
while run:
    timer.tick(fps)
    if counter < 19:
        counter += 1
        if counter > 3:
            flicker = False
    else:
        counter = 0
        flicker = True
    if powerup and power_counter < 600: #Aumentar el contador del poder de la superpastilla
        power_counter += 1
    elif powerup and power_counter >= 600: #Desactivar el poder de la superpastilla y reiniciar el estado de los fantasmas
        power_counter = 0
        powerup = False
        eaten_ghost = [False, False, False, False]
    if startup_counter < 180 and not game_over and not game_won:
        moving = False
        startup_counter += 1
    else:
        moving = True

    screen.fill('black')
    draw_board() #Dibujar el tablero

    #Determinar el centro de Pacman para manejar colisiones y chequeos de posicion
    center_x = player_x + 23
    center_y = player_y + 24

    #Modificacion de la velocidad de los Fantasmas segun su estado
    if powerup:
        ghost_speeds = [1, 1, 1, 1]
    else:
        ghost_speeds = [2, 2, 2, 2]
    if eaten_ghost[0]:
        ghost_speeds[0] = 2
    if eaten_ghost[1]:
        ghost_speeds[1] = 2
    if eaten_ghost[2]:
        ghost_speeds[2] = 2
    if eaten_ghost[3]:
        ghost_speeds[3] = 2
    if blinky_dead:
        ghost_speeds[0] = 4
    if inky_dead:
        ghost_speeds[1] = 4
    if pinky_dead:
        ghost_speeds[2] = 4
    if clyde_dead:
        ghost_speeds[3] = 4

    game_won = True
    for i in range(len(level)):
        if 1 in level[i] or 2 in level[i]:
            game_won = False

    player_circle = pygame.draw.circle(screen, 'black', (center_x, center_y), 20, 2)
    draw_player()#Dibujar a Pacman
    #Inizializar a los fantasmas
    blinky = Ghost(blinky_x, blinky_y, targets[0], ghost_speeds[0], blinky_img, blinky_direction, blinky_dead,
                   blinky_box, 0)
    inky = Ghost(inky_x, inky_y, targets[1], ghost_speeds[1], inky_img, inky_direction, inky_dead,
                 inky_box, 1)
    pinky = Ghost(pinky_x, pinky_y, targets[2], ghost_speeds[2], pinky_img, pinky_direction, pinky_dead,
                  pinky_box, 2)
    clyde = Ghost(clyde_x, clyde_y, targets[3], ghost_speeds[3], clyde_img, clyde_direction, clyde_dead,
                  clyde_box, 3)
    draw_misc()
    #Asignar a los objetivos
    targets = get_targets(blinky_x, blinky_y, inky_x, inky_y, pinky_x, pinky_y, clyde_x, clyde_y)

    turns_allowed = check_position(center_x, center_y)
    if moving: #Movimiento de los fantasmas
        player_x, player_y = move_player(player_x, player_y)
        if not blinky_dead and not blinky.in_box:
            blinky_x, blinky_y, blinky_direction = blinky.move_blinky()
        else:
            blinky_x, blinky_y, blinky_direction = blinky.move_clyde()
        if not pinky_dead and not pinky.in_box:
            pinky_x, pinky_y, pinky_direction = pinky.move_pinky()
        else:
            pinky_x, pinky_y, pinky_direction = pinky.move_clyde()
        if not inky_dead and not inky.in_box:
            inky_x, inky_y, inky_direction = inky.move_inky()
        else:
            inky_x, inky_y, inky_direction = inky.move_clyde()
        clyde_x, clyde_y, clyde_direction = clyde.move_clyde()
    score, powerup, power_counter, eaten_ghost = check_collisions(score, powerup, power_counter, eaten_ghost)
    
    if not powerup: #Manejo de la logica de colision si Pacman choca con un Fantasma sin tener la superpastilla
        if (player_circle.colliderect(blinky.rect) and not blinky.dead) or \
                (player_circle.colliderect(inky.rect) and not inky.dead) or \
                (player_circle.colliderect(pinky.rect) and not pinky.dead) or \
                (player_circle.colliderect(clyde.rect) and not clyde.dead):
            if lives > 0:
                lives -= 1
                startup_counter = 0
                powerup = False
                power_counter = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_x = 56
                blinky_y = 58
                blinky_direction = 0
                inky_x = 440
                inky_y = 388
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438
                pinky_direction = 2
                clyde_x = 440
                clyde_y = 438
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
            else:
                game_over = True
                moving = False
                startup_counter = 0
    if powerup and player_circle.colliderect(blinky.rect) and eaten_ghost[0] and not blinky.dead: #Manejo de la logica de colision entre Blinky y Pacman luego de que este se lo coma
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(inky.rect) and eaten_ghost[1] and not inky.dead: #Manejo de la logica de colision entre Inky y Pacman luego de que este se lo coma
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(pinky.rect) and eaten_ghost[2] and not pinky.dead: #Maneja logica de colision entre Pinky y Pacman luego de que este se lo coma
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(clyde.rect) and eaten_ghost[3] and not clyde.dead: #Maneja de la logica de colision entre Clyde y Pacman luego de que este se lo coma
        if lives > 0:
            powerup = False
            power_counter = 0
            lives -= 1
            startup_counter = 0
            player_x = 450
            player_y = 663
            direction = 0
            direction_command = 0
            blinky_x = 56
            blinky_y = 58
            blinky_direction = 0
            inky_x = 440
            inky_y = 388
            inky_direction = 2
            pinky_x = 440
            pinky_y = 438
            pinky_direction = 2
            clyde_x = 440
            clyde_y = 438
            clyde_direction = 2
            eaten_ghost = [False, False, False, False]
            blinky_dead = False
            inky_dead = False
            clyde_dead = False
            pinky_dead = False
        else:
            game_over = True
            moving = False
            startup_counter = 0
    if powerup and player_circle.colliderect(blinky.rect) and not blinky.dead and not eaten_ghost[0]: #Si el jugador se come a Blinky
        blinky_dead = True
        eaten_ghost[0] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(inky.rect) and not inky.dead and not eaten_ghost[1]: #Si el jugador se come a Inky
        inky_dead = True
        eaten_ghost[1] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(pinky.rect) and not pinky.dead and not eaten_ghost[2]: #Si el jugador se come a Pinky
        pinky_dead = True
        eaten_ghost[2] = True
        score += (2 ** eaten_ghost.count(True)) * 100
    if powerup and player_circle.colliderect(clyde.rect) and not clyde.dead and not eaten_ghost[3]: #Si el jugador se come a Clyde
        clyde_dead = True
        eaten_ghost[3] = True
        score += (2 ** eaten_ghost.count(True)) * 100

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN: #eventos para la asignacion de la direccion
            if event.key == pygame.K_RIGHT:
                direction_command = 0
            if event.key == pygame.K_LEFT:
                direction_command = 1
            if event.key == pygame.K_UP:
                direction_command = 2
            if event.key == pygame.K_DOWN:
                direction_command = 3
            if event.key == pygame.K_SPACE and (game_over or game_won): #Si el jugador gana o pierde y presiona espacio, se reinicia el juego
                powerup = False
                power_counter = 0
                lives -= 1
                startup_counter = 0
                player_x = 450
                player_y = 663
                direction = 0
                direction_command = 0
                blinky_x = 56
                blinky_y = 58
                blinky_direction = 0
                inky_x = 440
                inky_y = 388
                inky_direction = 2
                pinky_x = 440
                pinky_y = 438
                pinky_direction = 2
                clyde_x = 440
                clyde_y = 438
                clyde_direction = 2
                eaten_ghost = [False, False, False, False]
                blinky_dead = False
                inky_dead = False
                clyde_dead = False
                pinky_dead = False
                score = 0
                lives = 3
                level = copy.deepcopy(boards)
                game_over = False
                game_won = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT and direction_command == 0:
                direction_command = direction
            if event.key == pygame.K_LEFT and direction_command == 1:
                direction_command = direction
            if event.key == pygame.K_UP and direction_command == 2:
                direction_command = direction
            if event.key == pygame.K_DOWN and direction_command == 3:
                direction_command = direction

    if direction_command == 0 and turns_allowed[0]:
        direction = 0
    if direction_command == 1 and turns_allowed[1]:
        direction = 1
    if direction_command == 2 and turns_allowed[2]:
        direction = 2
    if direction_command == 3 and turns_allowed[3]:
        direction = 3

    if player_x > 900:
        player_x = -47
    elif player_x < -50:
        player_x = 897

    if blinky.in_box and blinky_dead:
        blinky_dead = False
    if inky.in_box and inky_dead:
        inky_dead = False
    if pinky.in_box and pinky_dead:
        pinky_dead = False
    if clyde.in_box and clyde_dead:
        clyde_dead = False

    pygame.display.flip()
pygame.quit()