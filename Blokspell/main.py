from os import access

from PPlay.window import *
from PPlay.sprite import *
from PPlay.gameimage import *
from PPlay.animation import *

# Variáveis GLobais
resolution = {'x' : 1280, 'y' : 720}

class Menu:
    def __init__(self, width=0, height=0):
        self.resolution = {'x':width, 'y':height}
        self.main_window = Window(self.resolution['x'], self.resolution['y'])
        
        self.background = GameImage('src/fundo_menu.jpg')
        self.background.image = pygame.transform.scale(self.background.image, (self.resolution['x'], self.resolution['y']))
        self.background.width = self.main_window.width
        self.background.height = self.main_window.height


    def close(self):
        self.main_window.close()


menu = Menu(1200, 720)
menu.main_window.set_title('Blockspell')

# Menu Loop
while True:
    menu.background.draw()
    menu.main_window.update()
