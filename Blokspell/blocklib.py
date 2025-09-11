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
        self.play_btn.y = self.play_btn.y+75
        self.last_play_btn_animation = time();

        # Mage animation
        self.mage_head = GameImage('src/cabeça_mago.png')
        self.mage_head.image = pygame.transform.scale(self.mage_head.image, (self.resolution['x']/100*60, self.resolution['y']/100*80))
        self.mage_head.x = self.resolution['x']/2 - int(self.mage_head.image.get_width()/2)
        self.mage_head.y = 0

        self.mage_hand1 = GameImage('src/mao1.png')
        self.mage_hand1.x = self.play_btn.x - int(self.play_btn.width)/2 + 75
        self.mage_hand1.y = self.play_btn.y - int(self.play_btn.height)/2 - 10

        self.mage_hand2 = GameImage('src/mao2.png')
        self.mage_hand2.x = self.mage_hand1.x - 55
        self.mage_hand2.y = self.mage_hand1.y - 10

    def falling_blocks_anim(self, interval_secs):
        block = choice(self.blocks)

        if time()-self.last_block_renderization >= interval_secs:
            self.last_block_renderization = time()
            if block.y >= self.resolution['y']:
                
                if block.x in self.block_ocupied_positions:
                    self.block_ocupied_positions.remove(block.x)
                
                first_space = range(0, int(self.mage_head.x)-50)
                second_space = range(int(self.mage_head.x+self.mage_head.width+50), int(self.resolution['x'])-int(block.width))
                pos_x = choice(list(first_space)+list(second_space))
                while pos_x in self.block_ocupied_positions:
                    pos_x = choice(list(first_space)+list(second_space))
                block.x = pos_x
                block.y = randint(5, 15)-block.height
                self.block_ocupied_positions.append(pos_x)
        block.move_y(4)

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

    def play_btn_anim(self, interval_secs):
        if time() - self.last_play_btn_animation >= interval_secs:
            self.play_btn.x = self.play_btn.x * -1
            self.last_play_btn_animation = time()
            

    def close(self):
        self.main_window.close()
