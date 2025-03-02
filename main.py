#Libraries

#From File " SimplePygame.py"
from SimplePyGame import Game, Sprite, pygame


#Start
print("Starting...")

#Sprites
#Knight graphics
KNIGHT_GRAPHICS = [
    "images\characters\knight\knight_idle_anim_f0.png",
    "images\characters\knight\knight_run_anim_f0.png"
]

#Set up
game = Game("Simple RPG")
game.background_color = (128, 255, 96)

#Adding the sprites
#Knight: (376,276)-> Position of the knight when it is added , (48,48)-> The size of the knight when added into the programme
knight = game.add_sprite(Sprite("Knight", KNIGHT_GRAPHICS, (376 , 276) , (48,48) ))

#Running ... 
game.run()