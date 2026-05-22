import pygame
from config import LARGURA, ALTURA, FPS, TELA_INICIO, SAIR

pygame.init()
pygame.mixer.init()

window = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Smili, o rato')

estado = TELA_INICIO
clock  = pygame.time.Clock()


while estado != SAIR:
    clock.tick(FPS)
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            estado = SAIR
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_ESCAPE:
                estado = SAIR


pygame.quit()