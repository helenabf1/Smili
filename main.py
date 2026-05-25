import pygame
from config import LARGURA, ALTURA, FPS, TELA_INICIO, TELA_INSTRUCOES, TELA_JOGO, SAIR
from assets import carregar_assets
from telas import tela_inicio, tela_instrucoes, tela_jogo

pygame.init()
pygame.mixer.init()

window = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Smili, o rato')

assets = carregar_assets()
estado = TELA_INICIO

while estado != SAIR:
    if   estado == TELA_INICIO:      estado = tela_inicio(window, assets)
    elif estado == TELA_INSTRUCOES:  estado = tela_instrucoes(window, assets)
    elif estado == TELA_JOGO:        estado = tela_jogo(window, assets)
    else: estado = SAIR

pygame.quit()