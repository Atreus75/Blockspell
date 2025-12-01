from PPlay.gameimage import *
from PPlay.mouse import *
from PPlay.sprite import *
from PPlay.window import *
from PPlay.animation import *
from random import randint, choice
from time import time
from tetris import Tetris
from math import sin

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
    def __init__(self, image_file, frames=1, move_timeout=0, damage=0, life=0, vel_x=0, attack_cooldown=0):
        super().__init__(image_file, frames)
        self.set_total_duration(1000)
        self.move_timeout = move_timeout
        self.damage = damage
        self.life = life
        self.vel_x = vel_x
        self.last_move = time()
        self.last_attack = 0
        self.attack_cooldown = attack_cooldown
        self.alive = True
        self.state = "walking"  # walking / attacking / recovering
        self.attack_offset = 0  # deslocamento momentâneo no ataque
        self.attack_recoil = 6  # quão forte a sacudida é
        self.recover_time = 0.15  # tempo pra voltar da sacudida
        self.image_file = image_file

    def move(self):
        self.x -= self.vel_x

class Cachorro(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/cachorro_spritesheet.png'
        super().__init__(image_file, frames=12, move_timeout=3, damage=20, life=100, vel_x=25, attack_cooldown=5)

class Gorila(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/gorila_spritesheet.png'
        super().__init__(image_file, frames=6, move_timeout=5, damage=50, life=200, vel_x=10, attack_cooldown=8)

class Rato(Enemie):
    def __init__(self):
        image_file = 'src/inimigos/rato_spritesheet.png'
        super().__init__(image_file, frames=3, move_timeout=1, damage=5, life=50, vel_x=40, attack_cooldown=2)

class Mago(Sprite):
    def __init__(self, image_file, frames=1):
        super().__init__(image_file, frames)
        self.life = 100
        self.mana = 100
        self.anim_state = False
        self.last_animation = 0.0
    
    def regenerate_life(self, points=0):
        total_regen = 10 * points
        self.life = self.life + total_regen if self.life + total_regen <= 100 else 100
        
    def regenerate_mana(self, points=0):
        self.mana += 10 * points
    
class Spell(Sprite):
    def __init__(self, x=0, y=0):
        self.current_frame = 0
        self.current_collision_frame = 0
        self.image_path = 'src/bola_fodona/Bola_0.png'
        super().__init__(self.image_path)
        self.damage = 25
        self.last_animation = time()
        self.last_collision_animation = 0
        self.animation_timeout = 0.2
        self.state = "moving"  # "moving", "colliding", "finished"
        self.collided_with = None

        # Posição inicial (evita nascer fora da tela)
        self.x = x
        self.y = y

class Rain(Sprite):
    def __init__(self, x=0, y=0, frames=None):
        super().__init__('src/açoes/raio/frame-1.gif')
        self.x = x
        self.y = y
        self.frames = frames or []
        self.current_frame = 0
        self.damage = 30
        self.last_animation = time()
        self.animation_timeout = 0.05
        self.finished = False
        self.has_hit = False  # garante que só dá dano uma vez
        self.enemy_hitbox_radius = 60  # tolerância do impacto

    def update(self, window, enemies):
        """Atualiza animação e aplica dano no frame do impacto."""
        now = time()
        if now - self.last_animation >= self.animation_timeout:
            self.last_animation = now
            self.current_frame += 1

            # se acabou os frames, remove
            if self.current_frame >= len(self.frames):
                self.finished = True
                return

            # atualiza imagem
            self.image = self.frames[self.current_frame]

            # aplica dano no frame do impacto (ajuste fino)
            if self.current_frame == 4 and not self.has_hit:
                for enemy in enemies:
                    if enemy and abs(enemy.x - self.x) < self.enemy_hitbox_radius:
                        enemy.life -= self.damage
                        if enemy.life <= 0:
                            enemy.alive = False
                        # 💥 feedback visual: faz o inimigo piscar
                        flash_surface = pygame.Surface((enemy.width, enemy.height), pygame.SRCALPHA)
                        flash_surface.fill((255, 255, 255, 150))
                        window.screen.blit(flash_surface, (enemy.x, enemy.y))
                        self.has_hit = True

        # desenha o raio em tela
        self.draw()


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
        self.enemie_limit = 4
        self.score = 0

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
        self.selection_box = Sprite('src/cenario/select_back.png')
        self.selection_box.x = self.tetris.x - self.selection_box.width - 20
        self.selection_box.y = self.tetris.y + 70

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

        self.block_sprites = [
            'src/peças/I_azul.png',
            'src/peças/I_verde.png',
            'src/peças/I_vermelha.png',
            'src/peças/L_azul.png',
            'src/peças/L_verde.png',
            'src/peças/L_vermelho.png',
            'src/peças/O_azul.png',
            'src/peças/O_verde.png',
            'src/peças/O_vermelho.png',
            'src/peças/S_azul.png',
            'src/peças/S_verde.png',
            'src/peças/S_vermelho.png',
            'src/peças/T_azul.png',
            'src/peças/T_verde.png',
            'src/peças/T_vermelho.png'
        ]
        self.block_colors = [
            'vermelho',
            'azul',
            'verde'
        ]
        self.block_shapes = [
            'I',
            'O',
            'L',
            'S'
        ]
        
        self.current_block_options = [None, None, None]

        self.enemy_slots = [None, None, None]  # 3 posições fixas
        self.slot_positions = [
            self.mago.x + 300,  # Posição mais próxima
            self.mago.x + 450,  # Posição intermediária
            self.mago.x + 600  # Posição mais distante
        ]
        self.slot_damage_multiplier = [1.0, 0.7, 0.4]  # Dano reduzido conforme distância
        self.last_enemy_gen = time()
        self.current_spells = []
        self.spell_velx = 200
        self._load_spell_assets()
        
        self.rain_frames = [
            pygame.image.load(f"src/açoes/raio/frame-{i}.gif").convert_alpha()
            for i in range(1, 10)
        ]
        self.current_rains = []
        self.last_rain_gen = 0

    def placar(self):
        self.main_window.draw_text(f"Score: {self.score}", 10, 40, size=25, color=(255, 255, 255))

    def _load_spell_assets(self):
        """Carrega todas as imagens do feitiço na memória para evitar lag."""
        self.spell_frames = [
            pygame.image.load(f"src/bola_fodona/Bola_{i}.png").convert_alpha() 
            for i in range(8)
        ]

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
        """Garante até 3 inimigos em fila da esquerda pra direita."""
        # Remove mortos
        for i in range(3):
            e = self.enemy_slots[i]
            if e and not e.alive:
                self.enemy_slots[i] = None

        # Avança os de trás para frente se houver espaço
        for i in range(2):
            if self.enemy_slots[i] is None and self.enemy_slots[i + 1]:
                self.enemy_slots[i] = self.enemy_slots[i + 1]
                self.enemy_slots[i + 1] = None
                self.enemy_slots[i].target_slot = i

        # Gera novos inimigos sempre na posição mais à direita disponível
        for i in range(2, -1, -1):
            if self.enemy_slots[i] is None:
                choose = randint(0, 19)
                if 0 <= choose <= 9:
                    e = Cachorro()
                elif 10 <= choose <= 13:
                    e = Gorila()
                else:
                    e = Rato()

                # nasce fora da tela, anda até o slot
                e.x = self.main_window.width + randint(50, 100)
                e.y = self.chao.y - e.height
                e.target_slot = i
                e.state = "walking"
                e.alive = True
                e.last_attack = time()
                self.enemy_slots[i] = e

    def launch_rain(self):
        """Lança um raio sobre cada inimigo visível, respeitando cooldown individual."""
        now = time()
        any_spawned = False

        for enemy in self.enemy_slots:
            if not enemy:
                continue

            # cooldown individual de cada inimigo
            if not hasattr(enemy, "last_rain_time"):
                enemy.last_rain_time = 0

            if now - enemy.last_rain_time >= 1.5:
                enemy.last_rain_time = now

                x = enemy.x + enemy.width // 2
                y = 200  # um pouco acima do inimigo

                self.current_rains.append(Rain(x, y, self.rain_frames))
                any_spawned = True

        print(f"[DEBUG] Raios ativos: {len(self.current_rains)} (spawned={any_spawned})")

    def update_rain(self):
        """Atualiza todos os raios ativos."""
        for rain in self.current_rains[:]:
            rain.update(self.main_window, self.enemy_slots)
            if rain.finished:
                self.current_rains.remove(rain)
                
    def launch_spell(self, power=1):
        """Cria e adiciona um novo feitiço ofensivo escalonado visualmente pelo dano."""
        x = self.mago.x + self.mago.width - 20
        y = self.mago.y + self.mago.height // 3

        spell = Spell(x, y)
        spell.state = "moving"
        spell.current_frame = 0
        spell.current_collision_frame = 0
        spell.last_animation = time()
        spell.last_collision_animation = 0
        spell.animation_timeout = 0.08
        spell.damage = 10 * power  # dano proporcional à força

        # --- Escala visual conforme dano ---
        scale = 1.0 + (spell.damage / 100)
        if scale > 1.8:
            scale = 2.5
        elif scale < 1.0:
            scale = 1.0

        w = int(spell.width * scale)
        h = int(spell.height * scale)
        spell.image = pygame.transform.scale(spell.image, (w, h))
        spell.width = w
        spell.height = h
        spell.rect = spell.image.get_rect(topleft=(spell.x, spell.y))

        print(f'Spell lançado com dano {spell.damage} (escala {scale:.2f}x)')
        self.current_spells.append(spell)


    
    def update_spells(self):
        """Atualiza movimento, colisões e animações de todos os feitiços ativos."""
        spells_to_remove = []

        for spell in self.current_spells:
            # MOVIMENTO
            if spell.state == "moving":
                
            # Cria um pequeno brilho atrás do feitiço
                if not hasattr(spell, "trail"):
                    spell.trail = []

                # Guarda a posição atual
                spell.trail.append((spell.x, spell.y+int(spell.height/2)))
                if len(spell.trail) > 8:  # limita o tamanho da trilha
                    spell.trail.pop(0)

                # Desenha a trilha com transparência
                for i, (tx, ty) in enumerate(spell.trail):
                    alpha = 255 - i * 30
                    if alpha < 50:
                        alpha = 50
                    surface = pygame.Surface((8, 8), pygame.SRCALPHA)
                    pygame.draw.circle(surface, (255, 255, 180, alpha), (4, 4), 4)
                    self.main_window.screen.blit(surface, (tx, ty))
                
                spell.x += self.spell_velx * self.main_window.delta_time()

                # animação cíclica de voo
                if time() - spell.last_animation >= spell.animation_timeout:
                    spell.last_animation = time()
                    spell.current_frame = (spell.current_frame + 1) % 5
                    spell.image = self.spell_frames[spell.current_frame]
                    spell.width = spell.image.get_width()
                    spell.height = spell.image.get_height()
                    spell.rect = spell.image.get_rect(topleft=(spell.x, spell.y))

                # colisão com inimigos
                for enemy in self.enemy_slots:
                    if not enemy:
                        continue  # slot vazio
                    if spell.collided(enemy):
                        spell.state = "colliding"
                        spell.collided_with = enemy
                        spell.last_collision_animation = time()
                        enemy.life -= spell.damage

                        # inimigo morre?
                        if enemy.life <= 0:
                            enemy.alive = False
                            self.score += 100 if isinstance(enemy, Rato) else 200 if isinstance(enemy, Cachorro) else 300

                        break  # evita múltiplas colisões no mesmo frame

                # saiu da tela
                if spell.x > self.main_window.width:
                    spell.state = "finished"

            # COLISÃO / EXPLOSÃO
            elif spell.state == "colliding":
                if time() - spell.last_collision_animation >= spell.animation_timeout:
                    spell.last_collision_animation = time()
                    spell.current_collision_frame += 1

                    if spell.current_collision_frame < 3:
                        idx = 5 + spell.current_collision_frame
                        spell.image = self.spell_frames[idx]
                        spell.width = spell.image.get_width()
                        spell.height = spell.image.get_height()
                        spell.rect = spell.image.get_rect(topleft=(spell.x, spell.y))
                    else:
                        spell.state = "finished"
            

            # DESENHA (apenas se não acabou)
            if spell.state != "finished":
                spell.draw()
            else:
                spells_to_remove.append(spell)

        # LIMPA feitiços terminados
        for spell in spells_to_remove:
            self.current_spells.remove(spell)


    def pause_menu(self):
        mouse = self.main_window.get_mouse()
        # --- Carrega imagens ---
        fundo = GameImage("src/menu/fundo_menu.jpg")
        fundo.image = pygame.transform.scale(
            fundo.image, (self.main_window.width, self.main_window.height)
        )

        btn_continuar = GameImage("src/menu/play.png")
        btn_menu = GameImage("src/menu/sair.png")

        # Centraliza os botões
        btn_continuar.x = self.main_window.width / 2 - btn_continuar.width / 2
        btn_menu.x = self.main_window.width / 2 - btn_menu.width / 2
        btn_continuar.y = self.main_window.height / 2 - 80
        btn_menu.y = self.main_window.height / 2 + 20

        while True:
            fundo.draw()
            btn_continuar.draw()
            btn_menu.draw()

            self.main_window.draw_text("PAUSADO", self.main_window.width / 2 - 100, 100, 50, (255, 255, 255))

            if mouse.is_over_object(btn_continuar):
                if mouse.is_button_pressed(1):
                    pygame.time.wait(150)
                    return "continuar"

            if mouse.is_over_object(btn_menu):
                if mouse.is_button_pressed(1):
                    pygame.time.wait(150)
                    return "menu"

            self.main_window.update()

    def animate_enemies(self):
        """Atualiza movimento, ataques e animações dos inimigos por slot."""
        for i, e in enumerate(self.enemy_slots):
            if not e:
                continue

            target_x = self.slot_positions[e.target_slot]

            # --- 1️⃣ Movimento até o slot ---
            if e.state == "walking":
                e.x -= e.vel_x * self.main_window.delta_time()
                e.update()
                e.draw()

                # chegou no slot (com margem de 2px)
                if e.x <= target_x + 2:
                    e.x = target_x
                    e.state = "attacking"
                    e.image = pygame.image.load(e.image_file).convert_alpha()  # garante frame neutro
                continue

            # --- 2️⃣ Ataque à distância (corporal) ---
            if e.state == "attacking":
                if time() - e.last_attack >= e.attack_cooldown:
                    e.last_attack = time()

                    # Sacudida / recuo visual
                    e.attack_offset = e.attack_recoil
                    e.state = "recovering"

                    # Aplica dano proporcional à distância
                    damage = int(e.damage * self.slot_damage_multiplier[e.target_slot])
                    self.mago.life -= damage

                # mantém frame neutro de ataque
                e.draw()

            # --- 3️⃣ Recuo após ataque ---
            elif e.state == "recovering":
                # Movimento tipo vai e volta
                phase = sin(e.attack_offset) * 4
                e.x += phase
                e.attack_offset -= 10 * self.main_window.delta_time()

                e.attack_offset -= 50 * self.main_window.delta_time()

                # Quando termina o recuo, volta pro estado de ataque
                if e.attack_offset <= 0:
                    e.attack_offset = 0
                    e.state = "attacking"

                e.draw()

    def animate_mage(self):
        now = time()
        if self.mago.anim_state == True and self.mago.last_animation == 0:
            self.mago.image = pygame.image.load(f"src/magos/mago_atk.png").convert_alpha()
            self.mago.last_animation = now
        elif now - self.mago.last_animation >= 0.5:
            self.mago.image = pygame.image.load(f"src/magos/mago_p.png").convert_alpha()
            self.mago.anim_state = False 
            self.mago.last_animation = 0

    def update_select_box(self):
        if len(self.current_block_options) <= 0:
            color = choice(self.block_colors)
            shape = choice(self.block_shapes)


        self.selection_box.draw()


    def game_loop(self):
        last_limit_increse = 0
        tm = 0
        kb = self.main_window.get_keyboard()
        while True:
            if kb.key_pressed('G') and time()-tm >= 2:
                self.tetris.spawn_piece_manual('O', 'vermelho')
                tm = time()

            # Aumenta o limite de inimigos a cada 60 segundos usando o total time
            if time() - last_limit_increse >=60:
                last_limit_increse = time()
                self.enemie_limit += 1
            
            self.main_window.set_background_color('black')

            # --- pausa ---
            if kb.key_pressed('r'):
                self.launch_rain()
                print(f'{len(self.current_rains)} rains in game.')
            if kb.key_pressed('ESC'):
                pygame.time.wait(150)
                resultado = self.pause_menu()
                if resultado == "menu":
                    self.esc_pressed = time()
                    break
            if self.mago.life <= 0: # game over
                break
            
            if self.tetris.game_over:
                self.tetris.reset()
            self.animate_clouds()
            self.generate_enemies()
            
            # Mage actions
            self.animate_mage()
            if self.tetris.last_cleared_color_counts:
                # DEBUG opcional: print(self.tetris.last_cleared_color_counts)

                for counts in self.tetris.last_cleared_color_counts:
                    # counts agora é um dicionário com keys 'red','green','blue','yellow'
                    red = counts.get("red", 0)
                    green = counts.get("green", 0)
                    blue = counts.get("blue", 0)
                    yellow = counts.get("yellow", 0)

                    # sua ordem original queria verdes, azuis, vermelhos, amarelos
                    verdes = green
                    azuis = blue
                    vermelhos = red
                    amarelos = yellow

                    # Verde → lança feitiço ofensivo
                    if verdes > 0:
                        self.mago.regenerate_life(verdes)
                

                    # Azul → cura vida
                    if azuis > 0:
                        self.mago.regenerate_mana(azuis)

                    # Vermelho → regenera mana
                    if vermelhos > 0:
                        self.mago.anim_state = True
                        self.launch_spell(vermelhos)
                        # posiciona certinho
                        spell = self.current_spells[-1]
                        spell.x = self.mago.x + self.mago.width - 20
                        spell.y = self.mago.y + (self.mago.height // 3)

                    # Amarelo → opcional
                    # if amarelos > 0:
                    #     self.mago.apply_buff("ataque", amarelos)

                # limpa após processar tudo
                self.tetris.last_cleared_color_counts.clear()

            # Enemies animations
            
            # Draws
            self.ceu.draw()
            if len(self.current_clouds) >= 1:
                for cloud in self.current_clouds:
                    cloud.draw()
            self.chao.draw()
            life_color = (0, 245, 0) if self.mago.life >= 70 else (231, 245, 0) if 50 <= self.mago.life < 70 else (255, 0, 0)
            self.castelo.draw()
            self.mago.draw()
            self.placar()
            self.tetris.draw()
            self.animate_enemies()
            self.update_spells()
            self.update_rain()
            self.update_select_box()

            self.main_window.draw_text(f'LIFE: {self.mago.life}', self.mago.x, self.chao.y+25, 20, life_color, 'Arial', True, False)
            self.main_window.draw_text(f'MANA: {self.mago.mana}', self.mago.x + 100, self.chao.y+25, 20, (0, 0, 255), 'Arial', True, False)
            self.main_window.update()
            self.tetris.update()
