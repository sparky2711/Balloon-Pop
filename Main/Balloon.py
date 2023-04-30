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

# Set FPS and Clock
fps = 60
clock = pygame.time.Clock()

# Set Webcam Dimensions
cap = cv2.VideoCapture(0)
cap.set(3, width)
cap.set(4, height)

# Load Balloon Image
imgBalloon = pygame.image.load('../Resources/BalloonRed.png').convert_alpha()
imgBackground = pygame.image.load('../Resources/Project - GUI/background.png').convert()
rectBalloon = imgBalloon.get_rect()
rectBalloon.x, rectBalloon.y = 500, 300

# Initialize Variables
speed = 11
score = 0
name = ""

# Initialize Hand Detector
detector = HandDetector(detectionCon=0.8, maxHands=1)

# Function to Reset Balloon Position
def resetBalloon():
    rectBalloon.x = random.randint(100, img.shape[1] - 100)
    rectBalloon.y = img.shape[0] + 50

# Show Start Page
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
        rectBalloon.y -= speed
        # check if ballon has reached top without pop
        if rectBalloon.y <0:
            resetBalloon()
            speed += 0.5

        if hands:
            hand = hands[0]
            x, y, z = hand['lmList'][8]
            if rectBalloon.collidepoint(x, y):
                resetBalloon()
                score += 10
                speed += 1
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        imgRGB = np.rot90(imgRGB)
        frame = pygame.surfarray.make_surface(imgRGB).convert()
        frame = pygame.transform.flip(frame, True, False)
        window.blit(frame, (0, 0))
        window.blit(imgBalloon, rectBalloon)

        font = pygame.font.Font('../Resources/Marcellus-Regular.ttf', 50)
        textScore = font.render(f'Score: {score}', True, (50, 50, 255))
        textTime = font.render(f'Time: {timeRemain}', True, (50, 50, 255))
        window.blit(textScore, (35, 35))
        window.blit(textTime, (1000, 35))

    # Update Display
    pygame.display.update()
    # Set FPS
    clock.tick(fps)
