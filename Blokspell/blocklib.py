from PPlay.gameimage import *
from PPlay.mouse import *
from PPlay.sprite import *
from PPlay.window import *
from PPlay.animation import *
from random import randint


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
            block.image = pygame.transform.scale(block.image, (self.resolution['x']/100*5, self.resolution['y']/100*5))
            block.y = self.resolution['y']+1

        # Play button configuration
        self.play_btn = GameImage('src/play_button1.png')
        self.play_btn = Utils.centralize_over_object(self.play_btn, self.main_window)


    def falling_blocks_anim(self):
        block = self.blocks[randint(0, len(self.blocks)-1)]
        if block.y >= self.resolution['y']:
            if block.x in self.block_ocupied_positions:
                self.block_ocupied_positions.remove(block.x)
            pos_x = randint(0, int(self.resolution['x']-block.width))
            while pos_x in self.block_ocupied_positions:
                pos_x = randint(0, self.main_window.width)
            block.x = pos_x
            block.y = randint(0, 5)-block.height
            self.block_ocupied_positions.append(pos_x)
        block.move_y(5)
        block.draw()

    def close(self):
        self.main_window.close()
