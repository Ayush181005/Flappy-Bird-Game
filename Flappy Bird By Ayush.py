import pygame # pip install pygame
from pygame.locals import *
import sys
from random import randint

# Global constants and variables
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 700
FPS = 30 # min: 16
GAME_IMAGES = {}
GAME_SOUNDS = {}

EASINESS = 3 # max 3
if EASINESS > 3:
    EASINESS = 3

# Functions
def welcomeScreen():
    while True:
        # Blitting images (Sequence is important)
        screen.blit(GAME_IMAGES["background"], (0, 0))
        screen.blit(GAME_IMAGES["base"], (baseX, baseY))
        screen.blit(GAME_IMAGES["player"], (playerX, playerY))
        screen.blit(GAME_IMAGES["message"], (messageX, messageY))
        pygame.display.update() # only one frame(same screen), so no need of fps
        for event in pygame.event.get():
            if event.type == KEYDOWN and event.key == K_ESCAPE or event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and event.key == K_SPACE:
                return

def pause():
    loop = 1
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                loop = 0
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    loop = 0
                if event.key == pygame.K_SPACE:
                    screen.fill((0, 0, 0))
                    loop = 0
        pygame.display.update()
        pygame.time.Clock().tick(FPS)

def gameLoop():
    newPipe1 = getRandomPipes()
    newPipe2 = getRandomPipes()
    newPipe3 = getRandomPipes()

    upperPipes = [
        {'x':SCREEN_WIDTH, 'y':newPipe1[0]['y']},
        {'x':SCREEN_WIDTH*1.33, 'y':newPipe2[0]['y']},
        {'x':SCREEN_WIDTH*1.66, 'y':newPipe3[0]['y']}
    ]

    lowerPipes = [
        {'x':SCREEN_WIDTH, 'y':newPipe1[1]['y']},
        {'x':SCREEN_WIDTH*1.33, 'y':newPipe2[1]['y']},
        {'x':SCREEN_WIDTH*1.66, 'y':newPipe3[1]['y']}
    ]

    # Game Controls
    score = 0
    pipeSpeedX = -10
    playerSpeedY = -9 # Towards the ground
    playerFlyingSpeed = -8 # Towards up
    playerMaxSpeed = 10 # So that due to gravity, bird does not have too much velocity
    playerAccelerationY = 1 # Due to gravity on player's planet
    playerFlying = False
    playerHeight = GAME_IMAGES["player"].get_height()
    playerY = SCREEN_HEIGHT/2

    while True:
        paused = False
        for event in pygame.event.get():
            if event.type == KEYDOWN and (event.key == K_ESCAPE or event.type == QUIT):
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN and (event.key == K_SPACE or event.type == K_PAUSE):
                pause()

            if event.type == KEYDOWN and (event.key == K_w or event.key == K_UP):
                if playerY > 0:
                    playerSpeedY = playerFlyingSpeed
                    playerFlying = True
                    GAME_SOUNDS["fly"].play()

        # Moving player up
        playerY += playerSpeedY
        if playerFlying:
            playerFlying = False

        # Moving player Down
        if not playerFlying and playerSpeedY < playerMaxSpeed:
            playerSpeedY += playerAccelerationY

        # Moving the pipes
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            upperPipe["x"] += pipeSpeedX
            lowerPipe["x"] += pipeSpeedX

        # Adding New pipes
        newPipe = getRandomPipes()
        if 0 < upperPipes[0]["x"] <= abs(pipeSpeedX):
            upperPipes.append(newPipe[0])
            lowerPipes.append(newPipe[1])

        # Removing old pipes
        if upperPipes[0]["x"] < 0:
            upperPipes.pop(0)
            lowerPipes.pop(0)

        # Changing the Score
        playerCenterX = playerX + playerWidth/2
        for pipe in upperPipes:
            pipeCenterX = pipe["x"] + pipeWidth/2
            if pipeCenterX < playerCenterX < abs(pipeSpeedX)+pipeCenterX:
                score += 1
                GAME_SOUNDS["point"].play()

        # Player dies
        if isHit(playerX, playerY, lowerPipes, upperPipes):
            GAME_SOUNDS["die"].play()
            pygame.time.wait(2000)
            return score

        highScoreFile = open("highScore.txt", "r")
        highScore = highScoreFile.read()
        highScoreFile.close()
        if highScore == "":
            highScore = 0
        if score >= int(highScore):
            highScoreFile = open("highScore.txt", "w")
            highScoreFile.write(str(score))
            highScore = score
            highScoreFile.close()

        screen.blit(GAME_IMAGES["background"], (0, 0))
        for upperPipe, lowerPipe in zip(upperPipes, lowerPipes):
            screen.blit(GAME_IMAGES["pipe"][0], (upperPipe["x"], upperPipe["y"]))
            screen.blit(GAME_IMAGES["pipe"][1], (lowerPipe["x"], lowerPipe["y"]))
        highScoreX = 10 + GAME_IMAGES["highScoreText"].get_width()
        highScoreY = 10
        highScoreDigits = [int(x) for x in str(highScore)]
        for highScoreDigit in highScoreDigits:
            screen.blit(GAME_IMAGES["highScoreText"], (0, GAME_IMAGES["numbers"][0].get_height()/4))
            screen.blit(GAME_IMAGES["numbers"][highScoreDigit], (highScoreX, highScoreY))
            highScoreX += GAME_IMAGES["numbers"][0].get_width()
        scoreDigits = [int(x) for x in str(score)]
        scoreX = SCREEN_WIDTH - highScoreX
        scoreY = highScoreY
        for digit in scoreDigits:
            screen.blit(GAME_IMAGES["numbers"][digit], (scoreX, scoreY))
            scoreX += GAME_IMAGES["numbers"][0].get_width()
        screen.blit(GAME_IMAGES["base"], (baseX, baseY))
        screen.blit(GAME_IMAGES["player"], (playerX, playerY))
        pygame.display.update()
        pygame.time.Clock().tick(FPS)

def isHit(playerX, playerY, lowerPipes, upperPipes):
    # Hitting with the ceiling or base
    if playerY<0 or playerY+playerHeight>SCREEN_HEIGHT-GAME_IMAGES["base"].get_height():
        return True

    # Hitting upperPipes
    for upperPipe in upperPipes:
        if (playerY < upperPipe["y"] + pipeHeight) and (upperPipe["x"] - playerWidth < playerX < upperPipe["x"] + pipeWidth):
            return True

    # Hitting lowerPipes
    for lowerPipe in lowerPipes:
        if (playerY + playerWidth > lowerPipe["y"]) and (lowerPipe["x"] - playerWidth < playerX < lowerPipe["x"] + pipeWidth):
            return True

    return False

def getRandomPipes():
    pipeHeight = GAME_IMAGES["pipe"][0].get_height()
    pipeGap = GAME_IMAGES["player"].get_height()*EASINESS
    pipeX = SCREEN_WIDTH
    lowerPipeY = randint(pipeGap, baseY)
    upperPipeY = lowerPipeY - (pipeGap + pipeHeight)
    pipe = [
        {'x':pipeX, 'y':upperPipeY},
        {'x':pipeX, 'y':lowerPipeY}
    ]
    return pipe

# Initialize Screen
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), RESIZABLE)
pygame.display.set_caption('Flappy Bird')

# Loading game images
GAME_IMAGES["background"] = pygame.image.load("img/background.png").convert_alpha()
GAME_IMAGES["base"] = pygame.image.load("img/base.png").convert_alpha()
GAME_IMAGES["player"] = pygame.image.load("img/bird.png").convert_alpha()
GAME_IMAGES["message"] = pygame.image.load("img/message.png").convert_alpha()
GAME_IMAGES["highScoreText"] = pygame.image.load("img/highScoreText.png").convert_alpha()
GAME_IMAGES["pipe"] = [
    pygame.transform.rotate(pygame.image.load("img/pipe.png").convert_alpha(), 180),
    pygame.image.load("img/pipe.png").convert_alpha()
]
GAME_IMAGES["numbers"] = (
    pygame.image.load("img/0.png").convert_alpha(),
    pygame.image.load("img/1.png").convert_alpha(),
    pygame.image.load("img/2.png").convert_alpha(),
    pygame.image.load("img/3.png").convert_alpha(),
    pygame.image.load("img/4.png").convert_alpha(),
    pygame.image.load("img/5.png").convert_alpha(),
    pygame.image.load("img/6.png").convert_alpha(),
    pygame.image.load("img/7.png").convert_alpha(),
    pygame.image.load("img/8.png").convert_alpha(),
    pygame.image.load("img/9.png").convert_alpha()
)
# Loading Game Sounds
GAME_SOUNDS["fly"] = pygame.mixer.Sound("sound/fly.wav")
GAME_SOUNDS["die"] = pygame.mixer.Sound("sound/die.wav")
GAME_SOUNDS["point"] = pygame.mixer.Sound("sound/point.wav")

# image coordinates
baseX = 0
baseY = SCREEN_HEIGHT - GAME_IMAGES["base"].get_height()
playerX = SCREEN_WIDTH/5
playerY = SCREEN_HEIGHT/2
playerWidth = GAME_IMAGES["player"].get_width()
playerHeight = GAME_IMAGES["player"].get_height()
messageX = (SCREEN_WIDTH-GAME_IMAGES["message"].get_width())/2
messageY = (SCREEN_HEIGHT-GAME_IMAGES["message"].get_height())/2
pipeHeight = GAME_IMAGES["pipe"][0].get_height()
pipeWidth = GAME_IMAGES["pipe"][0].get_width()

while True:
    welcomeScreen()
    gameLoop()