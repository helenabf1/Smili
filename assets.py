"""assets.py — carrega todos os sprites, tiles, sons e fontes."""
import pygame, os
from config import IMG_DIR, SND_DIR, FNT_DIR, TAMANHO_RATO, FAIXA_H

def _img(name, w=None, h=None):
    p = os.path.join(IMG_DIR, name)
    if not os.path.exists(p):
        return None
    s = pygame.image.load(p).convert_alpha()
    if w and h:   return pygame.transform.smoothscale(s,(w,h))
    if h:
        ow,oh = s.get_size()
        return pygame.transform.smoothscale(s,(int(ow*h/oh),h))
    if w:
        ow,oh = s.get_size()
        return pygame.transform.smoothscale(s,(w,int(oh*w/ow)))
    return s

def _plain(w,h,cor):
    s=pygame.Surface((w,h),pygame.SRCALPHA); s.fill(cor); return s

def _flip(s): return pygame.transform.flip(s,True,False)

def carregar_assets():
    a = {}

    #fontes
    fp = os.path.join(FNT_DIR,'PressStart2P.ttf')
    if os.path.exists(fp):
        a['fnt_xs']    = pygame.font.Font(fp,  7)
        a['fnt_sm']    = pygame.font.Font(fp,  9)
        a['fnt_md']    = pygame.font.Font(fp, 13)
        a['fnt_lg']    = pygame.font.Font(fp, 18)
        a['fnt_title'] = pygame.font.Font(fp, 22)
    else:
        for k,sz in [('fnt_xs',11),('fnt_sm',14),('fnt_md',18),
                     ('fnt_lg',24),('fnt_title',30)]:
            a[k] = pygame.font.SysFont('monospace',sz)

    #rato
    r = _img('rato.png', TAMANHO_RATO, TAMANHO_RATO)
    a['rato']      = r if r else _plain(TAMANHO_RATO,TAMANHO_RATO,(190,160,110,255))
    a['rato_flip'] = _flip(a['rato'])

    #carros
    _carros = ['onibus','sedan_verm','van_ratz','sedan_verd','lixo']
    for nome in _carros:
        c = _img(f'car_{nome}.png')
        if c is None:
            c = _plain(80,60,(150,150,150,255))
        a[f'car_{nome}']      = c
        a[f'car_{nome}_flip'] = _flip(c)

    #obstaculos
    _obs = [('obs_barrel',52,58),('obs_pneu',60,52),('obs_caixa_mad',60,52),
            ('obs_pallets',75,48),('obs_saco_lixo',50,58),('obs_gravetos',70,48)]
    for nome,ow,oh in _obs:
        o = _img(f'{nome}.png', ow, oh)
        a[nome] = o if o else _plain(ow,oh,(120,100,70,255))

    #canos
    _cores_cano = ['cinza','marrom','azul','verde']
    _fallback_w = {'g':220,'m':148,'p':98}
    for cor in _cores_cano:
        for sz,fw in _fallback_w.items():
            img = _img(f'cano_{cor}_{sz}.png')
            a[f'cano_{cor}_{sz}'] = img if img else _plain(fw,52,(120,110,90,255))
    for sz in ['g','m','p']:
        a[f'cano_cinza_claro_{sz}']  = a.get(f'cano_cinza_{sz}')
        a[f'cano_cinza_escuro_{sz}'] = a.get(f'cano_cinza_{sz}')
        a[f'cano_terra_{sz}']        = a.get(f'cano_marrom_{sz}')

    #ratoeira
    rt = _img('ratoeira.png',42,42)
    a['ratoeira'] = rt if rt else _plain(42,42,(100,70,30,255))

    #queijo
    q = _img('queijo.png',34,28)
    a['queijo'] = q if q else _plain(34,28,(230,195,20,255))

    #tiles de cenario
    def _tile(name, fallback_cor):
        t = _img(name, 600, FAIXA_H)
        return t if t else _plain(600, FAIXA_H, fallback_cor)

    a['tile_calcada_pedra'] = _tile('tile_calcada_pedra.png', (115,112,108,255))
    a['tile_rua']           = _tile('tile_rua.png',           ( 72, 76, 82,255))
    a['tile_calcada_bege']  = _tile('tile_calcada_bege.png',  (185,160,110,255))
    a['tile_esgoto']        = _tile('tile_esgoto_hd.png',     ( 55, 18, 85,255))

    #game over
    go = _img('game_over_rato.png')
    a['game_over_img'] = go

    #sons
    for sname in ['anda', 'mordeu', 'morreu']:
        p = os.path.join(SND_DIR, f'{sname}.ogg')
        a[f'som_{sname}'] = pygame.mixer.Sound(p) if os.path.exists(p) else None

    # musica de fundo
    a['musica'] = os.path.join(SND_DIR, 'musica_fundo.ogg')
    return a

def som(a, nome):
    s = a.get(f'som_{nome}')
    if s: s.play()

def musica(a):
    p = a.get('musica','')
    if p and os.path.exists(p):
        pygame.mixer.music.load(p)
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(-1)
