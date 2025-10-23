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

class Enemie(Animation):
    def __init__(self, image_file, frames=1, move_timeout=0, damage=0, life=0, vel_x=0):
        super().__init__(image_file, frames)
        self.set_total_duration(1000)
        self.move_timeout = move_timeout
        self.damage = damage
        self.life = life
        self.vel_x = vel_x
        self.last_move = time()
        self.alive = True

    def move(self):
        self.x -= self.vel_x


class Cachorro(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/cachorro_spritesheet.png'
        super().__init__(image_file, frames=12, move_timeout=3, damage=20, life=100, vel_x=25)

class Gorila(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/gorila_spritesheet.png'
        super().__init__(image_file, frames=6, move_timeout=5, damage=50, life=200, vel_x=10)

class Rato(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/rato_spritesheet.png'
        super().__init__(image_file, frames=3, move_timeout=1, damage=5, life=50, vel_x=40)

class Mago(Sprite):
    def __init__(self, image_file, frames=1):
        super().__init__(image_file, frames)
        self.life = 100
        self.mana = 100
    
    def regenerate_life(self, points=0):
        self.life += 10 * points
        
    def regenerate_mana(self, points=0):
        self.mana += 10 * points
    
class Spell(Sprite):
    def __init__(self):
        self.current_frame = 0
        self.current_collision_frame = 0
        self.image_path = 'src/bola_fodona/bola_0.png'
        super().__init__(self.image_path)
        self.damage = 25
        self.last_animation = time()
        self.last_collision_animation = 0
        self.animation_timeout = 0.2
        #self.set_total_duration(1000)


class Regeneration(Sprite):
    def __init__(self):
        super().__init__('/src/açoes/rec_vida.png')
        self.life_points = 5
        self.animation_duration = 1

class Menu:
    def __init__(self, mouse=Mouse(), window=Window(0, 0)):
        self.main_window = window

        self.player_mouse = mouse
        self.background = GameImage('src/menu/fundo_menu.jpg')
        self.background.image = pygame.transform.scale(self.background.image, (self.main_window.width, self.main_window.height))
        self.background.width = self.main_window.width
        self.background.height = self.main_window.height
        self.last_window_animation = 0

    def preset_blocks(self):
        # Pre-configures the little blocks for their background animation
        self.block_vely = 100
        self.blocks = [
            Sprite('src/peças/I_azul.png'),
            Sprite('src/peças/I_verde.png'),
            Sprite('src/peças/I_vermelha.png'),
            Sprite('src/peças/L_azul.png'),
            Sprite('src/peças/L_verde.png'),
            Sprite('src/peças/L_vermelho.png'),
            Sprite('src/peças/O_azul.png'),
            Sprite('src/peças/O_verde.png'),
            Sprite('src/peças/O_vermelho.png'),
            Sprite('src/peças/peça_dourada.png'),
            Sprite('src/peças/S_azul.png'),
            Sprite('src/peças/S_verde.png'),
            Sprite('src/peças/S_vermelho.png'),
            Sprite('src/peças/T_azul.png'),
            Sprite('src/peças/T_verde.png'),
            Sprite('src/peças/T_vermelho.png')
                ]

        self.block_ocupied_positions = []
        for block in self.blocks:
            block.image = pygame.transform.scale(block.image, (self.main_window.width/100*6, self.main_window.height/100*6))
            block.y = self.main_window.height
        self.last_block_renderization = time()

    def preset_play_btn(self):
        # Play button configuration
        self.play_btn = GameImage('src/menu/play_button1.png')
        self.play_btn = Utils.centralize_over_object(self.play_btn, self.main_window)
        self.play_btn.y = self.play_btn.y + 80
        self.last_play_btn_animation = time()
        self.play_btn.height -= self.play_btn.height/2.7

    def preset_mage(self):
        # Menu Mage
        self.mage_head = GameImage('src/menu/cabeça_mago.png')
        self.mage_head.image = pygame.transform.scale(self.mage_head.image, (self.main_window.width/100*60, self.main_window.height/100*80))
        self.mage_head.x = self.main_window.width/2 - int(self.mage_head.image.get_width()/2)
        self.mage_head.y = 0

        self.mage_hand1 = GameImage('src/menu/mao1.png')
        self.mage_hand1.x = self.play_btn.x - int(self.play_btn.width)/2 + 75
        self.mage_hand1.y = self.play_btn.y - (int(self.play_btn.height) - 30)

        self.mage_hand2 = GameImage('src/menu/mao2.png')
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
        self.esc_pressed = 0
        self.enemie_generation_rate = 20

        self.ceu = Sprite('src/cenario/ceu.png')
        self.chao = Sprite('src/cenario/chao2.png')
        self.chao.y = self.main_window.height - (self.chao.height)
        self.castelo = Sprite('src/cenario/castelo.png')
        self.castelo.x = 0
        self.castelo.y = self.main_window.height - (self.castelo.height + (self.chao.height))
        self.mago = Mago('src/magos/mago_p.png')
        self.mago.x = (self.castelo.x + self.castelo.width - 20)
        self.mago.y = self.main_window.height - (self.mago.height + (self.chao.height))

        self.tetris = Tetris(self.main_window, 10, 15, 28, (self.main_window.width//2 - 190, self.main_window.height//2 - 300))

        # Preset das clouds
        self.clouds = [
            'src/nuvens/nuvem_0.png',
            'src/nuvens/nuvem_1.png',
            'src/nuvens/nuvem_2.png',
            'src/nuvens/nuvem_3.png',
            'src/nuvens/nuvem_casa.png'
        ]
        
        self.current_clouds = []
        self.cloud_vel = -100
        self.last_cloud_animation = time()
        
        self.current_enemies = []
        self.last_enemie_generation = time()

        self.current_spells = []
        self.spell_velx = 100

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
    # tetris_pplay.py

    def generate_enemies(self):
        if time() - self.last_enemie_generation >= self.enemie_generation_rate or len(self.current_enemies) == 0:
            self.last_enemie_generation = time()
            
            choose = randint(1, 20)
            if 0 <= choose <= 9:
                self.current_enemies.append(Cachorro())
            elif 10 <= choose <= 13:
                self.current_enemies.append(Gorila())
            elif 14 <= choose <= 19:
                self.current_enemies.append(Rato())
            else:
                self.current_enemies.append(Cachorro())
            
            self.current_enemies[-1].x = self.main_window.width
            self.current_enemies[-1].y = self.chao.y - self.current_enemies[-1].height
    
    def launch_spell(self, count=1):
        spell = Spell()
        spell.damage *= count
        self.current_spells.append(spell)
    
    def animate_spell(self, spell=Spell()):
        possible_spell_sprites = [
            'src/bola_fodona/bola_0.png',
            'src/bola_fodona/Bola_1.png',
            'src/bola_fodona/Bola_2.png',
            'src/bola_fodona/Bola_3.png',
            'src/bola_fodona/Bola_4.png'
        ]

        spell.x += self.spell_velx * self.main_window.delta_time()
        
        if time() - spell.last_animation >= spell.animation_timeout:
            spell.last_animation = time()
            if spell.current_frame == 4:
                spell.current_frame = 0
            else:
                spell.current_frame += 1
            
            spell.image = pygame.image.load(possible_spell_sprites[spell.current_frame])
            spell.width = spell.image.get_width()
            spell.height = spell.image.get_height()
            spell.rect = spell.image.get_rect()
            
        spell.draw()
    
    def animate_spell_collision(self, spell=Spell()):
        possible_collision_sprites = [
            'src/bola_fodona/Bola_5.png',
            'src/bola_fodona/Bola_6.png',
            'src/bola_fodona/Bola_7.png'
        ]
        
        if time()-spell.last_collision_animation >= spell.animation_timeout+0.3:
            spell.last_animation = time()
            spell.image = pygame.image.load(possible_collision_sprites[spell.current_collision_frame])
            spell.width = spell.image.get_width()
            spell.height = spell.image.get_height()
            spell.rect = spell.image.get_rect()
            spell.current_collision_frame += 1
    
    def game_loop(self):
        while True:
            self.main_window.set_background_color('black')
            
            # Checks
            if self.main_window.get_keyboard().key_pressed('ESC'):
                self.esc_pressed = time()
                break
            
            # Functions
            if self.tetris.game_over:
                self.tetris.reset()
            self.animate_clouds()
            self.generate_enemies()
            # Mage actions
            if len(self.tetris.last_cleared_color_counts) >= 1:
                counts = self.tetris.last_cleared_color_counts[0]
                
                for i in range(1, 9):
                    if i == 1 or i == 5:
                        self.launch_spell(counts[i])
                        self.current_spells[-1].y = self.mago.y + self.current_spells[-1].height
                        self.current_spells[-1].x = self.mago.x + self.mago.width
                    elif i == 2 or i == 6:
                        self.mago.regenerate_life(counts[i])
                    elif i == 3 or i == 7:
                        self.mago.regenerate_mana(counts[i])
                self.tetris.last_cleared_color_counts.pop()
            
            # Draws
            self.ceu.draw()
            if len(self.current_clouds) >= 1:
                for cloud in self.current_clouds:
                    cloud.draw()
            self.chao.draw()
            self.castelo.draw()
            self.mago.draw()
            for enemie in self.current_enemies:
                if enemie.life <= 0:
                    enemie.alive = False
                    self.current_enemies.remove(enemie)
                
                if time() - enemie.last_move >= enemie.move_timeout and enemie.alive:
                    enemie.last_move = time()
                    if enemie.x >= self.mago.x + self.mago.width:
                        enemie.move()


                enemie.update()
                enemie.draw()

            
            if len(self.current_spells) >= 1:
                for spell in self.current_spells:
                    if spell.x >= self.main_window.width:
                        self.current_spells.remove(spell)
                    else:
                        self.animate_spell(spell)
                        for spell in self.current_spells:
                            for enemie in self.current_enemies:
                                if spell.collided_perfect(enemie) and spell.current_collision_frame <= 2:
                                    self.animate_spell_collision(spell)
                                elif spell.current_collision_frame > 2 and spell in self.current_spells:
                                    self.current_spells.remove(spell)
                    
            self.tetris.draw()
            self.main_window.update()
            self.tetris.update()
