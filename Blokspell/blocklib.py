from PPlay.gameimage import *
from PPlay.mouse import *
from PPlay.sprite import *
from PPlay.window import *
from PPlay.animation import *
from random import randint, choice
from time import time


class Utils:
    def __init__(self):
        pass

    # Centralizes an object over another object
    def centralize_over_object(top_obj, back_obj):
        top_obj.x = back_obj.width/2 - top_obj.width/2
        top_obj.y = back_obj.height/2 - top_obj.height/2
        return top_obj


class Menu:
    def __init__(self, width=0, height=0):
        self.resolution = {'x':width, 'y':height}
        self.main_window = Window(self.resolution['x'], self.resolution['y'])
        self.main_window.set_fullscreen()

        self.background = GameImage('src/fundo_menu.jpg')
        self.background.image = pygame.transform.scale(self.background.image, (self.resolution['x'], self.resolution['y']))
        self.background.width = self.main_window.width
        self.background.height = self.main_window.height

        # Pre-configures the little blocks for their background animation
        self.blocks = [
            Sprite('src/I_azul.png'),
            Sprite('src/I_verde.png'),
            Sprite('src/I_vermelha.png'),
            Sprite('src/L_azul.png'),
            Sprite('src/L_verde.png'),
            Sprite('src/L_vermelho.png'),
            Sprite('src/O_azul.png'),
            Sprite('src/O_verde.png'),
            Sprite('src/O_vermelho.png'),
            Sprite('src/peça_dourada.png'),
            Sprite('src/S_azul.png'),
            Sprite('src/S_verde.png'),
            Sprite('src/S_vermelho.png'),
            Sprite('src/T_azul.png'),
            Sprite('src/T_verde.png'),
            Sprite('src/T_vermelho.png')
                ]

        self.block_ocupied_positions = []
        for block in self.blocks:
            block.image = pygame.transform.scale(block.image, (self.resolution['x']/100*6, self.resolution['y']/100*6))
            block.y = self.resolution['y']
        self.last_block_renderization = time()


        # Play button configuration
        self.play_btn = GameImage('src/play_button1.png')
        self.play_btn = Utils.centralize_over_object(self.play_btn, self.main_window)
 
        # Pre-Configures the enemies animation
        self.enemies = [Sprite('src/gollira_transparente.gif'), Sprite('src/cachorro_transparente.gif'), Sprite('src/rato.gif')]
        for enemie in self.enemies:
            enemie.image = pygame.transform.scale(enemie.image, (self.resolution['x']/100*10, self.resolution['y']/100*10))
            enemie.y = self.resolution['y']-130
            enemie.x = randint(-5, -1) - int(enemie.width)
        self.enemie_ocupied_positions = []
        self.last_enemie_renderization = time()

    def falling_blocks_anim(self, interval_secs):
        block = choice(self.blocks)

        if time()-self.last_block_renderization >= interval_secs:
            self.last_block_renderization = time()
            if block.y >= self.resolution['y']:
                
                if block.x in self.block_ocupied_positions:
                    self.block_ocupied_positions.remove(block.x)
                
                #first_space = range(0, int(self.play_btn.x)-150)
                #second_space = range(int(self.play_btn.x+self.play_btn.width+150), int(self.resolution['x'])-int(block.width))
                #pos_x = choice(list(first_space)+list(second_space))
                pos_x = randint(0, self.resolution['x']-int(block.width))
                while pos_x in self.block_ocupied_positions:
                    #pos_x = choice(list(first_space)+list(second_space))
                    pos_x = randint(0, self.resolution['x']-int(block.width))
                block.x = pos_x
                block.y = randint(5, 10)-block.height
                self.block_ocupied_positions.append(pos_x)
        block.move_y(5)

    def enemies_anim(self, interval_secs):
        enemie = choice(self.enemies)
        if time()-self.last_enemie_renderization >= interval_secs:
            self.last_enemie_renderization = time()
            if enemie.x <= -1:
                if enemie.x in self.enemie_ocupied_positions:
                    self.enemie_ocupied_positions.remove(enemie.x)

                pos_x = choice(list(range(self.resolution['x']+1, self.resolution['x']+10)))
                while pos_x in self.enemie_ocupied_positions:
                    pos_x = choice(list(range(self.resolution['x']+1, self.resolution['x']+10)))
                enemie.x = pos_x
                self.enemie_ocupied_positions.append(pos_x)
        enemie.move_x(-2)


    def close(self):
        self.main_window.close()
