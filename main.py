import pygame
from config import LARGURA, ALTURA, FPS, TELA_INICIO, TELA_JOGO, SAIR
from assets import carregar_assets
from telas import tela_inicio

pygame.init()
pygame.mixer.init()

window = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Smili, o rato')

assets = carregar_assets()
estado = TELA_INICIO

while estado != SAIR:
    if estado == TELA_INICIO:
        estado = tela_inicio(window, assets)
    else:
        estado = SAIR


pygame.quit()