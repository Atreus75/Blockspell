from PPlay.gameimage import *
from PPlay.mouse import *
from PPlay.sprite import *
from PPlay.window import *
from PPlay.animation import *
from random import randint, choice
from time import time
from tetris import Tetris



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
    def __init__(self, mouse=Mouse(), window=Window(0, 0)):
        self.main_window = window

        self.player_mouse = mouse
        self.background = GameImage('src/fundo_menu.jpg')
        self.background.image = pygame.transform.scale(self.background.image, (self.main_window.width, self.main_window.height))
        self.background.width = self.main_window.width
        self.background.height = self.main_window.height
        self.last_window_animation = 0

    def preset_blocks(self):
        # Pre-configures the little blocks for their background animation
        self.block_vely = 100
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
            block.image = pygame.transform.scale(block.image, (self.main_window.width/100*6, self.main_window.height/100*6))
            block.y = self.main_window.height
        self.last_block_renderization = time()

    def preset_play_btn(self):
        # Play button configuration
        self.play_btn = GameImage('src/play_button1.png')
        self.play_btn = Utils.centralize_over_object(self.play_btn, self.main_window)
        self.play_btn.y = self.play_btn.y + 80
        self.last_play_btn_animation = time()
        self.play_btn.height -= self.play_btn.height/2.7

    def preset_mage(self):
        # Menu Mage
        self.mage_head = GameImage('src/cabeça_mago.png')
        self.mage_head.image = pygame.transform.scale(self.mage_head.image, (self.main_window.width/100*60, self.main_window.height/100*80))
        self.mage_head.x = self.main_window.width/2 - int(self.mage_head.image.get_width()/2)
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

    def animate_falling_blocks(self, interval_secs, play_pressed=False):
        block = choice(self.blocks)
        if time()-self.last_block_renderization >= interval_secs and play_pressed == False:
            self.last_block_renderization = time()

            if block.y >= self.main_window.height:    
                if block.x in self.block_ocupied_positions:
                    self.block_ocupied_positions.remove(block.x)
                
                first_space = range(0, int(self.mage_head.x)-50)
                second_space = range(int(self.mage_head.x+self.mage_head.width+50), int(self.main_window.width)-int(block.width))
                pos_x = choice(list(first_space)+list(second_space))
                while pos_x in self.block_ocupied_positions:
                    pos_x = choice(list(first_space)+list(second_space))
                block.x = pos_x
                block.y = randint(-30, -5) - block.height
                self.block_ocupied_positions.append(pos_x)
        for block in self.blocks:
            block.y += self.block_vely * self.main_window.delta_time()

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

    def menu_loop(self):
        # Menu Definitions
        play_pressed = False
        wait_blocks = 0
        mage_anim_interval = 0.05
        blocks_anim_interval = 0.05

        self.preset_blocks()
        self.preset_play_btn()
        self.preset_mage()
        
        # Loop
        while True:
            # Verifications
            if self.main_window.get_keyboard().key_pressed('ESC'):
                self.main_window.close()
                exit() # End window and the entire program
            
            now = time()
            if play_pressed and now - wait_blocks >= 5:
                break # End menu loop and goes to game loop

            if self.player_mouse.is_over_object(self.play_btn):
                mage_anim_interval = 0.005
                
                if self.player_mouse.is_button_pressed(1):
                    self.mage_hand1.y = self.origin_mage_hand1_y
                    self.mage_hand2.y = self.origin_mage_hand2_y
                    #play_sound.play()
                    wait_blocks = time()
                    play_pressed = True
            else:
                if not self.player_mouse.is_button_pressed(1):
                    mage_anim_interval = 0.05

            # Animations
            self.animate_falling_blocks(blocks_anim_interval)
            if not play_pressed:
                self.animate_mage_hands(mage_anim_interval)

            # Draws in visual layer order (back to front)
            self.background.draw()
            
            # Draws all blocks
            for block in self.blocks:
                block.draw()

            Utils.draw_all([self.play_btn, self.mage_head, self.mage_hand1, self.mage_hand2])
            self.main_window.update()


class Game:
    def __init__(self, main_window=Window(0, 0)):
        self.main_window = main_window

        self.ceu = Sprite('src/ceu.png')
        self.chao = Sprite('src/chao2.png')
        self.chao.y = self.main_window.height - (self.chao.height)
        self.castelo = Sprite('src/castelo.png')
        self.castelo.x = 0
        self.castelo.y = self.main_window.height - (self.castelo.height + (self.chao.height))
        self.mago = Sprite('src/mago_p.png')
        self.mago.x = (self.castelo.x + self.castelo.width - 20)
        self.mago.y = self.main_window.height - (self.mago.height + (self.chao.height))

        self.tetris = Tetris(self.main_window, 10, 15, 28, (self.main_window.width//2 - 190, self.main_window.height//2 - 300))

        # Preset das clouds
        self.clouds = [
            'src/nuvem_0.png',
            'src/nuvem_1.png',
            'src/nuvem_2.png',
            'src/nuvem_3.png',
            'src/nuvem_casa.png'
        ]
        self.current_clouds = []
        self.cloud_vel = -100
        self.last_cloud_animation = time()

    def animate_clouds(self):
        if len(self.current_clouds) >= 1:
            if randint(0, 1500) == randint(0, 1500):
                self.current_clouds.append(Sprite(choice(self.clouds[0:4])))
                self.current_clouds[-1].x = randint(self.main_window.width + int(self.current_clouds[-1].width), self.main_window.width + int(self.current_clouds[-1].width) + 100)
                self.current_clouds[-1].y = randint(0, int(self.main_window.height / 2) - int(self.current_clouds[-1].height))

            for cloud in self.current_clouds:
                if cloud.x < (0-cloud.width):
                    self.current_clouds.remove(cloud)
                else:
                    cloud.x += self.cloud_vel * self.main_window.delta_time()
        else:
            self.current_clouds.append(Sprite(choice(self.clouds[0:4])))
            self.current_clouds[-1].x = self.main_window.width + self.current_clouds[-1].width
            self.current_clouds[-1].y = randint(0, int(self.main_window.height/2))
    
    def game_loop(self):
        while True:
            # Checks
            if self.main_window.get_keyboard().key_pressed('ESC'):
                break
            
            if self.tetris.game_over:
                self.tetris.reset()
            
            self.main_window.set_background_color('black')
            self.animate_clouds()

            # Draws
            self.ceu.draw()
            if len(self.current_clouds) >= 1:
                for cloud in self.current_clouds:
                    cloud.draw()
            self.chao.draw()
            self.castelo.draw()
            self.mago.draw()
            self.tetris.draw()
            self.main_window.update()
            self.tetris.update()


