"""
mundo.py — lógica final do jogo.

MAPA (14 faixas):
  0,5,13 → calçada pedra (safe)
  1–4    → rua (carros + ratoeiras)
  6,12   → calçada bege (safe)
  7–11   → esgoto (canos/plataformas móveis)
"""
import pygame, random
from config import (LARGURA, ALTURA, FAIXA_H, TAMANHO_RATO,
                    PONTOS_POR_PASSO, PONTOS_POR_QUEIJO,
                    PONTOS_POR_NIVEL, AUMENTO_VELOCIDADE,
                    VELOCIDADE_INICIAL_CARRO, VELOCIDADE_MAXIMA_CARRO,
                    VELOCIDADE_INICIAL_TRONCO, VELOCIDADE_MAXIMA_TRONCO,
                    VELOCIDADE_SCROLL_INICIAL, AUMENTO_SCROLL_POR_NIVEL,
                    VELOCIDADE_SCROLL_MAXIMA, MARGEM_MORTE_SCROLL)

PADRAO={0:'safe_pedra',1:'road',2:'road',3:'road',4:'road',
        5:'safe_pedra',6:'safe_bege',
        7:'sewer',8:'sewer',9:'sewer',10:'sewer',11:'sewer',
        12:'safe_bege',13:'safe_pedra'}

def tipo_faixa(idx): return PADRAO[abs(idx)%14]
def tile_key(tipo):
    if tipo=='road':      return 'tile_rua'
    if tipo=='sewer':     return 'tile_esgoto'
    if tipo=='safe_bege': return 'tile_calcada_bege'
    return 'tile_calcada_pedra'

#pools

POOL_CARROS=[
    ('car_onibus',65,55,2),('car_sedan_verm',60,55,3),
    ('car_van_ratz',63,55,2),('car_sedan_verd',60,55,3),('car_lixo',80,55,2),
]

def _build_plataformas_pool(assets):
    pool = []
    cores  = ['cinza','marrom','azul','verde']
    pesos  = {'g':3, 'm':2, 'p':1}
    for cor in cores:
        for sz,peso in pesos.items():
            key = f'cano_{cor}_{sz}'
            img = assets.get(key)
            if img:
                w_real,h_real = img.get_size()
                pool.append((key, w_real, h_real, peso))
    for key in ['obs_pneu','obs_pallets','obs_bau']:
        img = assets.get(key)
        if img:
            w_real,h_real = img.get_size()
            pool.append((key, w_real, h_real, 1))
    return pool

def _wt(pool):
    return [p[-1] for p in pool]
def _pick(pool):
    return random.choices(pool,weights=_wt(pool),k=1)[0]

def _overlap(ax,ay,aw,ah, bx,by,bw,bh, gap=20):
    return not(ax+aw+gap<=bx or bx+bw+gap<=ax or ay+ah+gap<=by or by+bh+gap<=ay)

#mundo
class Mundo:
    def __init__(self, assets):
        self.assets=assets
        self.PLAT_POOL=_build_plataformas_pool(assets)
        self.pontos=0; self.nivel=1; self.causa_morte=''
        self.vel_car=VELOCIDADE_INICIAL_CARRO
        self.vel_plat=VELOCIDADE_INICIAL_TRONCO
        self.vel_scroll=VELOCIDADE_SCROLL_INICIAL

        self.rato_wx=LARGURA//2-TAMANHO_RATO//2
        self.rato_wy=0
        self.em_plataforma=False
        self._plat_ref=None

        self.CAMERA_OFFSET=int(600*0.62)
        self.camera_y=float(self.rato_wy-self.CAMERA_OFFSET)

        self.carros=[]; self.plataformas=[]; self.obst=[]; self.queijos=[]
        self._faixas_geradas=set()
        self._gerar_faixas()

    #camera
    def atualizar_camera(self):
        self.camera_y -= self.vel_scroll

        alvo = self.rato_wy - self.CAMERA_OFFSET
        
        if self.camera_y > alvo:
            self.camera_y += (alvo - self.camera_y) * 0.14
        self.camera_y = min(self.camera_y, float(-self.CAMERA_OFFSET + FAIXA_H))

    def world_to_screen_y(self, wy): return int(wy - self.camera_y)

    def rato_esmagado(self):
        """Retorna True se o rato saiu pela borda inferior da tela."""
        sy = self.world_to_screen_y(self.rato_wy)
        return sy > ALTURA - MARGEM_MORTE_SCROLL

    def _gerar_faixas(self):
        top=int((self.camera_y-FAIXA_H*3)//FAIXA_H)-2
        bot=int((self.camera_y+620)//FAIXA_H)+3
        for fi in range(top,bot):
            if fi in self._faixas_geradas: continue
            self._faixas_geradas.add(fi)
            t=tipo_faixa(fi); wy=fi*FAIXA_H
            if t=='road':
                self._spawn_carros(fi,wy)
                self._spawn_ratoeiras(fi,wy)
            elif t=='sewer':
                self._spawn_plataformas(fi,wy)
                if random.random()<0.38:
                    self._spawn_queijo_safe(fi,wy)
            elif t in('safe_pedra','safe_bege'):
                self._spawn_queijo_safe(fi,wy)

    def _spawn_carros(self,fi,wy):
        n=random.randint(2,4)
        key,larg,alt,_=_pick(POOL_CARROS)
        dir=1 if fi%2==0 else -1
        vel=min(self.vel_car*random.uniform(0.8,1.3),VELOCIDADE_MAXIMA_CARRO)
        img_key=key if dir==1 else f'{key}_flip'
        img=self.assets.get(img_key) or self.assets.get(key)
        cy=wy+(FAIXA_H-alt)//2

        GAP=max(larg+30, random.randint(180,320))
        for k in range(n):
            wx=(-larg-k*GAP-random.randint(0,60)) if dir==1 else (LARGURA+k*GAP+random.randint(0,60))
            self.carros.append({'wx':wx,'wy':cy,'w':larg,'h':alt,'vel':vel,'dir':dir,'img':img})

    def _spawn_plataformas(self, fi, wy):
        if not self.PLAT_POOL: return

        dir = 1 if fi % 2 == 0 else -1
        vel = min(self.vel_plat * random.uniform(0.8, 1.25), VELOCIDADE_MAXIMA_TRONCO)
        n = random.randint(2, 3)

        GAP_MIN = 220

        novas = []
        offset = 0
        for k in range(n):
            key, larg, alt, _ = _pick(self.PLAT_POOL)
            img = self.assets.get(key)
            if not img:
                continue
            larg, alt = img.get_size()
            alt = 50

            cy = wy + (FAIXA_H - alt) // 2

            gap_extra = random.randint(0, 100)
            slot = larg + GAP_MIN + gap_extra

            if dir == 1:
                wx = -larg - offset - random.randint(0, 40)
            else:
                wx = LARGURA + offset + random.randint(0, 40)

            offset += slot
            novas.append({'wx': wx, 'wy': cy, 'w': larg, 'h': alt,
                          'vel': vel, 'dir': dir, 'img': img, 'fi': fi})

        self.plataformas.extend(novas)

    def _spawn_ratoeiras(self,fi,wy):
        if random.random()>0.55: return
        for _ in range(random.randint(1,2)):
            wx=random.randint(20,LARGURA-62); cy=wy+(FAIXA_H-42)//2
            self.obst.append({'wx':wx,'wy':cy,'w':42,'h':42,'img':self.assets['ratoeira'],'tipo':'ratoeira'})

    def _spawn_queijo_safe(self,fi,wy):
        if random.random()>0.55: return
        for _ in range(random.randint(1,2)):
            wx=random.randint(30,LARGURA-64); cy=wy+(FAIXA_H-28)//2
            if not any(_overlap(wx,cy,34,28,q['wx'],q['wy'],q['w'],q['h'])
                       for q in self.queijos if abs(q['wy']-cy)<10):
                self.queijos.append({'wx':wx,'wy':cy,'w':34,'h':28,'coletado':False})

    def mover_rato(self,dx,dy):
        nx=self.rato_wx+dx*TAMANHO_RATO; ny=self.rato_wy+dy*FAIXA_H
        nx=max(0,min(LARGURA-TAMANHO_RATO,nx))
        if ny>FAIXA_H: ny=self.rato_wy
        moved=(nx!=self.rato_wx or ny!=self.rato_wy)
        self.rato_wx=nx; self.rato_wy=ny
        if dy<0: self.pontos+=PONTOS_POR_PASSO
        return moved

    def atualizar(self):
        """
        BUG CORRIGIDO: obstáculos continuam se movendo mesmo durante a pausa.
        O método atualizar() é chamado também pela tela de pausa a cada frame,
        garantindo que carros e plataformas nunca "congelem".
        """
        nv=1+self.pontos//PONTOS_POR_NIVEL
        if nv>self.nivel:
            self.nivel=nv
            self.vel_car=min(VELOCIDADE_INICIAL_CARRO+(nv-1)*AUMENTO_VELOCIDADE,VELOCIDADE_MAXIMA_CARRO)
            self.vel_plat=min(VELOCIDADE_INICIAL_TRONCO+(nv-1)*AUMENTO_VELOCIDADE*0.5,VELOCIDADE_MAXIMA_TRONCO)
            self.vel_scroll=min(VELOCIDADE_SCROLL_INICIAL+(nv-1)*AUMENTO_SCROLL_POR_NIVEL,VELOCIDADE_SCROLL_MAXIMA)

        for c in self.carros:
            c['wx'] += c['vel'] * c['dir']
            if c['dir'] == 1 and c['wx'] > LARGURA + 20:
                c['wx'] = -c['w'] - random.randint(80, 280)
            elif c['dir'] == -1 and c['wx'] < -c['w'] - 20:
                c['wx'] = LARGURA + random.randint(80, 280)

        self.em_plataforma=False; self._plat_ref=None
        for p in self.plataformas:
            old_wx=p['wx']; p['wx']+=p['vel']*p['dir']
            if p['dir'] == 1 and p['wx'] > LARGURA + 30:
                p['wx'] = -p['w'] - random.randint(220, 420)
            elif p['dir'] == -1 and p['wx'] < -p['w'] - 30:
                p['wx'] = LARGURA + random.randint(220, 420)
            
            if self._sobre_plataforma(p):
                self.em_plataforma=True; self._plat_ref=p
                delta=p['wx']-old_wx
                self.rato_wx+=delta
                self.rato_wx=max(0,min(LARGURA-TAMANHO_RATO,self.rato_wx))

        MARGIN=750; cy=self.camera_y
        self.carros=[e for e in self.carros if abs(e['wy']-cy)<MARGIN]
        self.plataformas=[e for e in self.plataformas if abs(e['wy']-cy)<MARGIN]
        self.obst=[e for e in self.obst if abs(e['wy']-cy)<MARGIN]
        self.queijos=[q for q in self.queijos if not q['coletado'] and abs(q['wy']-cy)<MARGIN]
        self._gerar_faixas()

    def _sobre_plataforma(self,p,mg=8):
        rx,ry=self.rato_wx,self.rato_wy; rw,rh=TAMANHO_RATO,TAMANHO_RATO
        cy_rato=ry+rh//2
        return (rx+mg<p['wx']+p['w'] and rx+rw-mg>p['wx'] and
                cy_rato>p['wy']-12 and cy_rato<p['wy']+p['h']+12)

    @staticmethod
    def _aabb(ax,ay,aw,ah,bx,by,bw,bh,mg=0):
        return ax+mg<bx+bw and ax+aw-mg>bx and ay+mg<by+bh and ay+ah-mg>by

    def verificar_colisoes(self):
        rx,ry=self.rato_wx,self.rato_wy; rw,rh=TAMANHO_RATO,TAMANHO_RATO
        MG=10; coletou=False
        # morte por esmagamento
        if self.rato_esmagado():
            self.causa_morte='esmagado'; return 'esmagado',False
        for c in self.carros:
            if self._aabb(rx,ry,rw,rh,c['wx'],c['wy'],c['w'],c['h'],MG):
                self.causa_morte='carro'; return 'carro',False
        for o in self.obst:
            if o['tipo']=='ratoeira' and self._aabb(rx,ry,rw,rh,o['wx'],o['wy'],o['w'],o['h'],MG):
                self.causa_morte='ratoeira'; return 'ratoeira',False
        fi=round(self.rato_wy/FAIXA_H)
        if tipo_faixa(fi)=='sewer' and not self.em_plataforma:
            self.causa_morte='esgoto'; return 'esgoto',False
        for q in self.queijos:
            if not q['coletado'] and self._aabb(rx,ry,rw,rh,q['wx'],q['wy'],q['w'],q['h'],0):
                q['coletado']=True; self.pontos+=PONTOS_POR_QUEIJO; coletou=True
        return 'ok',coletou
