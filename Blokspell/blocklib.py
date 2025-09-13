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

    def draw_all(objects=[]):
        for obj in objects:
            obj.draw()

class Menu:
    def __init__(self, width=0, height=0):
        self.resolution = {'x':width, 'y':height}
        self.main_window = Window(self.resolution['x'], self.resolution['y'])
        self.main_window.set_fullscreen()

        self.background = GameImage('src/fundo_menu.jpg')
        self.background.image = pygame.transform.scale(self.background.image, (self.resolution['x'], self.resolution['y']))
        self.background.width = self.main_window.width
        self.background.height = self.main_window.height

    def preset_blocks(self):
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

    def preset_play_btn(self):
        # Play button configuration
        self.play_btn = GameImage('src/play_button1.png')
        self.play_btn = Utils.centralize_over_object(self.play_btn, self.main_window)
        self.play_btn.y = self.play_btn.y + 80
        self.last_play_btn_animation = time();
        self.play_btn.height -= self.play_btn.height/2.7

    def preset_mage(self):
        # Menu Mage
        self.mage_head = GameImage('src/cabeça_mago.png')
        self.mage_head.image = pygame.transform.scale(self.mage_head.image, (self.resolution['x']/100*60, self.resolution['y']/100*80))
        self.mage_head.x = self.resolution['x']/2 - int(self.mage_head.image.get_width()/2)
        self.mage_head.y = 0

        self.mage_hand1 = GameImage('src/mao1.png')
        self.mage_hand1.x = self.play_btn.x - int(self.play_btn.width)/2 + 75
        self.mage_hand1.y = self.play_btn.y - (int(self.play_btn.height) - 30)

        self.mage_hand2 = GameImage('src/mao2.png')
        self.mage_hand2.x = self.mage_hand1.x - 55
        self.mage_hand2.y = self.mage_hand1.y - 15
        
        self.origin_mage_hand1_y = self.mage_hand1.y
        self.origin_mage_hand2_y = self.mage_hand2.y
        self.last_mage_animation = time()
        self.hand_vely = 1

    def animate_falling_blocks(self, interval_secs):
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
                block.y = randint(-10, -5) - block.height
                self.block_ocupied_positions.append(pos_x)
        for block in self.blocks:
            block.move_y(2)

    def animate_mage_hands(self, interval_secs):
        reached_top = self.mage_hand1.y >= self.origin_mage_hand1_y
        reached_bottom = self.mage_hand1.y+10 <= self.origin_mage_hand1_y - 20

        if time()-self.last_mage_animation >= interval_secs:
            self.last_mage_animation = time()
            if reached_top or reached_bottom:
                self.hand_vely *= -1
            self.mage_hand1.y += self.hand_vely
            self.mage_hand2.y += self.hand_vely * -1

    def animate_play_btn(self, interval_secs):
        if time() - self.last_play_btn_animation >= interval_secs and interval_secs != -1:
            self.play_btn.x = self.play_btn.x * -1
            self.last_play_btn_animation = time()
        elif interval_secs == -1:
            self.play_btn.x = self.play_btn.x if self.play_btn.x > 0 else self.play_btn.x * -1

    def close(self):
        self.main_window.close()

