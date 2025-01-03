# // librairie ici pygame = py pour gagner du temps//
import pygame as py
from pygame.locals import * 
import sys
import os, os.path
import pickle
from maps.attributs import GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT

# // les init de pygame //
py.init()

# // Set up de l'écran //
ecran = py.display.set_mode(size=(GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT), flags=FULLSCREEN|SCALED)
color = (255,255,255)
ecran.fill(color)


# // Set up du framerate //
FPS = 60
fpsClock = py.time.Clock()

SAVE_FOLDER = "sauvegardes/"
NUM_SAVE_SLOTS = 5
FONT = py.font.Font(size=32)

# // imports divers //
from inputs import verifierInputKey, mouse1

# // Toutes les classes sont si dessous // 
from Joueur import Joueur, get_joueur_position_cell
from Environement import *
from Transition import Transition

def main():
    # // Espace dédié au diverses variables liée au fonctionnement du code //
    continuer = True

    id, location, joueur = mainMenu()
    mapjeu = Map(0, 0, location["destination"])

    # // ajout des sprites dans le jeu //

    transitionEcran = Transition(GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT, end=0.3, transitionType="fade", playType="ping-pong")
    transitionZone = Transition(GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT, end=0.5, transitionType="circle", playType="ping-pong")
    dernierePositionJoueur = joueur.rect.topleft

    zoom = 1
    
    # // la boucle pour les evenements et autres //
    while continuer: 

        # // Les évenement (input joueur) sont ici //
        keys_pressed_once = []
        for event in py.event.get():
            if event.type == py.QUIT:
                saveGame(id, location, joueur, ecran)
                py.quit()
                sys.exit()
            elif event.type == py.KEYDOWN:
                keys_pressed_once.append(event.key)
                if verifierInputKey(event.key, "quit"):
                    saveGame(id, location, joueur, ecran)
                    py.quit()
                    sys.exit()
                elif verifierInputKey(event.key, "zoom"):
                    zoom += 0.2
                elif verifierInputKey(event.key, "dezoom"):
                    zoom -= 0.2
                # un zoom négatif casse tout
                zoom = py.math.clamp(zoom, 0.1, 1)
            elif event.type == py.MOUSEBUTTONDOWN:
                if event.button == 1:
                    keys_pressed_once.append(mouse1)
        

        # // mise a niveaux des objets du monde (joueur, pnj, ...)
        dt = fpsClock.get_time() / 1000
        #print(fpsClock.get_fps())
        if not transitionEcran.playing and not transitionZone.playing:
            joueurCellStart = get_joueur_position_cell(joueur.rect.center)
            positionJoueurStart = joueur.rect.center
            zoom, new_location = joueur.update(dt, keys_pressed_once, mapjeu, zoom)
            if new_location != -1:
                location = new_location
                transitionZone.play()
                dernierePositionJoueur = positionJoueurStart
            if joueurCellStart != get_joueur_position_cell(joueur.rect.center):
                transitionEcran.play()
                dernierePositionJoueur = positionJoueurStart
        transitionEcran.update(dt)
        fini = transitionZone.update(dt)
        if fini and transitionZone.playing:
            mapjeu = Map(0, 0, location["destination"])
            joueur.rect.center = location["position"]
            mapjeu.removeItems(joueur.collectedItems)
        joueurCenter = joueur.rect.center
        if (transitionEcran.playing and not transitionEcran.reverse) or (transitionZone.playing and not transitionZone.reverse):
            joueurCenter = dernierePositionJoueur
        # // Affichage //
        ecran.fill(color)

        for layer in range(NUM_LAYERS - NUM_LAYERS_ABOVE_PLAYER):
            mapjeu.draw(dt, ecran, joueurCenter, zoom, layer)
        joueur.draw(ecran, zoom, joueurCenter)
        for layer in range(NUM_LAYERS - NUM_LAYERS_ABOVE_PLAYER, NUM_LAYERS):
            mapjeu.draw(dt, ecran, joueurCenter, zoom, layer)
        joueur.drawHUD(ecran)

        transitionEcran.draw(ecran)
        transitionZone.draw(ecran)

        py.display.update()

        fpsClock.tick(FPS)

# // fonction diverses //

def mainMenu():
    deleteImageSize = (75, 75)
    deleteImage = py.transform.scale(py.image.load("images/Shuriken.png"), deleteImageSize)
    deleting = -1
    deleteText = ""
    deleteButtons = [py.Rect((260, i * 150 + 50), deleteImageSize) if os.path.isfile(SAVE_FOLDER + "save" + str(i) + ".txt") else False for i in range(NUM_SAVE_SLOTS)]

    saveSlots = [{"rect": py.Rect(50, i * 150 + 25, 200, 125), "image": False if not os.path.isfile(SAVE_FOLDER + "save" + str(i) + ".png") else py.image.load(SAVE_FOLDER + "save" + str(i) + ".png")} for i in range(NUM_SAVE_SLOTS)]
    running = True
    hovered = 0
    while running:
        mouse_x, mouse_y = py.mouse.get_pos()
        for i, button in enumerate(saveSlots):
            if button["rect"].collidepoint((mouse_x, mouse_y)):
                hovered = i
        for event in py.event.get():
            if event.type == py.KEYDOWN:
                if event.key == py.K_ESCAPE:
                    py.quit()
                    sys.exit()
                elif event.key != pygame.K_RETURN and deleting != -1:
                    if event.key == pygame.K_BACKSPACE:
                        deleteText = deleteText[:-1]
                    else:
                        deleteText += event.unicode
                elif event.key == pygame.K_RETURN and deleting != -1:
                    if deleteText.lower() == "oui":
                        deleteButtons[deleting] = False
                        saveSlots[deleting]["image"] = False
                        fileName = SAVE_FOLDER + "save" + str(deleting)
                        os.remove(fileName + ".txt")
                        os.remove(fileName + ".png")
                    deleting = -1
                    deleteText = ""
            elif event.type == py.QUIT:
                py.quit()
                sys.exit()
            elif event.type == py.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i, button in enumerate(saveSlots):
                        if button["rect"].collidepoint((mouse_x, mouse_y)):
                            return loadSave(i)
                    for i, button in enumerate(deleteButtons):
                        if button and button.collidepoint((mouse_x, mouse_y)):
                            deleting = i
        
        ecran.fill(color)

        for i, button in enumerate(saveSlots):
            rectColor = (100, 200, 0) if i != hovered else (0, 100, 200)
            py.draw.rect(ecran, rectColor, button["rect"], 10)
            text_img = FONT.render("sauvegarde: " + str(i), True, (0, 100, 100))
            ecran.blit(text_img, (button["rect"].topleft[0] + 20, button["rect"].topleft[1] + 50))
            if i == hovered and button["image"]:
                ecran.blit(button["image"], (GAME_SCREEN_WIDTH - 825, 50))
        
        for button in deleteButtons:
            if button:
                ecran.blit(deleteImage, button.topleft)

        if deleting != -1:
            py.draw.rect(ecran, (200, 200, 200), (40, 40, GAME_SCREEN_WIDTH / 1.5, GAME_SCREEN_HEIGHT / 1.5))
            text_img = FONT.render("confirmez que vous voulez supprimer la sauvegarde: " + str(deleting) + " (oui/non)", True, (0, 100, 100))
            ecran.blit(text_img, (60, 60))
            text_img = FONT.render(deleteText, True, (0, 100, 100))
            ecran.blit(text_img, (75, 120))

        pygame.display.update()

        fpsClock.tick(FPS)

def loadSave(id=0):
    fileName = SAVE_FOLDER + "save" + str(id) + ".txt"
    if os.path.isfile(fileName):
        with open(fileName, "rb") as f:
            save = pickle.load(f)
        return id, save["location"], Joueur(save["position"][0], save["position"][1], save["items"], save["collectedItems"], save["events"])
    else:
        return id, {"destination": "overworld", "position": (100, 125)}, Joueur(100, 125, {}, {})

def saveGame(id, location, joueur: Joueur, preview: py.Surface):
    fileName = SAVE_FOLDER + "save" + str(id)
    py.image.save(py.transform.scale(preview, (800, 448)), fileName + ".png")
    with open(fileName + ".txt", "wb") as f:
        pickle.dump({"location": location, "items": joueur.items, "collectedItems": joueur.collectedItems, "position": joueur.rect.center, "events": joueur.evenements}, f)

if __name__ == "__main__":
    main()

