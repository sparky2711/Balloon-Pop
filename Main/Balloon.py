import random
import time
import pygame
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector

# Initialize Pygame
pygame.init()

# Set Window Dimensions
width, height = 1280, 720
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Balloon Pop")

# Set Webcam Dimensions
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Load Balloon Image
preferredHeight = 150
preferredWidth = 115
heightToWidth =  preferredHeight / preferredWidth

class Balloon:
    def __init__(self, property, rawImage, height, width, points, defaultSpeed):
        self.property = property
        self.height = height
        self.width = width
        self.rawImage = rawImage
        self.image = pygame.transform.scale(rawImage, (width, height))
        self.rect = self.image.get_rect()
        self.points = points
        self.rect.x = 500
        self.rect.y = 300
        self.speed = defaultSpeed

    def randomizeLocation(self, background):
        self.rect.x = random.randint(100, background.shape[1] - 100)
        self.rect.y = background.shape[0] + 50

redBalloon = Balloon('red', pygame.image.load('../Resources/BalloonRed.png').convert_alpha(), 150, 115, 10, 11)
goldBalloon = Balloon('gold', pygame.image.load('../Resources/BalloonGold.png').convert_alpha(), 160, 60, 20, 14)
pinkBalloon = Balloon('pink', pygame.image.load('../Resources/BalloonPink.png').convert_alpha(), 175, 80, 5, 8)
starBalloon = Balloon('star', pygame.image.load('../Resources/BalloonStar.png').convert_alpha(), 50, 50, 50, 20)

balloonList = [redBalloon, goldBalloon, pinkBalloon, starBalloon]

def randomBalloon(balloonList):
    length = len(balloonList)
    randomIndex = random.randint(0, length - 1)

    # Reduce the occurence of star balloon
    if balloonList[randomIndex].property == 'star':
        secondSpin = random.randint(0, length - 1)
        return balloonList[secondSpin]

    return balloonList[randomIndex]

# Initialize Variables
streamSpeed = 1
score = 0
name = ""

# Initialize Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Balloon pop sound
popSound = pygame.mixer.Sound('../Resources/pop.wav')

# Show Start Page
imgBackground = pygame.image.load('../Resources/Project - GUI/background.png').convert()
showStartPage = True
while showStartPage:
    # Get Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Draw Start Page
    window.fill((255, 255, 255))
    font = pygame.font.Font('../Resources/Marcellus-Regular.ttf', 50)
    text = font.render("Enter Your Name:", True, (50, 50, 255))
    textRect = text.get_rect()
    textRect.center = (width // 2, height // 2 - 50)
    window.blit(imgBackground, (0, 0))
    window.blit(text, textRect)

    # Get User Input
    userInput = pygame.Rect(width // 2 - 150, height // 2 + 25, 300, 50)
    pygame.draw.rect(window, (50, 50, 255), userInput, 2)
    font = pygame.font.Font('../Resources/Marcellus-Regular.ttf', 32)
    inputText = font.render(name, True, (50, 50, 255))
    window.blit(inputText, (userInput.x + 5, userInput.y + 5))
    pygame.display.update()

    # Check for User Input
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.unicode.isalpha():
                name += event.unicode
            elif event.key == pygame.K_BACKSPACE:
                name = name[:-1]
            elif event.key == pygame.K_RETURN:
                showStartPage = False

startTime = time.time()
totalTime = 60
fps = 120
clock = pygame.time.Clock()

# Choose random Balloon
balloon = randomBalloon(balloonList)

# Main Game Loop
while True:
    # Get Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    # Apply Logic
    timeRemain = int(totalTime - (time.time() - startTime))
    if timeRemain < 0:
        # Show Final Score
        window.fill((255, 255, 255))
        font = pygame.font.Font('../Resources/Marcellus-Regular.ttf', 50)
        extScore = font.render(f'Name : {name} ', True, (50, 50, 255))
        textScore = font.render(f' Your Score: {score}', True, (50, 50, 255))
        textTime = font.render(f'Time Up', True, (50, 50, 255))
        window.blit(textScore, (450, 350))
        window.blit(extScore, (450, 275))
        window.blit(textTime, (530, 200))
    else:
        #OPENCV
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)
        balloon.rect.y -= balloon.speed + streamSpeed
        # check if ballon has reached top without pop
        if balloon.rect.y <0:
            balloon = randomBalloon(balloonList)
            balloon.randomizeLocation(img)
            streamSpeed += 0.5

        if hands:
            hand = hands[0]
            x, y, z = hand['lmList'][8]
            if balloon.rect.collidepoint(x, y):
                score += balloon.points
                popSound.play()
                streamSpeed += 1
                balloon = randomBalloon(balloonList)
                balloon.randomizeLocation(img)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgRGB = np.rot90(imgRGB)
        frame = pygame.surfarray.make_surface(imgRGB).convert()
        frame = pygame.transform.flip(frame, True, False)
        window.blit(frame, (0, 0))
        window.blit(balloon.image, balloon.rect)

        font = pygame.font.Font('../Resources/Marcellus-Regular.ttf', 50)
        textScore = font.render(f'Score: {score}', True, (50, 50, 255))
        textTime = font.render(f'Time: {timeRemain}', True, (50, 50, 255))
        window.blit(textScore, (35, 35))
        window.blit(textTime, (1000, 35))

    # Update Display
    pygame.display.update()
    # Set FPS
    clock.tick(fps)
