import pygame;
import pygame.locals;
import pygame.transform;
from operator import attrgetter

DEBUG_MODE = True

class Sprite:
  def __init__(self, name, imageFile, position = (0,0), size = False, mirror = True):
    self.name = name
    self.pos = pygame.Vector2(position[0],position[1])
    self.img_index = 0
    self.animSeq = (0,0)
    self.animSpeed = 1
    self.animTimer = 0
    self.direction = 0
    self.layer = 0
    self.hidden = False
    self.img = []
    mirrorList = mirror
    if mirrorList == True:
      mirrorList = []
    if isinstance(imageFile, str):
      self.load_img(imageFile, size, mirrorList);
    else:
      for fname in imageFile:
        self.load_img(fname, size, mirrorList);
    if mirrorList:
      for img in mirrorList:
        self.img.append(img)
    self.width = self.img[0].get_width()
    self.height = self.img[0].get_height()
    self.halfwidth = self.width/2
    self.halfheight = self.height/2
    if DEBUG_MODE:
      print (name+": Loaded "+str(len(self.img))+" images.")
  
  def load_img(self, imageFile, size, mirror):
    loadedImg = pygame.image.load(imageFile)
    if size != False:
      loadedImg = pygame.transform.scale(loadedImg,size)
    self.img.append(loadedImg)
    if mirror != False:
      mirror.append(pygame.transform.flip(loadedImg, True, False))

  def set_anim(self, anim, speed):
    self.animSeq = anim
    self.img_index = anim[0]
    self.animSpeed = speed

  def update_anim(self):
    self.animTimer += 1
    if self.animTimer > self.animSpeed:
      self.animTmer = 0
      self.img_index += 1
      if self.img_index > self.animSeq[1]:
        self.img_index = self.animSeq[0]

  def update(self, eventList, spriteList):
    self.update_anim()
      
  def draw(self, gameDisplay):
    if not self.hidden:
      img = pygame.transform.rotate(self.img[self.img_index],self.direction)
      gameDisplay.blit(img, self.pos - (self.halfwidth, self.halfheight))
      
  def touch_xy(self, x, y):
    if x < (self.pos.x - self.halfwidth):
      return False
    elif x > (self.pos.x + self.halfwidth):
      return False
    elif y < (self.pos.y - self.halfheight):
      return False
    elif y > (self.pos.y + self.halfheight):
      return False
    else:
      return True

  def touch_point(self, pt):
    return self.touch_xy(pt[0], pt[1])
      
  def touch_sprite(self, sprite):
    if sprite == self:
      return False
    elif abs(sprite.pos.x-self.pos.x) >= (self.halfwidth + sprite.halfwidth):
      return False
    elif abs(sprite.pos.y-self.pos.y) >= (self.halfheight + sprite.halfheight):
      return False
    else:
      return True

  def touch_any(self, spritelist):
    for sprite in spritelist:
      if self.touch_sprite(sprite):
        return True
    return False

  def touch_list(self, spritelist):
    touches = []
    for sprite in spritelist:
      if self.touch_sprite(sprite):
        touches.append(sprite)
    return touches


class Game:
  def __init__(self, name, screenSize = (800,600) , fullscreen = True):
    pygame.init()
    displayOptions = (pygame.FULLSCREEN | pygame.HWSURFACE | pygame.SCALED) if fullscreen else pygame.HWSURFACE | pygame.SCALED
    self.name = name
    self.fullscreen = fullscreen
    self.screenSize = screenSize
    self.display = pygame.display.set_mode(screenSize, displayOptions)
    self.background_color = (0,32,64)
    self.clock = pygame.time.Clock()
    self.frameCounter = 0
    self.sprites = []
    self.spriteAddBuffer = []
    self.spriteDelBuffer = []
    self.eventList = []
    self.keyStates = {} # 0 release, 1 down, 2 hold, 3 up
    self.exiting = False
    self.paused = False
    self.quitKey = pygame.locals.K_ESCAPE
    pygame.display.set_caption(name)
    Game.obj = self
    #else:
    #   print ("Singleton error in Game: Cannot have multiple Games in same application.")
    #   sys.exit(1)
          
  def add_sprite(self, sprite):
    if (sprite in self.sprites) or (sprite in self.spriteAddBuffer) or (sprite in self.spriteDelBuffer):
      print (str(self.frameCounter)+" Warning: Can't add sprite "+sprite.name+". It is already in the scene.")
    else:
      self.spriteAddBuffer.append(sprite)
    return sprite
          
  def rmv_sprite(self, sprite):
    if (sprite in self.spriteDelBuffer):
      print (str(self.frameCounter)+" Warning: Can't remove sprite "+sprite.name+". It is already being removed.")
    elif not (sprite in self.sprites or sprite in self.spriteAddBuffer):
      print (str(self.frameCounter)+" Warning: Can't remove sprite "+sprite.name+". It is not in the scene.")
    else:
      self.spriteDelBuffer.append(sprite)
    return sprite
  
  def key_pressed(self,key):
    return (key in self.keyStates) and (self.keyStates[key] == 1)
  
  def key_held(self, key):
    return (key in self.keyStates) and (self.keyStates[key] > 0)
  
  def key_released(self, key):
    return (key in self.keyStates) and (self.keyStates[key] == 3)

  def preUpdate(self):
    self.eventList = pygame.event.get()
    for key in self.keyStates:
      if self.keyStates[key] == 1:
        self.keyStates[key] = 2
      elif self.keyStates[key] == 3:
        self.keyStates[key] = 0
    for event in self.eventList:
      if event.type == pygame.KEYDOWN:
        self.keyStates[event.key] = 1
        if event.key == self.quitKey:
            self.exiting = True
      elif event.type == pygame.KEYUP:
        self.keyStates[event.key] = 3

  def update(self):
    for event in self.eventList:
      if event.type == pygame.QUIT:
        self.exiting = True
      elif event.type == pygame.KEYDOWN:
        if event.key == self.quitKey:
          self.exiting = True
        
  def updateSprites(self):
    for sprite in self.sprites:
      if (not self.paused) or sprite.runWhilePaused:
        sprite.update(self.eventList, self.sprites)
  
  def postUpdate(self):
    for sprite in self.spriteAddBuffer:
      self.sprites.append(sprite)
    for sprite in self.spriteDelBuffer:
      self.sprites.remove(sprite)
    self.spriteAddBuffer = []
    self.spriteDelBuffer = []
  
  def draw(self):
    self.display.fill(self.background_color)
    #sort sprites by Z order
    self.sprites.sort(key=attrgetter('layer'))
    for sprite in self.sprites:
      sprite.draw(self.display)
          
  def run(self):
    while not self.exiting:
      self.update()
      self.updateSprites()
      self.next()
    pygame.quit()

  def next (self):
    self.postUpdate()
    self.draw()
    pygame.display.update()
    self.clock.tick(30)
    self.preUpdate()
    if self.exiting:
        print("exiting")
        self.stop()

  def stop (self):
    pygame.quit()
    quit(0)
      
  def message(self, msg):
    #print(msg)
    pass