"""telas.py — renderização do mundo + HUD básico + tela inicial."""
import pygame
from config import (LARGURA, ALTURA, FPS, FAIXA_H, TAMANHO_RATO,
                    TELA_INICIO, TELA_JOGO, SAIR,
                    PRETO, BRANCO, CINZA, CINZA_ESCURO,
                    AMARELO, VERDE_CLARO, LARANJA)
from mundo import Mundo, tipo_faixa, tile_key

def _txt(surf, texto, fnt, cor, x, y, sombra=True, off=2):
    if sombra:
        surf.blit(fnt.render(texto, False, PRETO), (x+off, y+off))
    surf.blit(fnt.render(texto, False, cor), (x, y))

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

def _sombra_oval(surf, x, y, w, h, alpha=65):
    s = pygame.Surface((w, h//3+4), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0,0,0,alpha), (0,0,w, h//3+4))
    surf.blit(s, (x, y+h - h//6))

def _desenhar_mundo(surf, mundo):
    a   = mundo.assets
    cam = mundo.camera_y
    W2S = mundo.world_to_screen_y

    # 1. Tiles de fundo
    first = int(cam // FAIXA_H) - 1
    last  = first + (ALTURA // FAIXA_H) + 3
    for fi in range(first, last+1):
        world_top = fi * FAIXA_H
        sy = int(world_top - cam)
        if sy > ALTURA+FAIXA_H or sy < -FAIXA_H: continue
        tile = a[tile_key(tipo_faixa(fi))]
        surf.blit(tile, (0, sy))
        t  = tipo_faixa(fi)
        bc = (38,40,46) if t=='road' else (45,12,72) if t=='sewer' else (80,72,60)
        pygame.draw.line(surf, bc, (0,sy),(LARGURA,sy), 1)

    # 2. Carros com sombra
    for c in mundo.carros:
        sy = W2S(c['wy'])
        if -80 < sy < ALTURA+80:
            _sombra_oval(surf, c['wx'], sy, c['w'], c['h'])
            surf.blit(c['img'], (c['wx'], sy))

    # 3. Rato
    rsy = W2S(mundo.rato_wy)
    _sombra_oval(surf, mundo.rato_wx, rsy, TAMANHO_RATO, TAMANHO_RATO)
    surf.blit(a['rato'], (mundo.rato_wx, rsy))

def _hud(surf, a, pontos, nivel):
    hud = pygame.Surface((LARGURA, 30), pygame.SRCALPHA)
    hud.fill((12,10,8,220))
    pygame.draw.line(hud,(200,175,30,160),(0,29),(LARGURA,29),1)
    surf.blit(hud,(0,0))
    _txt(surf, f'PTS:{pontos:06d}', a['fnt_xs'], AMARELO,      6, 9)
    _txt(surf, f'NV:{nivel:02d}',   a['fnt_xs'], LARANJA, LARGURA-62, 9)

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

def tela_jogo(window, assets):
    clock  = pygame.time.Clock()
    mundo  = Mundo(assets)

    while True:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return TELA_INICIO
                elif ev.key in (pygame.K_UP,    pygame.K_w): mundo.mover_rato(0,-1)
                elif ev.key in (pygame.K_DOWN,  pygame.K_s): mundo.mover_rato(0,+1)
                elif ev.key in (pygame.K_LEFT,  pygame.K_a): mundo.mover_rato(-1,0)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d): mundo.mover_rato(+1,0)

        mundo.atualizar()
        mundo.atualizar_camera()

        resultado, coletou = mundo.verificar_colisoes()

        _desenhar_mundo(window, mundo)
        _hud(window, assets, mundo.pontos, mundo.nivel)
        pygame.display.flip()