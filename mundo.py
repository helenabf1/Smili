"""
mundo.py — geração e movimento de carros na rua.
"""
import pygame, random
from config import (LARGURA, ALTURA, FAIXA_H, TAMANHO_RATO,
                    PONTOS_POR_PASSO,
                    VELOCIDADE_INICIAL_CARRO, VELOCIDADE_MAXIMA_CARRO)

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

POOL_CARROS=[
    ('car_onibus',65,55,2),('car_sedan_verm',60,55,3),
    ('car_van_ratz',63,55,2),('car_sedan_verd',60,55,3),('car_lixo',80,55,2),
]

def _wt(pool): return [p[-1] for p in pool]
def _pick(pool): return random.choices(pool,weights=_wt(pool),k=1)[0]

class Mundo:
    def __init__(self, assets):
        self.assets   = assets
        self.pontos   = 0
        self.nivel    = 1
        self.vel_car  = VELOCIDADE_INICIAL_CARRO

        self.rato_wx = LARGURA//2 - TAMANHO_RATO//2
        self.rato_wy = 0

        self.CAMERA_OFFSET = int(600*0.62)
        self.camera_y = float(self.rato_wy - self.CAMERA_OFFSET)

        self.carros = []
        self.plataformas = []
        self.obst    = []
        self.queijos = []
        self._faixas_geradas = set()
        self._gerar_faixas()

    def atualizar_camera(self):
        alvo = self.rato_wy - self.CAMERA_OFFSET
        self.camera_y += (alvo - self.camera_y) * 0.14

    def world_to_screen_y(self, wy): return int(wy - self.camera_y)

    def _gerar_faixas(self):
        top = int((self.camera_y-FAIXA_H*3)//FAIXA_H)-2
        bot = int((self.camera_y+620)//FAIXA_H)+3
        for fi in range(top, bot):
            if fi in self._faixas_geradas: continue
            self._faixas_geradas.add(fi)
            t  = tipo_faixa(fi)
            wy = fi * FAIXA_H
            if t == 'road':
                self._spawn_carros(fi, wy)

    def _spawn_carros(self, fi, wy):
        n   = random.randint(2, 4)
        key,larg,alt,_ = _pick(POOL_CARROS)
        dir = 1 if fi%2==0 else -1
        vel = min(self.vel_car*random.uniform(0.8,1.3), VELOCIDADE_MAXIMA_CARRO)
        img_key = key if dir==1 else f'{key}_flip'
        img = self.assets.get(img_key) or self.assets.get(key)
        cy  = wy + (FAIXA_H-alt)//2
        GAP = max(larg+30, random.randint(180,320))
        for k in range(n):
            wx = (-larg-k*GAP-random.randint(0,60)) if dir==1 else (LARGURA+k*GAP+random.randint(0,60))
            self.carros.append({'wx':wx,'wy':cy,'w':larg,'h':alt,'vel':vel,'dir':dir,'img':img})

    def mover_rato(self, dx, dy):
        nx = self.rato_wx + dx*TAMANHO_RATO
        ny = self.rato_wy + dy*FAIXA_H
        nx = max(0, min(LARGURA-TAMANHO_RATO, nx))
        if ny > FAIXA_H: ny = self.rato_wy
        moved = (nx!=self.rato_wx or ny!=self.rato_wy)
        self.rato_wx = nx; self.rato_wy = ny
        if dy < 0: self.pontos += PONTOS_POR_PASSO
        return moved

    def atualizar(self):
        for c in self.carros:
            c['wx'] += c['vel'] * c['dir']
            if c['dir']==1 and c['wx'] > LARGURA+20:
                c['wx'] = -c['w'] - random.randint(80,280)
            elif c['dir']==-1 and c['wx'] < -c['w']-20:
                c['wx'] = LARGURA + random.randint(80,280)

        MARGIN=750; cy=self.camera_y
        self.carros = [e for e in self.carros if abs(e['wy']-cy)<MARGIN]
        self._gerar_faixas()

    @staticmethod
    def _aabb(ax,ay,aw,ah,bx,by,bw,bh,mg=0):
        return ax+mg<bx+bw and ax+aw-mg>bx and ay+mg<by+bh and ay+ah-mg>by

    def verificar_colisoes(self):
        rx,ry = self.rato_wx,self.rato_wy
        MG = 10
        for c in self.carros:
            if self._aabb(rx,ry,TAMANHO_RATO,TAMANHO_RATO,c['wx'],c['wy'],c['w'],c['h'],MG):
                return 'carro', False
        return 'ok', False
