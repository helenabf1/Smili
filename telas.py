"""telas.py — tela inicial básica."""
import pygame
from config import (LARGURA, ALTURA, FPS,
                    TELA_INICIO, TELA_JOGO, SAIR,
                    PRETO, BRANCO, CINZA, CINZA_ESCURO, AMARELO)

def _txt_c(surf, texto, fnt, cor, y, sombra=True, off=2):
    r = fnt.render(texto, False, cor)
    x = (LARGURA - r.get_width()) // 2
    if sombra:
        surf.blit(fnt.render(texto, False, PRETO), (x+off, y+off))
    surf.blit(r, (x, y))

def _fundo_menu(surf):
    surf.fill(CINZA_ESCURO)
    for x in range(0, LARGURA, 20):
        pygame.draw.line(surf, (34,28,22), (x,0),(x,ALTURA))
    for y in range(0, ALTURA, 20):
        pygame.draw.line(surf, (34,28,22), (0,y),(LARGURA,y))

def tela_inicio(window, assets):
    clock = pygame.time.Clock()
    t=0; pisca=True

    while True:
        clock.tick(FPS); t+=1
        if t >= FPS//2: pisca = not pisca; t = 0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:          return SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:   return SAIR
                else:                           return TELA_JOGO

        _fundo_menu(window)
        _txt_c(window, 'SMILI, O RATO', assets['fnt_title'], AMARELO, 180)
        if pisca:
            _txt_c(window, 'Pressione qualquer tecla', assets['fnt_xs'], BRANCO, 316)
            _txt_c(window, 'para jogar!',              assets['fnt_xs'], BRANCO, 332)
        _txt_c(window, 'ESC = Sair', assets['fnt_xs'], CINZA, ALTURA-48)
        pygame.display.flip()
