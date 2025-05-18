import sys
import pygame
from game_display import GameDisplay



################ 游戏运行 ################

class GameRun(GameDisplay):
    
    #======== 运行 ========#
    def run(self):
        self.initialize_state()
        ###
        self.game_started = True
        self.current_scene = 'zoom_cupboard'
        self.cupboard_unlocked = True
        #self.items_column[1] = 'knife'
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
        game = GameRun(1080, 750)
        game.run()
    except Exception as e:
        print('Error info:', e)
        a = input()