import pygame,random,math
from painter import Painter
from cell import Cell,CellList
from player import Player
from hud import HUD
from grid import Grid
from drawable import Drawable
from camera import Camera
import common

class agarGame :
    def __init__(self) -> None:
        self.players = {}
        self.counter = 0
        # Initialize essential entities
        self.cam = Camera()
        self.clock = pygame.time.Clock()
        self.grid = Grid(common.MAIN_SURFACE, self.cam)
        self.cells = CellList(common.MAIN_SURFACE, self.cam, 2000)
        self.painter = Painter()
        self.current_player = Player(common.MAIN_SURFACE,self.cam,1, "GeoVas")
        self.blob2 = Player(common.MAIN_SURFACE,self.cam,2,"Blob2")
        self.blob3 = Player(common.MAIN_SURFACE,self.cam,3,"Blob3")
        
        self.hud = HUD(common.MAIN_SURFACE, self.cam,self.current_player, self.players)
        self.drawOnScreen()
        
        #add players to dict
        
        self.add_player(self.blob2)
        self.add_player(self.blob3)
        
        
        print('Players: ', self.players)
        
    def drawOnScreen(self):
        self.painter.add(self.grid) 
        self.painter.add(self.cells)
        self.painter.add(self.hud)
        self.painter.add(self.current_player)
        
        
        print('Painter array: ', self.painter.paintings)

    def startGameLoop(self):
        # Game main loop
        while(True):
            
            self.clock.tick(140)
            
            self.cell = Cell(common.MAIN_SURFACE, self.cam) 
            self.cells.add(self.cell)
            
            self.reactToInput()
            
            self.current_player.move()    
                
            self.current_player.feed(self.players, self.painter.paintings)    
            
            self.current_player.collisionDetection(self.cells.list)
            self.cam.update(self.current_player)
            
            
            
            #self.remove_player(player2remove)
            
            common.MAIN_SURFACE.fill((242,251,255))
            # Uncomment next line to get dark-theme
            #surface.fill((0,0,0))
            self.painter.paint()
            # Start calculating next frame
            pygame.display.flip()
            
    def reactToInput(self):
        for e in pygame.event.get():
                if(e.type == pygame.KEYDOWN):
                    if(e.key == pygame.K_ESCAPE):
                        pygame.quit()
                        print("Quiting game!")
                        quit()
                    if(e.key == pygame.K_SPACE):
                        #del(self.cam)
                        self.current_player.split()
                    #if(e.key == pygame.K_w):
                        
                if(e.type == pygame.QUIT):
                    pygame.quit()
                    quit()
                    
    def add_player(self,player):
        #tmpid = self.generateID(player)
        self.players[self.counter] = player
        self.counter += 1
        self.painter.add(player)
        
    def remove_player(self,player):
        self.players.pop(player)
        pass
    
    def update_player(self,player):
        pass
        
    def configGame(self,configs):
        pass
        
            
    def get_player_playing(self):
        return self.current_player


    """ retorna a lista de jogadores menos o proprio player"""
    def getPlayersPlaying(self):
        return self.players.values()