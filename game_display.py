import sys
import pygame
from configs import BLACK, WHITE, GRAY
from element import Point, GameElement
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
    def resize_image(self, name, size0=0, size1=0, scale=False):
        assert type(size0) in [tuple, Point] or size0 > 0 or scale
        if type(size0) == tuple: new_w, new_h = size0
        elif type(size0) == Point: new_w, new_h = size0.p()
        else: new_w, new_h = size0, size1
        image = self.images[name]
        w, h = image.get_size()
        if new_w > 0 and new_h == 0:
            new_h = new_w*h/w if scale else new_w
        elif new_w == 0 and new_h > 0:
            new_w = new_h*w/h
        elif new_w == new_h == 0:
            new_w, new_h = scale * w, scale * h
        image = pygame.transform.scale(image, (new_w, new_h))
        return image
    
    #======== 根据场景框裁剪图片 ========#
    def cut_image_by_frame(self, image, pos):
        if type(pos) == Point: pos = pos.p()
        image_w, image_h = image.get_size()
        left = max(0, self.vision_pos.x - pos[0])
        top = max(0, self.vision_pos.y - pos[1])
        new_w = min(image_w, self.vision_pos.x + self.vision_size.x - pos[0]) - left
        new_h = min(image_h, self.vision_pos.y + self.vision_size.y - pos[1]) - top
        new_image = image.subsurface((left, top, new_w, new_h))
        new_pos = left + pos[0], top + pos[1]
        return new_image, new_pos
    
    #======== 根据场景框比例位置给出实际尺寸 ========#
    def generate_abs_pos(self, kx, ky):
        return self.vision_pos.x + kx*self.vision_size.x, self.vision_pos.y + ky*self.vision_size.y
    
    #======== 淡入淡出效果 ========#
    def fading(self):
        time = (pygame.time.get_ticks() - self.time_marker) / 1000
        if self.scene_changing == 2: black_size = self.vision_size
        else: black_size = self.scene_size
        black = self.resize_image('black', black_size)
        black.set_alpha(255 * min(time/self.fade_time, 1, 2.5-time/self.fade_time))
        self.window.blit(black, self.vision_pos.p())
        if 1.2 < time/self.fade_time < 1.3:
            self.current_scene = self.next_scene
            if not self.game_started: self.game_started = True
        if time/self.fade_time > 2.5:
            self.scene_changing = False
        return
    
    #======== 绘制当前画面 ========#
    def draw(self):
        # 获取窗口尺寸，定位场景框，涂黑背景
        width, height = pygame.display.get_window_size()
        if width > height * self.ratio_vision:
            self.vision_pos = Point((width - height*self.ratio_vision)/2, 0)
            self.vision_size = Point(height*self.ratio_vision, height)
            self.scene_size = Point(height*self.ratio_scene, height)
        else:
            self.vision_pos = Point(0, (height - width/self.ratio_vision)/2)
            self.vision_size = Point(width, width/self.ratio_vision)
            self.scene_size = Point(width/self.ratio_vision*self.ratio_scene, width/self.ratio_vision)
        self.window.fill(BLACK)
        # 菜单界面
        if self.current_scene == 'menu':
            # 封面图
            scale = self.vision_size.y / self.images['band_photo'].get_size()[1]
            cover = self.resize_image('band_photo', scale=scale)
            cover.set_alpha(128)
            self.window.blit(cover, (self.vision_pos + (self.vision_size - Point(cover.get_size()))/2).p())
            # 标题
            title = self.resize_image('title_pic', scale=scale*0.36)
            title_w, title_h = title.get_size()
            self.window.blit(title, (self.vision_pos + self.vision_size/2 + Point(-title_w/2, title_h/7)).p())
            # 按钮尺寸
            button = self.resize_image('icon_button', scale=scale*0.8)
            button_w, button_h = button.get_size()
            button_top = self.vision_pos.y + self.vision_size.y / 12
            space = self.vision_pos.x + self.vision_size.x * (0.28 if self.game_started else 0.35)
            # 新游戏按钮
            self.button_new_game = GameElement('rect_', space, button_top, button_w, button_h)
            self.window.blit(button, (space, button_top))
            text = self.text_surface(f'新游戏', 'simhei', int(self.vision_size.y/30))
            self.window.blit(text, text.get_rect(center=self.button_new_game.center))
            # 继续游戏按钮
            if self.game_started:
                self.button_continue = GameElement('rect_', (width-button_w)/2, button_top, button_w, button_h)
                self.window.blit(button, ((width-button_w)/2, button_top))
                text = self.text_surface('继续游戏', 'simhei', int(self.vision_size.y/30))
                self.window.blit(text, text.get_rect(center=self.button_continue.center))
            # 退出按钮
            self.button_exit = GameElement('rect_', width-space-button_w, button_top, button_w, button_h)
            self.window.blit(button, (width-space-button_w, button_top))
            text = self.text_surface('退出', 'simhei', int(self.vision_size.y/30))
            self.window.blit(text, text.get_rect(center=self.button_exit.center))
        # 游戏进行界面
        else:
            # 道具栏
            column_size = self.vision_size.y * self.ratio_column
            space = (self.vision_size.y*(self.ratio_vision-self.ratio_scene) - column_size) / 2
            column_left = self.vision_pos.x + self.scene_size.x + space
            self.item_buttons = [None] * self.item_column_num
            for i in range(self.item_column_num):
                column_top = self.vision_pos.y + self.vision_size.y - (self.item_column_num-i)*(column_size+space)
                self.item_buttons[i] = pygame.Rect(column_left, column_top, column_size, column_size)
                pygame.draw.rect(self.window, GRAY if self.chosen_column == i else WHITE, self.item_buttons[i])
                frame = self.resize_image('frame', column_size)
                self.window.blit(frame, (column_left, column_top))
                if self.item_column[i] is not None:
                    pic_item = self.resize_image('item_' + self.item_column[i], column_size)
                    self.window.blit(pic_item, (column_left, column_top))
            # 菜单图标
            space = self.vision_size.y - self.item_column_num*(column_size+space)
            icon_size = space*0.7
            icon_menu = self.resize_image('icon_menu', icon_size)
            self.window.blit(icon_menu, (column_left+(column_size-icon_size)/2, self.vision_pos.y+(space-icon_size)/2))
            self.button_menu = GameElement('circle', column_left+column_size/2, self.vision_pos.y+space/2, icon_size/2)
            # 游戏场景主体
            self.button_scene = GameElement('rect_', self.vision_pos, self.scene_size)
            scene_scale = self.scene_size.x / self.images[self.current_scene].get_size()[0]
            main_scene = self.resize_image(self.current_scene, scale=scene_scale)
            scene_pos = self.vision_pos.x, self.vision_pos.y + self.scene_size.y - main_scene.get_size()[1]
            main_scene, scene_pos = self.cut_image_by_frame(main_scene, scene_pos)
            self.window.blit(main_scene, scene_pos)
            # 场景：第一面墙，门，床侧面，乐队照片
            if self.current_scene == 'wall_door':
                # 门
                pic_pos = self.generate_abs_pos(0.16, 0.256)
                pic_door = self.resize_image('door', scale=scene_scale*0.96)
                self.window.blit(pic_door, pic_pos)
                if self.door_unlocked: pass
                else:
                    self.button_peephole = GameElement('ellip', 0.2828, 0.46458, 0.0155, 0.0243, 0)
                    self.button_lock = GameElement('rect', 0.1958, 0.5847, 0.2151, 0.6361)
                    self.button_door = GameElement('rect_', pic_pos, pic_door.get_size())
                # 吉他弦3
                if self.band_photo_complete and not self.got_items['string'][2]:
                    pic_pos = self.generate_abs_pos(0.71, 0.3)
                    pic_string = self.resize_image('string', self.vision_size.y*0.08)
                    pic_string = pygame.transform.flip(pic_string, True, False)
                    self.window.blit(pic_string, pic_pos)
                    self.button_string = GameElement('circle_', pic_pos, pic_string.get_size()[0]/2)
                # 相框
                pic_pos = self.generate_abs_pos(0.51, 0.2)
                pic_photo = self.resize_image('band_photo_'+('' if self.band_photo_complete else 'in')+'complete', scale=scene_scale*0.36)
                self.window.blit(pic_photo, pic_pos)
                self.button_photo = GameElement('rect_', pic_pos, pic_photo.get_size())
            # 场景：第二面墙，窗户，床正面，床头柜
            elif self.current_scene == 'wall_window':
                # 窗户
                pic_pos = self.generate_abs_pos(0.34, 0.04)
                pic_window = self.resize_image('curtain_'+('up' if self.curtain_open else 'down'), scale=scene_scale*1.2)
                self.window.blit(pic_window, pic_pos)
                self.button_curtain = GameElement('rect', 0.5151, 0.6185, 0.1028, 0.5306)
                # 拨片3
                if self.curtain_open and not self.got_items['plectrum'][2]:
                    pic_pos = self.generate_abs_pos(0.494, 0.5)
                    pic_plectrum = self.resize_image('plectrum', scale=scene_scale*0.14)
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
                pic_pos = self.generate_abs_pos(0.6, 0.692)
                pic_cupboard = self.resize_image('cupboard_'+('open' if self.cupboard_open else 'close'), scale=scene_scale)
                self.window.blit(pic_cupboard, pic_pos)
                self.button_cupboard = GameElement('rect_', pic_pos, pic_cupboard.get_size())
            # 场景：第三面墙，吉他，乐谱，大箱子
            elif self.current_scene == 'wall_guitar':
                # 吉他
                if not self.got_items['guitar']:
                    pic_pos = self.generate_abs_pos(0.62, 0.25)
                    pic_guitar = self.resize_image(f'guitar_{self.num_string_on_guitar}', scale=scene_scale*1.1)
                    self.window.blit(pic_guitar, pic_pos)
                # 乐谱
                pic_pos = self.generate_abs_pos(0.41, 0.774)
                pic_paper = self.resize_image('paper_'+('up' if self.music_paper_lifted else 'down'), scale=scene_scale*1.2)
                pic_paper, pic_pos = self.cut_image_by_frame(pic_paper, pic_pos)
                self.window.blit(pic_paper, pic_pos)
                self.button_paper = GameElement('rect_', pic_pos, pic_paper.get_size())
                # 大箱子+拨片
                pic_pos = self.generate_abs_pos(0.17, 0.96)
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
                # 书架
                pic_pos = self.generate_abs_pos(0.48, 0.15)
                pic_shelf = self.resize_image('shelf_'+('no' if self.got_items['music_book'] else 'with')+'_book', scale=scene_scale*1.2)
                self.window.blit(pic_shelf, pic_pos)
                self.button_book = GameElement('rect', 0.5168, 0.7992, 0.1514, 0.3153)
                # 小箱子
                pic_pos = self.generate_abs_pos(0.576, 0.321)
                pic_chest = self.resize_image('chest_'+('open' if self.chest_open else 'close'), scale=scene_scale*1.1)
                self.window.blit(pic_chest, pic_pos)
                self.button_chest = GameElement('rect_', pic_pos, pic_chest.get_size())


            # 场景：拉近，乐队照片
            elif self.current_scene == 'zoom_photo':
                # 吉他弦3
                if self.band_photo_complete and not self.got_items['string'][2]:
                    pic_pos = self.generate_abs_pos(0.72, 0.36)
                    pic_string = self.resize_image('string', self.vision_size.y*0.24)
                    pic_string = pygame.transform.flip(pic_string, True, False)
                    self.window.blit(pic_string, pic_pos)
                    self.button_string = GameElement('circle_', pic_pos, pic_string.get_size()[0]/2)
                # 照片
                pic_photo = self.resize_image('band_photo_'+('' if self.band_photo_complete else 'in')+'complete', scale=scene_scale*0.65)
                pic_size = Point(pic_photo.get_size())
                pic_pos = self.vision_pos + (self.scene_size - pic_size) / 2
                self.window.blit(pic_photo, pic_pos.p())
                self.button_photo = GameElement('rect', 0.5235, 0.6496, 0.2444, 0.8166)
            '''
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
                # 床头柜
                pic_pos = self.generate_abs_pos(0.15, 0.155)
                pic_cupboard = self.resize_image('cupboard_'+('open' if self.cupboard_open else 'close'), scale=scene_scale)
                pic_cupboard, pic_pos = image_cut(pic_cupboard, pic_pos)
                self.window.blit(pic_cupboard, pic_pos)
                # 密码框
                self.button_music_note = [None] * 4
                for i in range(4):
                    if self.cupboard_open:
                        pic_pos = self.generate_abs_pos(0.382+i*0.063, 0.453)
                        pic_note = self.resize_image(f'icon_note_{self.cupboard_code[i]}', 0.053*self.KSC*self.vision_height, 0.077*self.vision_height)
                    else:
                        pic_pos = self.generate_abs_pos(0.372+i*0.065, 0.362-i*0.001)
                        pic_note = self.resize_image(f'icon_note_{self.cupboard_code[i]}', 0.057*self.KSC*self.vision_height, 0.105*self.vision_height)
                    self.window.blit(pic_note, pic_pos)
                    self.button_music_note[i] = GameElement('rect_', pic_pos, pic_note.get_size())
                # 抽屉，吉他弦2，拨片2
                if not self.cupboard_open: self.button_cupboard = GameElement('rect', 0.26, 0.746, 0.315, 0.486)
                else:
                    self.button_cupboard = GameElement('rect', 0.215, 0.791, 0.315, 0.589)
                    if not self.got_items['plectrum'][1]:
                        pic_pos = self.generate_abs_pos(0.4, 0.35)
                        pic_plectrum = self.resize_image('plectrum', scale=0.06*scene_scale)
                        self.window.blit(pic_plectrum, pic_pos)
                        self.button_plectrum = GameElement('rect_', pic_pos, pic_plectrum.get_size())
                    if not self.got_items['string'][1]:
                        pic_pos = self.generate_abs_pos(0.56, 0.35)
                        pic_string = self.resize_image('string', scale=0.07*scene_scale)
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
                
            
            
            '''
            # 查看道具：音乐书 or 乐器图片 or 照片 or 信
            if self.showing_detail is not None:
                black = self.resize_image('black', self.scene_size)
                black.set_alpha(180)
                self.window.blit(black, self.vision_pos.p())
                if self.showing_detail == 'lock':
                    pass
                else:
                    pic_check = self.resize_image('item_'+self.showing_detail, self.scene_size.y)
                    self.window.blit(pic_check, (self.vision_pos.x+(self.scene_size.x-self.scene_size.y)/2, self.vision_pos.y))
                    if self.showing_detail == 'music_book': self.button_book = GameElement('rect', 0.3379, 0.659, 0.16, 0.883)
            # 边框
            frame = self.resize_image('frame', self.scene_size)
            #self.window.blit(frame, self.vision_pos.p())
            # 左右箭头
            arrow_width = 0.04 * self.vision_size.y
            space = 0.03 * self.vision_size.y
            if 'wall' in self.current_scene and self.showing_detail is None:
                icon_size = Point(arrow_width, arrow_width*self.ratio_arrow)
                icon_pos = self.vision_pos + Point(space, (self.vision_size.y - icon_size.y)/2)
                icon_go_left = self.resize_image('icon_go_left', icon_size)
                self.window.blit(icon_go_left, icon_pos.p())
                self.button_go_left = GameElement('rect_', icon_pos, icon_size)
                icon_pos.x = self.vision_pos.x + self.scene_size.x - space - arrow_width
                icon_go_right = self.resize_image('icon_go_right', icon_size)
                self.window.blit(icon_go_right, icon_pos.p())
                self.button_go_right = GameElement('rect_', icon_pos, icon_size)
            # 返回箭头
            if 'zoom' in self.current_scene or self.showing_detail is not None:
                icon_size = Point(arrow_width*self.ratio_arrow, arrow_width)
                icon_pos = self.vision_pos + Point((self.scene_size.x - icon_size.x)/2, self.scene_size.y - space - arrow_width)
                icon_go_back = 'icon_go_back'
                if self.showing_detail is not None or self.current_scene == 'zoom_peephole':
                    icon_go_back = icon_go_back + '_white'
                icon_go_back = self.resize_image(icon_go_back, icon_size)
                self.window.blit(icon_go_back, icon_pos.p())
                self.button_go_back = GameElement('rect_', icon_pos, icon_size)
        # 场景淡入淡出
        if self.scene_changing: self.fading()
        # 更新显示
        pygame.display.flip()


##########################################################

if __name__ == "__main__":
    print('\nThis is STAGE[2] (display) of the game.')
    a = input()
