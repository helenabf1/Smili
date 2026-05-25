import pygame
from config import (LARGURA, ALTURA, FPS, FAIXA_H, TAMANHO_RATO,
                    TELA_INICIO, TELA_INSTRUCOES, TELA_JOGO,
                    TELA_PAUSA, TELA_GAME_OVER, SAIR,
                    PRETO, BRANCO, CINZA, CINZA_ESCURO,
                    VERDE_CLARO, AMARELO, VERMELHO, LARANJA, MARROM_CLARO)
from assets import som, musica
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

def _painel(surf, x, y, w, h, cor_borda=None):
    p = pygame.Surface((w,h), pygame.SRCALPHA)
    p.fill((18,14,10,215))
    if cor_borda:
        pygame.draw.rect(p, cor_borda+(200,), (0,0,w,h), 3)
    surf.blit(p, (x,y))

def _desenhar_mundo(surf, mundo):
    a = mundo.assets
    cam = mundo.camera_y
    W2S = mundo.world_to_screen_y

    first = int(cam // FAIXA_H) - 1
    last  = first + (ALTURA // FAIXA_H) + 3
    for fi in range(first, last+1):
        world_top = fi * FAIXA_H
        sy = int(world_top - cam)
        if sy > ALTURA+FAIXA_H or sy < -FAIXA_H: continue
        tile = a[tile_key(tipo_faixa(fi))]
        surf.blit(tile, (0, sy))
        t = tipo_faixa(fi)
        bc = (38,40,46) if t=='road' else (45,12,72) if t=='sewer' else (80,72,60)
        pygame.draw.line(surf, bc, (0,sy),(LARGURA,sy), 1)

    for q in mundo.queijos:
        if q['coletado']: continue
        sy = W2S(q['wy'])
        if -40 < sy < ALTURA+40:
            surf.blit(a['queijo'], (q['wx'], sy))

    for o in mundo.obst:
        sy = W2S(o['wy'])
        if -80 < sy < ALTURA+80:
            _sombra_oval(surf, o['wx'], sy, o['w'], o['h'])
            surf.blit(o['img'], (o['wx'], sy))

    for p in mundo.plataformas:
        sy = W2S(p['wy'])
        if -80 < sy < ALTURA+80:
            _sombra_oval(surf, p['wx'], sy, p['w'], p['h'], alpha=45)
            surf.blit(p['img'], (p['wx'], sy))

    for c in mundo.carros:
        sy = W2S(c['wy'])
        if -80 < sy < ALTURA+80:
            _sombra_oval(surf, c['wx'], sy, c['w'], c['h'])
            surf.blit(c['img'], (c['wx'], sy))

    rsy = W2S(mundo.rato_wy)
    _sombra_oval(surf, mundo.rato_wx, rsy, TAMANHO_RATO, TAMANHO_RATO)
    surf.blit(a['rato'], (mundo.rato_wx, rsy))

def _hud(surf, a, pontos, recorde, nivel, vel_scroll=0.0):
    hud = pygame.Surface((LARGURA, 30), pygame.SRCALPHA)
    hud.fill((12,10,8,220))
    pygame.draw.line(hud,(200,175,30,160),(0,29),(LARGURA,29),1)
    surf.blit(hud,(0,0))
    _txt(surf, f'PTS:{pontos:06d}', a['fnt_xs'], AMARELO,       6,  9)
    _txt(surf, f'REC:{recorde:06d}',a['fnt_xs'], VERDE_CLARO, LARGURA//2-55, 9)
    _txt(surf, f'NV:{nivel:02d}',   a['fnt_xs'], LARANJA,    LARGURA-62, 9)
    from config import VELOCIDADE_SCROLL_MAXIMA, ALTURA
    proporcao = min(vel_scroll / max(VELOCIDADE_SCROLL_MAXIMA, 0.001), 1.0)
    barra_w = int((LARGURA - 4) * proporcao)
    cor_barra = (
        int(80  + 175 * proporcao),
        int(200 - 160 * proporcao),
        int(40),
    )
    barra_surf = pygame.Surface((LARGURA, 4), pygame.SRCALPHA)
    barra_surf.fill((30, 20, 10, 160))
    if barra_w > 0:
        pygame.draw.rect(barra_surf, cor_barra + (210,), (2, 1, barra_w, 2))
    surf.blit(barra_surf, (0, ALTURA - 4))

import os as _os
_REC_PATH = _os.path.join(_os.path.dirname(__file__), 'recorde.txt')

def _ler_rec():
    try:
        with open(_REC_PATH) as f: return int(f.read().strip())
    except: return 0

def _salvar_rec(n):
    try:
        with open(_REC_PATH,'w') as f: f.write(str(n))
    except: pass

def tela_inicio(window, assets):
    clock = pygame.time.Clock()
    t=0; pisca=True
    rx = LARGURA//2 - TAMANHO_RATO//2; rdx=1

    while True:
        clock.tick(FPS); t+=1
        if t>=FPS//2: pisca=not pisca; t=0
        rx+=rdx*2
        if rx>LARGURA//2+35 or rx<LARGURA//2-35: rdx*=-1

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:          return SAIR
            if ev.type==pygame.KEYDOWN:
                if   ev.key==pygame.K_ESCAPE: return SAIR
                elif ev.key==pygame.K_i:      return TELA_INSTRUCOES
                else:                         return TELA_JOGO

        _fundo_menu(window)
        _painel(window, LARGURA//2-200, 145, 400, 260, (210,175,25))
        _txt_c(window, 'SMILI, O RATO', assets['fnt_title'], AMARELO, 165, off=3)
        window.blit(assets['rato'],   (rx, ALTURA//2-15))
        window.blit(assets['queijo'], (LARGURA//2+52, ALTURA//2-8))
        if pisca:
            _txt_c(window,'Pressione qualquer tecla',assets['fnt_xs'],BRANCO,316)
            _txt_c(window,'para jogar!',              assets['fnt_xs'],BRANCO,332)
        _txt_c(window,'I = Instrucoes   ESC = Sair',assets['fnt_xs'],CINZA,ALTURA-48)
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
        linhas = []; linha_atual = ''
        for p in palavras:
            teste = (linha_atual + ' ' + p).strip()
            if fonte.size(teste)[0] <= max_w:
                linha_atual = teste
            else:
                if linha_atual: linhas.append(linha_atual)
                linha_atual = p
        if linha_atual: linhas.append(linha_atual)
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
        ('p',  'Desvie dos veiculos passando na rua, utilize os canos e as tabuas de madeira para atravessar o esgoto, mas nao se esqueca de desviar das serras que estao boiando!', BRANCO),
        ('br', '', None),
        ('p',  'Cuidado com as ratoeiras e para nao ser esmagado pela tela.', VERMELHO),
    ]

    linhas_render = []
    for tipo, txt, cor in blocos:
        if tipo == 'br':   linhas_render.append((None, LH_BL))
        elif tipo == 'h':  linhas_render.append((fnt_t.render(txt, True, cor), LH+4))
        elif tipo == 'kb': linhas_render.append((fnt.render(txt, True, cor), LH))
        elif tipo == 'p':
            for l in wrap(txt, fnt, MAX_W):
                linhas_render.append((fnt.render(l, True, cor), LH))

    total_h = sum(h for _, h in linhas_render)
    TOPO    = 52
    AREA_H  = ALTURA - TOPO - 4
    scroll  = 0
    MAX_SCR = max(0, total_h - AREA_H)

    while True:
        clock.tick(FPS)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:         return SAIR
            if ev.type == pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN, pygame.K_ESCAPE): return TELA_INICIO
                if ev.key == pygame.K_DOWN:  scroll = min(scroll+LH*3, MAX_SCR)
                if ev.key == pygame.K_UP:    scroll = max(scroll-LH*3, 0)
            if ev.type == pygame.MOUSEWHEEL:
                scroll = max(0, min(scroll - ev.y*LH*3, MAX_SCR))

        _fundo_menu(window)
        _txt_c(window, 'INSTRUCOES', fnt_t, AMARELO, 16)
        old_clip = window.get_clip()
        window.set_clip(pygame.Rect(0, TOPO, LARGURA, AREA_H))
        y = TOPO - scroll
        for surf2, h in linhas_render:
            if surf2 and y+h > TOPO and y < TOPO+AREA_H:
                window.blit(surf2, (PAD, y))
            y += h
        window.set_clip(old_clip)
        if MAX_SCR > 0:
            prop = scroll / MAX_SCR
            bh   = max(24, int(AREA_H * AREA_H / total_h))
            by   = TOPO + int((AREA_H - bh) * prop)
            pygame.draw.rect(window, (80,80,80), (LARGURA-4, TOPO, 3, AREA_H))
            pygame.draw.rect(window, CINZA, (LARGURA-4, by, 3, bh), border_radius=2)
        pygame.display.flip()

def tela_pausa(window, assets, mundo=None):
    clock = pygame.time.Clock()
    esc  = pygame.Surface((LARGURA,ALTURA),pygame.SRCALPHA)
    esc.fill((0,0,0,172))
    t=0; m=True

    while True:
        clock.tick(FPS); t+=1
        if t>=FPS//2: m=not m; t=0
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:    return SAIR
            if ev.type==pygame.KEYDOWN:
                if ev.key in (pygame.K_p,pygame.K_RETURN): return TELA_JOGO
                if ev.key==pygame.K_ESCAPE:                return TELA_INICIO
        if mundo is not None:
            mundo.atualizar()
        if mundo is not None:
            _desenhar_mundo(window, mundo)
        window.blit(esc,(0,0))
        _txt_c(window,'PAUSADO',assets['fnt_title'],AMARELO,ALTURA//2-62)
        if m: _txt_c(window,'P ou ENTER = continuar',assets['fnt_xs'],BRANCO,ALTURA//2+12)
        _txt_c(window,'ESC = menu',assets['fnt_xs'],CINZA,ALTURA//2+36)
        pygame.display.flip()

def tela_game_over(window, assets, pontos, recorde, causa):
    clock = pygame.time.Clock()
    novo = (pontos >= recorde and pontos > 0)
    t=0; m=True
    msg_causa = {
        'carro':    'Smili foi atropelado!',
        'ratoeira': 'Smili caiu numa ratoeira!',
        'esgoto':   'Smili se afogou no esgoto!',
        'esmagado': 'Smili foi esmagado pela tela!',
    }.get(causa, 'Smili nao sobreviveu!')
    go = assets.get('game_over_img')

    while True:
        clock.tick(FPS); t+=1
        if t>=FPS//2: m=not m; t=0
        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:    return SAIR
            if ev.type==pygame.KEYDOWN:
                if ev.key in (pygame.K_RETURN,pygame.K_r): return TELA_JOGO
                if ev.key==pygame.K_ESCAPE:                return TELA_INICIO
        _fundo_menu(window)
        _painel(window, 0, 0, LARGURA, ALTURA, (180,30,25))
        _txt_c(window, 'FIM DE JOGO', assets['fnt_title'], VERMELHO, 20, off=3)
        RAT_Y = 60; rat_h = go.get_height() if go else 0
        if go:
            ix = LARGURA//2 - go.get_width()//2
            window.blit(go, (ix, RAT_Y))
        INFO_Y = RAT_Y + rat_h + 10
        _txt_c(window, msg_causa, assets['fnt_sm'], AMARELO, INFO_Y)
        if novo and m:
            _txt_c(window,'!! NOVO RECORDE !!', assets['fnt_sm'], AMARELO, INFO_Y+24)
        _txt_c(window, f'Pontos:  {pontos}',  assets['fnt_md'], BRANCO,      INFO_Y+52)
        _txt_c(window, f'Recorde: {recorde}', assets['fnt_md'], VERDE_CLARO, INFO_Y+76)
        if m: _txt_c(window,'ENTER / R = jogar de novo', assets['fnt_xs'], BRANCO, ALTURA-50)
        _txt_c(window,'ESC = menu', assets['fnt_xs'], CINZA, ALTURA-32)
        pygame.display.flip()

def tela_jogo(window, assets):
    clock = pygame.time.Clock()
    recorde = _ler_rec()
    mundo = Mundo(assets)
    musica(assets)

    while True:
        clock.tick(FPS)

        for ev in pygame.event.get():
            if ev.type==pygame.QUIT:
                if mundo.pontos>recorde: recorde=mundo.pontos; _salvar_rec(recorde)
                pygame.mixer.music.stop()
                return SAIR
            if ev.type==pygame.KEYDOWN:
                if ev.key==pygame.K_ESCAPE:
                    pygame.mixer.music.stop()
                    return TELA_INICIO
                elif ev.key in (pygame.K_UP, pygame.K_w):    mundo.mover_rato(0,-1)
                elif ev.key in (pygame.K_DOWN, pygame.K_s):  mundo.mover_rato(0,+1)
                elif ev.key in (pygame.K_LEFT, pygame.K_a):  mundo.mover_rato(-1,0)
                elif ev.key in (pygame.K_RIGHT, pygame.K_d): mundo.mover_rato(+1,0)
                elif ev.key==pygame.K_p:
                    res = tela_pausa(window, assets, mundo)
                    if res != TELA_JOGO:
                        pygame.mixer.music.stop()
                        return res

        mundo.atualizar()
        mundo.atualizar_camera()
        resultado, coletou = mundo.verificar_colisoes()
        if coletou:
            som(assets,'mordeu')
        if resultado != 'ok':
            pygame.mixer.music.stop()
            som(assets,'morreu')
            pts = mundo.pontos
            if pts > recorde: recorde=pts; _salvar_rec(recorde)
            return tela_game_over(window, assets, pts, recorde, resultado)

        _desenhar_mundo(window, mundo)
        _hud(window, assets, mundo.pontos, recorde, mundo.nivel, mundo.vel_scroll)
        pygame.display.flip()