"""telas.py — renderização completa do mundo."""
import pygame
from config import (LARGURA, ALTURA, FPS, FAIXA_H, TAMANHO_RATO,
                    TELA_INICIO, TELA_INSTRUCOES, TELA_JOGO, SAIR,
                    PRETO, BRANCO, CINZA, CINZA_ESCURO,
                    AMARELO, VERDE_CLARO, LARANJA, VERMELHO)
from mundo import Mundo, tipo_faixa, tile_key


def _txt(surf, texto, fnt, cor, x, y, sombra=True, off=2):
    if sombra:
        surf.blit(fnt.render(texto, False, PRETO), (x + off, y + off))
    surf.blit(fnt.render(texto, False, cor), (x, y))


def _txt_c(surf, texto, fnt, cor, y, sombra=True, off=2):
    r = fnt.render(texto, False, cor)
    x = (LARGURA - r.get_width()) // 2
    if sombra:
        surf.blit(fnt.render(texto, False, PRETO), (x + off, y + off))
    surf.blit(r, (x, y))


def _fundo_menu(surf):
    surf.fill(CINZA_ESCURO)
    for x in range(0, LARGURA, 20):
        pygame.draw.line(surf, (34, 28, 22), (x, 0), (x, ALTURA))
    for y in range(0, ALTURA, 20):
        pygame.draw.line(surf, (34, 28, 22), (0, y), (LARGURA, y))


def _sombra_oval(surf, x, y, w, h, alpha=65):
    s = pygame.Surface((w, h // 3 + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, alpha), (0, 0, w, h // 3 + 4))
    surf.blit(s, (x, y + h - h // 6))


def _painel(surf, x, y, w, h, cor_borda=None):
    p = pygame.Surface((w, h), pygame.SRCALPHA)
    p.fill((18, 14, 10, 215))
    if cor_borda:
        pygame.draw.rect(p, cor_borda + (200,), (0, 0, w, h), 3)
    surf.blit(p, (x, y))


def _desenhar_mundo(surf, mundo):
    a = mundo.assets
    cam = mundo.camera_y
    W2S = mundo.world_to_screen_y

    first = int(cam // FAIXA_H) - 1
    last = first + (ALTURA // FAIXA_H) + 3
    for fi in range(first, last + 1):
        world_top = fi * FAIXA_H
        sy = int(world_top - cam)
        if sy > ALTURA + FAIXA_H or sy < -FAIXA_H:
            continue
        tile = a[tile_key(tipo_faixa(fi))]
        surf.blit(tile, (0, sy))
        t = tipo_faixa(fi)
        bc = (38, 40, 46) if t == 'road' else (45, 12, 72) if t == 'sewer' else (80, 72, 60)
        pygame.draw.line(surf, bc, (0, sy), (LARGURA, sy), 1)

    for q in mundo.queijos:
        if q['coletado']:
            continue
        sy = W2S(q['wy'])
        if -40 < sy < ALTURA + 40:
            surf.blit(a['queijo'], (q['wx'], sy))

    for o in mundo.obst:
        sy = W2S(o['wy'])
        if -80 < sy < ALTURA + 80:
            _sombra_oval(surf, o['wx'], sy, o['w'], o['h'])
            surf.blit(o['img'], (o['wx'], sy))

    for p in mundo.plataformas:
        sy = W2S(p['wy'])
        if -80 < sy < ALTURA + 80:
            _sombra_oval(surf, p['wx'], sy, p['w'], p['h'], alpha=45)
            surf.blit(p['img'], (p['wx'], sy))

    for c in mundo.carros:
        sy = W2S(c['wy'])
        if -80 < sy < ALTURA + 80:
            _sombra_oval(surf, c['wx'], sy, c['w'], c['h'])
            surf.blit(c['img'], (c['wx'], sy))

    rsy = W2S(mundo.rato_wy)
    _sombra_oval(surf, mundo.rato_wx, rsy, TAMANHO_RATO, TAMANHO_RATO)
    surf.blit(a['rato'], (mundo.rato_wx, rsy))


def _hud(surf, a, pontos, nivel):
    hud = pygame.Surface((LARGURA, 30), pygame.SRCALPHA)
    hud.fill((12, 10, 8, 220))
    pygame.draw.line(hud, (200, 175, 30, 160), (0, 29), (LARGURA, 29), 1)
    surf.blit(hud, (0, 0))
    _txt(surf, f'PTS:{pontos:06d}', a['fnt_xs'], AMARELO, 6, 9)
    _txt(surf, f'NV:{nivel:02d}', a['fnt_xs'], LARANJA, LARGURA - 62, 9)


def tela_inicio(window, assets):
    clock = pygame.time.Clock()
    t = 0
    pisca = True

    while True:
        clock.tick(FPS)
        t += 1
        if t >= FPS // 2:
            pisca = not pisca
            t = 0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return SAIR
                elif ev.key == pygame.K_i:
                    return TELA_INSTRUCOES
                else:
                    return TELA_JOGO

        _fundo_menu(window)
        _txt_c(window, 'SMILI, O RATO', assets['fnt_title'], AMARELO, 180)
        if pisca:
            _txt_c(window, 'Pressione qualquer tecla', assets['fnt_xs'], BRANCO, 316)
            _txt_c(window, 'para jogar!', assets['fnt_xs'], BRANCO, 332)
        _txt_c(window, 'I = Instrucoes   ESC = Sair', assets['fnt_xs'], CINZA, ALTURA - 48)
        pygame.display.flip()


def tela_instrucoes(window, assets):
    clock = pygame.time.Clock()
    fnt   = assets['fnt_xs']
    fnt_t = assets['fnt_sm']
    PAD   = 28
    LH    = 18
    LH_BL = 10

    def wrap(texto, fonte, max_w):
        palavras = texto.split()
        linhas = []
        linha_atual = ''
        for p in palavras:
            teste = (linha_atual + ' ' + p).strip()
            if fonte.size(teste)[0] <= max_w:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = p
        if linha_atual:
            linhas.append(linha_atual)
        return linhas or ['']

    MAX_W = LARGURA - PAD * 2

    blocos = [
        ('p',  'Ajude o Smili a atravessar a cidade e coletar queijinhos!', BRANCO),
        ('br', '', None),
        ('h',  'CONTROLES:', AMARELO),
        ('br', '', None),
        ('p',  'Para mover o Smili, utilize as setas ou as teclas WASD', BRANCO),
        ('br', '', None),
        ('kb', 'P = Pausar o jogo',       VERDE_CLARO),
        ('br', '', None),
        ('kb', 'ESC = Menu',              VERDE_CLARO),
        ('br', '', None),
        ('kb', 'ENTER = Voltar ao menu',  VERDE_CLARO),
        ('br', '', None),
        ('br', '', None),
        ('h',  'PERIGOS:', AMARELO),
        ('br', '', None),
        ('p',  'Existem alguns obstaculos que devem ser evitados para a sobrevivencia do Smili.', BRANCO),
        ('br', '', None),
        ('p',  'Desvie dos veiculos passando na rua, utilize os canos e as tabuas de madeira para atravessar o esgoto.', BRANCO),
        ('br', '', None),
        ('p',  'Cuidado com as ratoeiras e para nao ser esmagado pela tela.', VERMELHO),
    ]

    linhas_render = []
    for tipo, txt, cor in blocos:
        if tipo == 'br':
            linhas_render.append((None, LH_BL))
        elif tipo == 'h':
            s = fnt_t.render(txt, True, cor)
            linhas_render.append((s, LH + 4))
        elif tipo == 'kb':
            s = fnt.render(txt, True, cor)
            linhas_render.append((s, LH))
        elif tipo == 'p':
            for l in wrap(txt, fnt, MAX_W):
                s = fnt.render(l, True, cor)
                linhas_render.append((s, LH))

    total_h = sum(h for _, h in linhas_render)
    TOPO    = 52
    AREA_H  = ALTURA - TOPO - 4
    scroll  = 0
    MAX_SCR = max(0, total_h - AREA_H)

    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    return TELA_INICIO
                if ev.key == pygame.K_DOWN:
                    scroll = min(scroll + LH * 3, MAX_SCR)
                if ev.key == pygame.K_UP:
                    scroll = max(scroll - LH * 3, 0)
            if ev.type == pygame.MOUSEWHEEL:
                scroll = max(0, min(scroll - ev.y * LH * 3, MAX_SCR))

        _fundo_menu(window)
        _txt_c(window, 'INSTRUCOES', fnt_t, AMARELO, 16)

        old_clip = window.get_clip()
        window.set_clip(pygame.Rect(0, TOPO, LARGURA, AREA_H))
        y = TOPO - scroll
        for surf2, h in linhas_render:
            if surf2 and y + h > TOPO and y < TOPO + AREA_H:
                window.blit(surf2, (PAD, y))
            y += h
        window.set_clip(old_clip)

        if MAX_SCR > 0:
            prop = scroll / MAX_SCR
            bh   = max(24, int(AREA_H * AREA_H / total_h))
            by   = TOPO + int((AREA_H - bh) * prop)
            pygame.draw.rect(window, (80, 80, 80), (LARGURA - 4, TOPO, 3, AREA_H))
            pygame.draw.rect(window, CINZA, (LARGURA - 4, by, 3, bh), border_radius=2)

        pygame.display.flip()


def tela_jogo(window, assets):
    clock = pygame.time.Clock()
    mundo = Mundo(assets)

    while True:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return TELA_INICIO
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    mundo.mover_rato(0, -1)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    mundo.mover_rato(0, +1)
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    mundo.mover_rato(-1, 0)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    mundo.mover_rato(+1, 0)

        mundo.atualizar()
        mundo.atualizar_camera()
        resultado, coletou = mundo.verificar_colisoes()

        if resultado != 'ok':
            return TELA_INICIO

        _desenhar_mundo(window, mundo)
        _hud(window, assets, mundo.pontos, mundo.nivel)
        pygame.display.flip()"""telas.py — renderização completa do mundo."""
import pygame
from config import (LARGURA, ALTURA, FPS, FAIXA_H, TAMANHO_RATO,
                    TELA_INICIO, TELA_INSTRUCOES, TELA_JOGO, SAIR,
                    PRETO, BRANCO, CINZA, CINZA_ESCURO,
                    AMARELO, VERDE_CLARO, LARANJA, VERMELHO)
from mundo import Mundo, tipo_faixa, tile_key


def _txt(surf, texto, fnt, cor, x, y, sombra=True, off=2):
    if sombra:
        surf.blit(fnt.render(texto, False, PRETO), (x + off, y + off))
    surf.blit(fnt.render(texto, False, cor), (x, y))


def _txt_c(surf, texto, fnt, cor, y, sombra=True, off=2):
    r = fnt.render(texto, False, cor)
    x = (LARGURA - r.get_width()) // 2
    if sombra:
        surf.blit(fnt.render(texto, False, PRETO), (x + off, y + off))
    surf.blit(r, (x, y))


def _fundo_menu(surf):
    surf.fill(CINZA_ESCURO)
    for x in range(0, LARGURA, 20):
        pygame.draw.line(surf, (34, 28, 22), (x, 0), (x, ALTURA))
    for y in range(0, ALTURA, 20):
        pygame.draw.line(surf, (34, 28, 22), (0, y), (LARGURA, y))


def _sombra_oval(surf, x, y, w, h, alpha=65):
    s = pygame.Surface((w, h // 3 + 4), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, alpha), (0, 0, w, h // 3 + 4))
    surf.blit(s, (x, y + h - h // 6))


def _painel(surf, x, y, w, h, cor_borda=None):
    p = pygame.Surface((w, h), pygame.SRCALPHA)
    p.fill((18, 14, 10, 215))
    if cor_borda:
        pygame.draw.rect(p, cor_borda + (200,), (0, 0, w, h), 3)
    surf.blit(p, (x, y))


def _desenhar_mundo(surf, mundo):
    a = mundo.assets
    cam = mundo.camera_y
    W2S = mundo.world_to_screen_y

    first = int(cam // FAIXA_H) - 1
    last = first + (ALTURA // FAIXA_H) + 3
    for fi in range(first, last + 1):
        world_top = fi * FAIXA_H
        sy = int(world_top - cam)
        if sy > ALTURA + FAIXA_H or sy < -FAIXA_H:
            continue
        tile = a[tile_key(tipo_faixa(fi))]
        surf.blit(tile, (0, sy))
        t = tipo_faixa(fi)
        bc = (38, 40, 46) if t == 'road' else (45, 12, 72) if t == 'sewer' else (80, 72, 60)
        pygame.draw.line(surf, bc, (0, sy), (LARGURA, sy), 1)

    for q in mundo.queijos:
        if q['coletado']:
            continue
        sy = W2S(q['wy'])
        if -40 < sy < ALTURA + 40:
            surf.blit(a['queijo'], (q['wx'], sy))

    for o in mundo.obst:
        sy = W2S(o['wy'])
        if -80 < sy < ALTURA + 80:
            _sombra_oval(surf, o['wx'], sy, o['w'], o['h'])
            surf.blit(o['img'], (o['wx'], sy))

    for p in mundo.plataformas:
        sy = W2S(p['wy'])
        if -80 < sy < ALTURA + 80:
            _sombra_oval(surf, p['wx'], sy, p['w'], p['h'], alpha=45)
            surf.blit(p['img'], (p['wx'], sy))

    for c in mundo.carros:
        sy = W2S(c['wy'])
        if -80 < sy < ALTURA + 80:
            _sombra_oval(surf, c['wx'], sy, c['w'], c['h'])
            surf.blit(c['img'], (c['wx'], sy))

    rsy = W2S(mundo.rato_wy)
    _sombra_oval(surf, mundo.rato_wx, rsy, TAMANHO_RATO, TAMANHO_RATO)
    surf.blit(a['rato'], (mundo.rato_wx, rsy))


def _hud(surf, a, pontos, nivel):
    hud = pygame.Surface((LARGURA, 30), pygame.SRCALPHA)
    hud.fill((12, 10, 8, 220))
    pygame.draw.line(hud, (200, 175, 30, 160), (0, 29), (LARGURA, 29), 1)
    surf.blit(hud, (0, 0))
    _txt(surf, f'PTS:{pontos:06d}', a['fnt_xs'], AMARELO, 6, 9)
    _txt(surf, f'NV:{nivel:02d}', a['fnt_xs'], LARANJA, LARGURA - 62, 9)


def tela_inicio(window, assets):
    clock = pygame.time.Clock()
    t = 0
    pisca = True

    while True:
        clock.tick(FPS)
        t += 1
        if t >= FPS // 2:
            pisca = not pisca
            t = 0

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return SAIR
                elif ev.key == pygame.K_i:
                    return TELA_INSTRUCOES
                else:
                    return TELA_JOGO

        _fundo_menu(window)
        _txt_c(window, 'SMILI, O RATO', assets['fnt_title'], AMARELO, 180)
        if pisca:
            _txt_c(window, 'Pressione qualquer tecla', assets['fnt_xs'], BRANCO, 316)
            _txt_c(window, 'para jogar!', assets['fnt_xs'], BRANCO, 332)
        _txt_c(window, 'I = Instrucoes   ESC = Sair', assets['fnt_xs'], CINZA, ALTURA - 48)
        pygame.display.flip()


def tela_instrucoes(window, assets):
    clock = pygame.time.Clock()
    fnt   = assets['fnt_xs']
    fnt_t = assets['fnt_sm']
    PAD   = 28
    LH    = 18
    LH_BL = 10

    def wrap(texto, fonte, max_w):
        palavras = texto.split()
        linhas = []
        linha_atual = ''
        for p in palavras:
            teste = (linha_atual + ' ' + p).strip()
            if fonte.size(teste)[0] <= max_w:
                linha_atual = teste
            else:
                if linha_atual:
                    linhas.append(linha_atual)
                linha_atual = p
        if linha_atual:
            linhas.append(linha_atual)
        return linhas or ['']

    MAX_W = LARGURA - PAD * 2

    blocos = [
        ('p',  'Ajude o Smili a atravessar a cidade e coletar queijinhos!', BRANCO),
        ('br', '', None),
        ('h',  'CONTROLES:', AMARELO),
        ('br', '', None),
        ('p',  'Para mover o Smili, utilize as setas ou as teclas WASD', BRANCO),
        ('br', '', None),
        ('kb', 'P = Pausar o jogo',       VERDE_CLARO),
        ('br', '', None),
        ('kb', 'ESC = Menu',              VERDE_CLARO),
        ('br', '', None),
        ('kb', 'ENTER = Voltar ao menu',  VERDE_CLARO),
        ('br', '', None),
        ('br', '', None),
        ('h',  'PERIGOS:', AMARELO),
        ('br', '', None),
        ('p',  'Existem alguns obstaculos que devem ser evitados para a sobrevivencia do Smili.', BRANCO),
        ('br', '', None),
        ('p',  'Desvie dos veiculos passando na rua, utilize os canos e as tabuas de madeira para atravessar o esgoto.', BRANCO),
        ('br', '', None),
        ('p',  'Cuidado com as ratoeiras e para nao ser esmagado pela tela.', VERMELHO),
    ]

    linhas_render = []
    for tipo, txt, cor in blocos:
        if tipo == 'br':
            linhas_render.append((None, LH_BL))
        elif tipo == 'h':
            s = fnt_t.render(txt, True, cor)
            linhas_render.append((s, LH + 4))
        elif tipo == 'kb':
            s = fnt.render(txt, True, cor)
            linhas_render.append((s, LH))
        elif tipo == 'p':
            for l in wrap(txt, fnt, MAX_W):
                s = fnt.render(l, True, cor)
                linhas_render.append((s, LH))

    total_h = sum(h for _, h in linhas_render)
    TOPO    = 52
    AREA_H  = ALTURA - TOPO - 4
    scroll  = 0
    MAX_SCR = max(0, total_h - AREA_H)

    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    return TELA_INICIO
                if ev.key == pygame.K_DOWN:
                    scroll = min(scroll + LH * 3, MAX_SCR)
                if ev.key == pygame.K_UP:
                    scroll = max(scroll - LH * 3, 0)
            if ev.type == pygame.MOUSEWHEEL:
                scroll = max(0, min(scroll - ev.y * LH * 3, MAX_SCR))

        _fundo_menu(window)
        _txt_c(window, 'INSTRUCOES', fnt_t, AMARELO, 16)

        old_clip = window.get_clip()
        window.set_clip(pygame.Rect(0, TOPO, LARGURA, AREA_H))
        y = TOPO - scroll
        for surf2, h in linhas_render:
            if surf2 and y + h > TOPO and y < TOPO + AREA_H:
                window.blit(surf2, (PAD, y))
            y += h
        window.set_clip(old_clip)

        if MAX_SCR > 0:
            prop = scroll / MAX_SCR
            bh   = max(24, int(AREA_H * AREA_H / total_h))
            by   = TOPO + int((AREA_H - bh) * prop)
            pygame.draw.rect(window, (80, 80, 80), (LARGURA - 4, TOPO, 3, AREA_H))
            pygame.draw.rect(window, CINZA, (LARGURA - 4, by, 3, bh), border_radius=2)

        pygame.display.flip()


def tela_jogo(window, assets):
    clock = pygame.time.Clock()
    mundo = Mundo(assets)

    while True:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    return TELA_INICIO
                elif ev.key in (pygame.K_UP, pygame.K_w):
                    mundo.mover_rato(0, -1)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):
                    mundo.mover_rato(0, +1)
                elif ev.key in (pygame.K_LEFT, pygame.K_a):
                    mundo.mover_rato(-1, 0)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d):
                    mundo.mover_rato(+1, 0)

        mundo.atualizar()
        mundo.atualizar_camera()
        resultado, coletou = mundo.verificar_colisoes()

        if resultado != 'ok':
            return TELA_INICIO

        _desenhar_mundo(window, mundo)
        _hud(window, assets, mundo.pontos, mundo.nivel)
        pygame.display.flip()