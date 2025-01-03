import pygame as py
import math
import pickle
import os
from copy import deepcopy

from maps.attributs import *
from Joueur import get_joueur_position_cell
from PNJs.dialogues import dialogues


class Wall(py.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        """ self.image = py.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((0, 0, 0, 0)) """
        self.rect = py.Rect(x, y, TILE_SIZE, TILE_SIZE)
    
class Porte(py.sprite.Sprite):
    def __init__(self, x, y, destination, position):
        super().__init__()
        """ self.image = py.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((0, 0, 0, 0)) """
        self.rect = py.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.destination = destination
        self.position = position

class ObjetDialogue(py.sprite.Sprite):
    def __init__(self, x, y, dialogue: dict, name="", face=""):
        super().__init__()
        self.rect = py.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.name = name or dialogue
        self.face = face or "vide.png"
        self.face = pygame.transform.scale(pygame.image.load("PNJs/faces/" + self.face), (WIDTH_FACE, HEIGHT_FACE))
        self.dialogue = deepcopy(dialogues[dialogue])
        self.dialogueKey = dialogue
        self.radius = TILE_SIZE * 2

class Item(py.sprite.Sprite):
    def __init__(self, x, y, name, layerIdx, mapName):
        super().__init__()
        self.rect = py.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.name = name
        self.layerIdx = layerIdx
        self.mapName = mapName

class Tile(py.sprite.Sprite):
    def __init__(self, x, y, image, animated="", time=0.0, *groups):
        super().__init__(*groups)
        self.rect = py.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.image = image
        self.animated = animated
        if self.animated != "":
            self.time = time
    
    def update(self, dt, images):
        if self.animated == "": return
        self.time += dt * animations[self.animated]["speed"]
        if self.time > 1.0:
            self.time = 0.0
        self.image = images[animations[self.animated]["tiles"][min(len(animations[self.animated]["tiles"]) - 1, floor(pygame.math.lerp(0, len(animations[self.animated]["tiles"]), self.time)))]]

class Map(py.sprite.Sprite):
    def __init__(self, x: int, y: int, path: str):
        super().__init__()
        self.images = setup_images("maps/" + FOLDER_PATH, "maps/" + TILE_MAP_FOLDER_NAME)
        self.rect = py.Rect(x, y, MapSize.width, MapSize.height)
        self.mapName = path
        self.tile_map_attributs = self.load_map("maps/" + path + "/" + TILE_MAP_FILE_NAME)
        self.tile_map = self.load_map("maps/" + path + "/" + TILE_MAP_RELOADABLE_FILE_NAME)
        self.create_groups()
        self.apply_attributs()
    
    def load_map(self, file_name):
        if os.path.isfile(file_name):
            with open(file_name, "rb") as f:
                return pickle.load(f)
        else:
            print("Pas de fichier map de nom: " + file_name)
            raise FileNotFoundError
    
    def create_groups(self):
        self.tile_groups = []
        for i, layer in enumerate(self.tile_map):
            self.tile_groups.append([])
            for y, row in enumerate(layer):
                if y % math.floor(GAME_SCREEN_HEIGHT / TILE_SIZE) == 0:
                    self.tile_groups[i].append([])
                for x, tile in enumerate(row):
                    if x % math.floor(GAME_SCREEN_WIDTH / TILE_SIZE) == 0 and y % math.floor(GAME_SCREEN_HEIGHT / TILE_SIZE) == 0:
                        self.tile_groups[i][-1].append(extendedGroup())
                    if tile["nom"] != VIDE:
                        animated = ""
                        time = 0.0
                        if tile["nom"] in animations:
                            animated = tile["nom"]
                            time = tile["special"]["time"]
                        Tile(x * TILE_SIZE, y * TILE_SIZE, self.images[tile["nom"]], animated, time, self.tile_groups[i][-1][math.floor(x / (GAME_SCREEN_WIDTH / TILE_SIZE))])
    
    def apply_attributs(self):
        self.collisions = extendedGroup()
        self.portes = extendedGroup()
        self.objetsDialogue = extendedGroup()
        self.items = extendedGroup()
        for layerIdx, layer in enumerate(self.tile_map_attributs):
            for y, row in enumerate(layer):
                for x, tile in enumerate(row):
                    tile_attributs = tile["attributs"]
                    tile_special = tile["special"]
                    if MUR in tile_attributs:
                        if not ("collision" in tile_special and tile_special["collision"] == "0"):
                            wall = Wall(x * TILE_SIZE + self.rect.left, y * TILE_SIZE + self.rect.top)
                            wall.add(self.collisions)
                    if "destination" in tile_special:
                        pos = (25, 50)
                        if "position" in tile_special:
                            sep = tile_special["position"].find(";")
                            pos = (int(tile_special["position"][:sep]), int(tile_special["position"][sep + 1:]))
                        porte = Porte(x * TILE_SIZE + self.rect.left, y * TILE_SIZE + self.rect.top, tile_special["destination"], pos)
                        porte.add(self.portes)
                    if "dialogue" in tile_special:
                        name = ""
                        if "nom" in tile_special:
                            name = tile_special["nom"]
                        face = ""
                        if "face" in tile_special:
                            face = tile_special["face"]
                        obj = ObjetDialogue(x * TILE_SIZE + self.rect.left, y * TILE_SIZE + self.rect.top, tile_special["dialogue"], name, face)
                        obj.add(self.objetsDialogue)
                    if "item" in tile_special:
                        item = Item(x * TILE_SIZE + self.rect.left, y * TILE_SIZE + self.rect.top, tile_special["item"], layerIdx, self.mapName)
                        item.add(self.items)
    
    def draw(self, dt, surface: py.Surface, positionJoueurGlobal, p_zoom, layer):
        layer_groups = self.tile_groups[layer]
        zoom = round(p_zoom, 2)
        topleft = self.rect.topleft
        positionJoueur = get_joueur_position_cell(positionJoueurGlobal)
        if zoom == 1:
            relative_pos = (topleft[0] + positionJoueur[0], topleft[1] + positionJoueur[1])
            group_pos = (math.floor(relative_pos[0] / GAME_SCREEN_WIDTH), math.floor(relative_pos[1] / GAME_SCREEN_HEIGHT))
            if 0 <= group_pos[1] < len(layer_groups):
                if 0 <= group_pos[0] < len(layer_groups[group_pos[1]]):
                    layer_groups[group_pos[1]][group_pos[0]].draw(surface, positionJoueurGlobal, zoom)
                    layer_groups[group_pos[1]][group_pos[0]].update(dt, self.images)
        else:
            relative_pos = (topleft[0] + positionJoueur[0], topleft[1] + positionJoueur[1])
            for y in range(max(0, math.floor(relative_pos[1] - GAME_SCREEN_HEIGHT / zoom)), math.floor(min(len(layer_groups) * GAME_SCREEN_HEIGHT, relative_pos[1] + GAME_SCREEN_HEIGHT / zoom)), GAME_SCREEN_HEIGHT):
                for x in range(max(0, math.floor(relative_pos[0] - GAME_SCREEN_WIDTH / zoom)), math.floor(min(len(layer_groups[math.floor(y / GAME_SCREEN_HEIGHT)]) * GAME_SCREEN_WIDTH, relative_pos[0] + GAME_SCREEN_WIDTH / zoom)), GAME_SCREEN_WIDTH):
                    group_pos = (math.floor(x / GAME_SCREEN_WIDTH), math.floor(y / GAME_SCREEN_HEIGHT))
                    layer_groups[group_pos[1]][group_pos[0]].draw(surface, positionJoueurGlobal, zoom)
                    layer_groups[group_pos[1]][group_pos[0]].update(dt, self.images)
    
    def removeTile(self, layer, coords):
        group_pos = (py.math.clamp(math.floor(coords[0] / GAME_SCREEN_WIDTH), 0, MapSize.getWidth()), py.math.clamp(math.floor(coords[1] / GAME_SCREEN_HEIGHT), 0,  MapSize.getHeight()))
        for sprite in self.tile_groups[layer][group_pos[1]][group_pos[0]].sprites():
            if sprite.rect.topleft == coords:
                sprite.kill()
                break
    
    def addItem(self, layerIdx, coords, name, imageName, animated=""):
        self.items.add(Item(coords[0], coords[1], name, layerIdx, self.mapName))
        group_pos = (py.math.clamp(math.floor(coords[0] / GAME_SCREEN_WIDTH), 0, MapSize.getWidth()), py.math.clamp(math.floor(coords[1] / GAME_SCREEN_HEIGHT), 0,  MapSize.getHeight()))
        self.tile_groups[layerIdx][group_pos[1]][group_pos[0]].add(Tile(coords[0], coords[1], self.images[imageName], animated))

    def removeItems(self, items: dict):
        for k in items.keys():
            for item in items[k]:
                if item.mapName == self.mapName:
                    self.removeTile(item.layerIdx, item.rect.topleft)
                    self.items.removeSprite(item)

# classe qui hérite de py.sprite.Group qui est la classe qui permet l'affichage et l'update d'un groupe de sprites
class extendedGroup(py.sprite.Group):
    # draw est une méthode de py.sprite.Group que je remplace par la mienne
    # elle prend comme argument self, la surface sur laquelle afficher, la position du joueur pour pouvoir décaler les sprites et le zoom a appliquer aux sprites
    def draw(self, surface: py.Surface, positionJoueurGlobal, p_zoom):
        # self.sprites est la liste qui contient tout les sprites de ce groupe
        sprites = self.sprites()
        # surface_blit est une réference a la fonction d'affichage, ce qui veut dire que surface_blit() est l'équivalent de surface.blit()
        surface_blit = surface.blit
        # je round le zoom pour éviter les erreurs de précision
        zoom = round(p_zoom, 2)
        # je fait ce teste pour ne pas devoir scaler si il n'y en a pas besoin
        positionJoueur = get_joueur_position_cell(positionJoueurGlobal)
        if zoom == 1:
            for spr in sprites:
                # spr est une instance d'une classe qui hérite de py.sprite.Sprite qui appartient a ce groupe
                topleft = spr.rect.topleft
                # pos contient la où doit ètre affiché l'objet en prenant le joueur comme centre
                pos = (math.floor(topleft[0] - positionJoueur[0]), math.floor(topleft[1] - positionJoueur[1]))
                # verifier si le sprite est sur l'écran
                self.spritedict[spr] = surface_blit(spr.image, pos)
        else:
            for spr in sprites:
                topleft = spr.rect.topleft
                # TODO: if this doesn't work, it's cause of scaling and GAME_SCREEN_WIDTH, change it!!!
                pos = (math.floor((topleft[0] - positionJoueur[0]) * zoom + GAME_SCREEN_WIDTH / 2 - GAME_SCREEN_WIDTH / 2 * zoom), math.floor((topleft[1] - positionJoueur[1]) * zoom + GAME_SCREEN_HEIGHT / 2 - GAME_SCREEN_HEIGHT / 2 * zoom))
                self.spritedict[spr] = surface_blit(py.transform.scale(spr.image, (math.ceil(spr.rect.width * zoom), math.ceil(spr.rect.height * zoom))), pos)
        self.lostsprites = []
    
    def removeSprite(self, spr):
        for sprite in self.sprites():
            if sprite.rect == spr.rect:
                self.remove(sprite)
                return
    
    def __str__(self) -> str:
        s = ""
        sprites = self.sprites()
        for spr in sprites:
            s += str(spr.rect.center) + "; "
        return s