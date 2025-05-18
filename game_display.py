import sys
import pygame
from configs import WINDOW_WIDTH, WINDOW_HEIGHT, BLACK, WHITE
from element import GameElement
from game_interact import GameInteract


################ 游戏画面显示 ################

class GameDisplay(GameInteract):
    
    #======== 生成文本对象 ========#
    def text_surface(self, text, fontfamily, fontsize, color=BLACK, antialias=True):
        font_path = pygame.font.match_font(fontfamily)
        if not font_path:
            # 如果没有找到中文字体，使用默认字体
            default_font = pygame.font.get_default_font()
            font_path = pygame.font.match_font(default_font)
        self.game_font = pygame.font.Font(font_path, fontsize)
        return self.game_font.render(text, antialias, color)
    
    #======== 调整图片尺寸 ========#
    def resize_image(self, name, new_width=0, new_height=0, scale=0):
        assert new_width > 0 and scale == 0 or scale > 0 and new_width == new_height == 0
        if new_width > 0 and new_height == 0:
            new_height = new_width
        image = self.images[name]
        if scale > 0:
            new_width, new_height = image.get_size()
            new_width *= scale
            new_height *= scale
        image = pygame.transform.scale(image, (new_width, new_height))
        return image
    
    #======== 根据场景框比例位置给出实际尺寸 ========#
    def generate_abs_pos(self, kx, ky):
        return self.scene_pos[0] + kx*self.KSC*self.scene_height, self.scene_pos[1] + ky*self.scene_height
    
    #======== 绘制当前画面 ========#
    def draw(self):
        # 淡入淡出效果
        def fading():
            time = (pygame.time.get_ticks() - self.time_marker) / 1000
            if self.scene_changing == 2:
                black_w, black_h = pygame.display.get_window_size()
                self.scene_pos = 0, 0
            else:
                black_w, black_h = self.KSC*self.scene_height, self.scene_height
            black = self.resize_image('black', black_w, black_h)
            black.set_alpha(255 * min(time/self.fade_time, 1, 2.5-time/self.fade_time))
            self.window.blit(black, self.scene_pos)
            if 1.2 < time/self.fade_time < 1.3:
                self.current_scene = self.next_scene
                if not self.game_started: self.game_started = True
            if time/self.fade_time > 2.5:
                self.scene_changing = False
            return
        # 获取窗口尺寸，涂黑背景
        width, height = pygame.display.get_window_size()
        self.window.fill(BLACK)
        # 菜单
        if self.current_scene == 'menu':
            # 封面图
            cover_w, cover_h = self.images['band_photo'].get_size()
            scale = max(width/cover_w, height/cover_h)
            cover = self.resize_image('band_photo', scale=scale)
            cover.set_alpha(128)
            self.window.blit(cover, ((width-scale*cover_w)/2, (height-scale*cover_h)/2))
            # 标题
            title_w, title_h = self.images['title_pic'].get_size()
            scale = max(0.36, height*0.36/title_h)
            title = self.resize_image('title_pic', scale=scale)
            self.window.blit(title, ((width-scale*title_w)/2, height/2-scale*title_h))
            # 按钮尺寸
            button_width, button_height = self.images['icon_button'].get_size()
            button_left = (width-button_width)/2
            space = 1.25 * button_height
            max_top = [i*height - button_height/2 for i in [0.6, 0.72, 0.75, 0.84]]
            top_0 = max(WINDOW_HEIGHT/2, max_top[0])
            # 新游戏按钮
            self.button_new_game = GameElement('rect_', button_left, top_0, button_width, button_height)
            self.window.blit(self.images['icon_button'], (button_left, top_0))
            text = self.text_surface(f'新游戏', 'simhei', 24)
            self.window.blit(text, text.get_rect(center=self.button_new_game.center))
            # 继续游戏按钮
            if self.game_started:
                button_top = max(top_0+space, max_top[1])
                self.button_continue = GameElement('rect_', button_left, button_top, button_width, button_height)
                self.window.blit(self.images['icon_button'], (button_left, button_top))
                text = self.text_surface('继续游戏', 'simhei', 24)
                self.window.blit(text, text.get_rect(center=self.button_continue.center))
            # 退出按钮
            if self.game_started: button_top = max(top_0+space*2, max_top[3])
            else: button_top = max(top_0+space, max_top[2])
            self.button_exit = GameElement('rect_', button_left, button_top, button_width, button_height)
            self.window.blit(self.images['icon_button'], (button_left, button_top))
            text = self.text_surface('退出', 'simhei', 24)
            self.window.blit(text, text.get_rect(center=self.button_exit.center))
        # 游戏进行界面
        else:
            self.edge_space = 15
            # 画面主体
            self.scene_height = max(self.KD*WINDOW_HEIGHT, min(self.KD*width/self.KSC, height))
            self.scene_pos = (max(0, (self.KD*width-self.KSC*self.scene_height)/2), max(0, (height-self.scene_height)/2))
            self.button_scene = GameElement('rect_', self.scene_pos, self.KSC*self.scene_height, self.scene_height)
            main_scene = self.resize_image(self.current_scene, self.KSC*self.scene_height, self.scene_height)
            self.window.blit(main_scene, self.scene_pos)
            # 道具栏
            column_space = 15
            column_left = self.scene_pos[0] + self.scene_height*self.KSC + self.edge_space + column_space
            column_width = max(0.07*WINDOW_WIDTH, min(0.07*width, (height-column_space)/self.items_column_num-column_space))
            self.item_buttons = [None] * self.items_column_num
            for i in range(self.items_column_num):
                column_y = column_width*i + column_space*(i+1)
                self.item_buttons[i] = pygame.Rect(column_left, column_y, column_width, column_width)
                pygame.draw.rect(self.window, WHITE, self.item_buttons[i])
                frame = self.resize_image('frame', column_width)
                self.window.blit(frame, (column_left, column_y))
                if self.items_column[i] is not None:
                    pic_item = self.resize_image('item_' + self.items_column[i], column_width)
                    self.window.blit(pic_item, (column_left, column_y))
            if self.chosen_item is not None:
                column_add = 8
                column_y = column_width*self.chosen_item + column_space*(self.chosen_item+1) - column_add
                frame = pygame.Rect(column_left-column_add, column_y, column_width+2*column_add, column_width+2*column_add)
                pygame.draw.rect(self.window, WHITE, frame, 3)
            # 游戏场景
            scene_scale = self.scene_height / self.images[self.current_scene].get_size()[1]
            def image_cut(image, pos):
                image_w, image_h = image.get_size()
                left = max(0, self.scene_pos[0] - pos[0])
                top = max(0, self.scene_pos[1] - pos[1])
                new_w = min(image_w, self.scene_pos[0]+self.KSC*self.scene_height-pos[0]) - left
                new_h = min(image_h, self.scene_pos[1]+self.scene_height-pos[1]) - top
                new_image = image.subsurface((left, top, new_w, new_h))
                new_pos = left + pos[0], top + pos[1]
                return new_image, new_pos
            # 场景：第一面墙，门，床侧面，乐队照片
            if self.current_scene == 'wall_door':
                # 门
                pic_pos = self.generate_abs_pos(0.16, 0.296)
                pic_door = self.resize_image('door', scale=scene_scale)
                self.window.blit(pic_door, pic_pos)
                self.button_peephole = GameElement('circle', 0.2767, 0.49, 0.017)
                # 吉他弦3
                if self.band_photo_complete and not self.got_items['string'][2]:
                    pic_pos = self.generate_abs_pos(0.78, 0.3)
                    pic_string = self.resize_image('string', self.scene_height*0.08)
                    self.window.blit(pic_string, pic_pos)
                    self.button_string = GameElement('circle_', pic_pos, pic_string.get_size()[0]/2)
                # 相框
                pic_pos = self.generate_abs_pos(0.54, 0.2)
                pic_photo = self.resize_image('band_photo_'+('' if self.band_photo_complete else 'in')+'complete', scale=scene_scale*0.4)
                self.window.blit(pic_photo, pic_pos)
                self.button_photo = GameElement('rect_', pic_pos, pic_photo.get_size())
            # 场景：第二面墙，窗户，床正面，床头柜
            elif self.current_scene == 'wall_window':
                # 窗户
                pic_pos = self.generate_abs_pos(0.35, 0.04)
                pic_window = self.resize_image('curtain_'+('up' if self.curtain_open else 'down'), scale=scene_scale*1.3)
                self.window.blit(pic_window, pic_pos)
                self.button_curtain = GameElement('rect', 0.517, 0.628, 0.1, 0.525)
                # 拨片3
                if self.curtain_open and not self.got_items['plectrum'][2]:
                    pic_pos = self.generate_abs_pos(0.538, 0.494)
                    pic_plectrum = self.resize_image('plectrum', scale=scene_scale*0.16)
                    self.window.blit(pic_plectrum, pic_pos)
                    self.button_plectrum = GameElement('rect_', pic_pos, pic_plectrum.get_size())
                # 枕头
                pic_pos = self.generate_abs_pos(0.28, 0.65)
                pic_pillow = self.resize_image('pillow_'+('scratched' if self.pillow_scratched else 'good'), scale=scene_scale*1.2)
                self.window.blit(pic_pillow, pic_pos)
                self.button_pillow = GameElement('rect_', pic_pos, pic_pillow.get_size())
                # 乐器卡片
                if self.pillow_scratched and not self.got_items['instrument_pics']:
                    pic_pos = self.generate_abs_pos(0.34, 0.703)
                    pic_card = self.resize_image('instrument_pics', scale=scene_scale*0.11)
                    pic_card = pygame.transform.rotate(pic_card, 5)
                    self.window.blit(pic_card, pic_pos)
                # 床头柜
                pic_pos = self.generate_abs_pos(0.645, 0.72)
                pic_cupboard = self.resize_image('cupboard_'+('open' if self.cupboard_open else 'close'), scale=scene_scale)
                self.window.blit(pic_cupboard, pic_pos)
                self.button_cupboard = GameElement('rect_', pic_pos, pic_cupboard.get_size())
            # 场景：第三面墙，吉他，乐谱，大箱子
            elif self.current_scene == 'wall_guitar':
                # 吉他
                if not self.got_items['guitar']:
                    pic_pos = self.generate_abs_pos(0.66, 0.32)
                    pic_guitar = self.resize_image(f'guitar_{self.num_string_on_guitar}', scale=scene_scale*1.1)
                    self.window.blit(pic_guitar, pic_pos)
                # 乐谱
                pic_pos = self.generate_abs_pos(0.43, 0.8)
                pic_paper = self.resize_image('paper_'+('up' if self.music_paper_lifted else 'down'), scale=scene_scale*1.2)
                pic_paper, pic_pos = image_cut(pic_paper, pic_pos)
                self.window.blit(pic_paper, pic_pos)
                self.button_paper = GameElement('rect_', pic_pos, pic_paper.get_size())
                # 大箱子+拨片
                pic_pos = self.generate_abs_pos(0.18, 0.97)
                pic_chest = self.resize_image('chest_big_'+('open' if self.chest_big_open else 'close'), scale=scene_scale)
                pic_pos = pic_pos[0], pic_pos[1] - pic_chest.get_size()[1]
                self.window.blit(pic_chest, pic_pos)
                self.button_chest = GameElement('rect_', pic_pos, pic_chest.get_size())
                pic_plectrum = self.resize_image('plectrum', scale=scene_scale*0.15)
                pic_plectrum.set_alpha(180)
                for i in range(3):
                    if self.plectrum_on_chest[i]:
                        pic_pos = self.generate_abs_pos([0.212, 0.279, 0.3489][i], 0.8815)
                        self.window.blit(pic_plectrum, pic_pos)
                
            # 场景：第四面墙，书桌，收音机，书架
            elif self.current_scene == 'wall_desk':
                pass

            
            # 场景：拉近，乐队照片
            elif self.current_scene == 'zoom_photo':
                # 吉他弦3
                if self.band_photo_complete and not self.got_items['string'][2]:
                    pic_pos = self.generate_abs_pos(0.8, 0.36)
                    pic_string = self.resize_image('string', self.scene_height*0.24)
                    self.window.blit(pic_string, pic_pos)
                    self.button_string = GameElement('circle_', pic_pos, pic_string.get_size()[0]/2)
                # 照片
                pic_photo = self.resize_image('band_photo_'+('' if self.band_photo_complete else 'in')+'complete', scale=scene_scale*0.7)
                pic_w, pic_h = pic_photo.get_size()
                pic_pos = self.scene_pos[0]+(self.KSC*self.scene_height-pic_w)/2, self.scene_pos[1]+(self.scene_height-pic_h)/2
                self.window.blit(pic_photo, pic_pos)
                self.button_photo = GameElement('rect', 0.523, 0.65, 0.277, 0.776)
            # 场景：拉近，床上枕头
            elif self.current_scene == 'zoom_pillow':
                # 枕头
                pic_pos = self.generate_abs_pos(0.365, 0.315)
                pic_pillow = self.resize_image('pillow_'+('scratched' if self.pillow_scratched else 'good'), scale=scene_scale*1.2)
                self.window.blit(pic_pillow, pic_pos)
                self.button_pillow = GameElement('rect_', pic_pos, pic_pillow.get_size())
                # 乐器卡片
                if self.pillow_scratched and not self.got_items['instrument_pics']:
                    pic_pos = self.generate_abs_pos(0.51, 0.44)
                    pic_card = self.resize_image('instrument_pics', scale=scene_scale*0.11)
                    pic_card = pygame.transform.rotate(pic_card, 5)
                    self.window.blit(pic_card, pic_pos)
                    self.button_card = GameElement('tri', [0.5156, 0.4479], [0.586, 0.4384], [0.5913, 0.5189])
            # 场景：拉近，床头柜
            elif self.current_scene == 'zoom_cupboard':
                pic_pos = self.generate_abs_pos(0.15, 0.155)
                pic_cupboard = self.resize_image('cupboard_'+('open' if self.cupboard_open else 'close'), scale=scene_scale)
                pic_cupboard, pic_pos = image_cut(pic_cupboard, pic_pos)
                self.window.blit(pic_cupboard, pic_pos)
                self.button_music_note = [None] * 4
                for i in range(4):
                    if self.cupboard_open:
                        pic_pos = self.generate_abs_pos(0.382+i*0.063, 0.453)
                        pic_note = self.resize_image(f'icon_note_{self.cupboard_code[i]}', 0.053*self.KSC*self.scene_height, 0.077*self.scene_height)
                    else:
                        pic_pos = self.generate_abs_pos(0.372+i*0.065, 0.362-i*0.001)
                        pic_note = self.resize_image(f'icon_note_{self.cupboard_code[i]}', 0.057*self.KSC*self.scene_height, 0.105*self.scene_height)
                    self.window.blit(pic_note, pic_pos)
                    self.button_music_note[i] = GameElement('rect_', pic_pos, pic_note.get_size())
                if not self.cupboard_open: self.button_cupboard = GameElement('rect', 0.26, 0.746, 0.315, 0.486)
                else:
                    self.button_cupboard = GameElement('rect', 0.215, 0.791, 0.315, 0.589)
                    if not self.got_items['plectrum'][1]:
                        pic_pos = self.generate_abs_pos(0.38, 0.35)
                        pic_plectrum = self.resize_image('plectrum', scale=0.06*scene_scale)
                        self.window.blit(pic_plectrum, pic_pos)
                        self.button_plectrum = GameElement('rect_', pic_pos, pic_plectrum.get_size())
                    if not self.got_items['string'][1]:
                        pic_pos = self.generate_abs_pos(0.5, 0.33)
                        pic_string = self.resize_image('string', scale=0.06*scene_scale)
                        self.window.blit(pic_string, pic_pos)
                        self.button_string = GameElement('rect_', pic_pos, pic_string.get_size())
                    
            # 场景：拉近，大箱子+拨片
            elif self.current_scene == 'zoom_chest_big':
                pic_pos = self.generate_abs_pos(0.18, 0.91)
                pic_chest = self.resize_image('chest_big_'+('open' if self.chest_big_open else 'close'), scale=scene_scale)
                pic_pos = pic_pos[0], pic_pos[1] - pic_chest.get_size()[1]
                self.window.blit(pic_chest, pic_pos)
                self.button_chest = GameElement('rect_', pic_pos, pic_chest.get_size())
                pic_plectrum = self.resize_image('plectrum', scale=scene_scale*0.16)
                pic_plectrum.set_alpha(180)
                for i in range(3):
                    if self.plectrum_on_chest[i]:
                        pic_pos = self.generate_abs_pos([0.272, 0.467, 0.668][i], 0.65)
                        self.window.blit(pic_plectrum, pic_pos)
                self.button_chest_hole = [GameElement('rect_', 0.258+i*0.196, 0.626, 0.105, 0.152) for i in range(3)]
            
            
            # 场景：拉近，书桌抽屉
            elif self.current_scene == 'zoom_drawer':
                if self.drawer_open:
                    if not self.got_items['tape']:
                        pic_pos = self.generate_abs_pos(0.36, 0.33)
                        pic_tape = self.resize_image('item_tape', scale=0.05*scene_scale)
                        self.window.blit(pic_tape, pic_pos)
                        self.button_tape = GameElement('rect', 0.368, 0.436, 0.342, 0.406)
                    if not self.got_items['knife']:
                        pic_pos = self.generate_abs_pos(0.5, 0.33)
                        pic_knife = self.resize_image('item_knife', scale=0.08*scene_scale)
                        self.window.blit(pic_knife, pic_pos)
                        self.button_knife = GameElement('ellip', 0.5324, 0.3816, 0.0397, 0.0064, 0.71409)
                
            
            
            
            
            # 左右箭头
            arrow_width = 0.04 * self.scene_height
            if 'wall' in self.current_scene:
                icon_x = self.scene_pos[0] + 1.6*self.edge_space
                icon_y = self.scene_pos[1] + self.scene_height/2 - self.KAR*arrow_width/2
                icon_go_left = self.resize_image('icon_go_left', arrow_width, self.KAR*arrow_width)
                self.window.blit(icon_go_left, (icon_x, icon_y))
                self.button_go_left = GameElement('rect_', icon_x, icon_y, arrow_width, self.KAR*arrow_width)
                icon_x = self.scene_pos[0] + self.KSC*self.scene_height - 1.6*self.edge_space - arrow_width
                icon_go_right = self.resize_image('icon_go_right', arrow_width, self.KAR*arrow_width)
                self.window.blit(icon_go_right, (icon_x, icon_y))
                self.button_go_right = GameElement('rect_', icon_x, icon_y, arrow_width, self.KAR*arrow_width)
            # 查看道具：音乐书 or 乐器图片 or 照片 or 信
            if self.showing_detail is not None:
                black = self.resize_image('black', self.KSC*self.scene_height, self.scene_height)
                black.set_alpha(180)
                self.window.blit(black, self.scene_pos)
            #if self.showing_detail == 'my_photo':
                pic_check = self.resize_image('item_'+self.showing_detail, self.scene_height)
                self.window.blit(pic_check, (self.scene_pos[0]+self.scene_height*(self.KSC-1)/2, self.scene_pos[1]))
            # 下箭头/返回箭头
            if 'zoom' in self.current_scene or self.showing_detail is not None:
                icon_x = self.scene_pos[0] + self.scene_height*self.KSC/2 - self.KAR*arrow_width/2
                icon_y = self.scene_pos[1] + self.scene_height - 1.6*self.edge_space - arrow_width
                icon_go_back = 'icon_go_back'
                if self.showing_detail is not None or self.current_scene == 'zoom_peephole':
                    icon_go_back = icon_go_back + '_white'
                icon_go_back = self.resize_image(icon_go_back, self.KAR*arrow_width, arrow_width)
                self.window.blit(icon_go_back, (icon_x, icon_y))
                self.button_go_back = GameElement('rect_', icon_x, icon_y, self.KAR*arrow_width, arrow_width)
            # 场景淡入淡出
            if self.scene_changing == 1: fading()
            # 边框
            frame = self.resize_image('frame', self.KSC*self.scene_height, self.scene_height)
            self.window.blit(frame, self.scene_pos)
            # 菜单图标
            self.icon_menu_radius = 0.04 * self.scene_height
            icon_menu = self.resize_image('icon_menu', 2*self.icon_menu_radius)        
            self.window.blit(icon_menu, (self.edge_space, self.edge_space))
            self.button_menu = GameElement('circle_', self.edge_space, self.edge_space, self.icon_menu_radius)
        # 场景淡入淡出
        if self.scene_changing == 2: fading()
        # 更新显示
        pygame.display.flip()


##########################################################

if __name__ == "__main__":
    print('\nThis is STAGE[2] (display) of the game.')
    a = input()