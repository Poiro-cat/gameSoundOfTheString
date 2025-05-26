import sys
import pygame
from game_display import GameDisplay



################ 游戏运行 ################

class GameRun(GameDisplay):
    
    #======== 运行 ========#
    def run(self):
        self.initialize_state()
        self.play_music('rock', -1, 0.1)
        ###
        self.game_started = True
        self.play_music('beethoven', -1, 0.2)
        self.current_scene = 'wall_desk'
        #self.band_photo_complete = True
        self.item_column[:4] = ['plectrum']*3 + ['music_book']
        ###
        self.clock = pygame.time.Clock()
        running = True
        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.scene_changing: continue
                if event.type == pygame.KEYDOWN:
                    self.handle_keydown(event.key)                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    x, y = event.pos
                    self.handle_click(x, y, event.button)
            # 绘制游戏
            self.draw()
            # 控制帧率
            self.clock.tick(60)
        self.game_quit()


##########################################################

if __name__ == "__main__":
    try:
        game = GameRun(1280, 720)
        game.run()
    except Exception as e:
        print('Error info:', e)
        a = input()
