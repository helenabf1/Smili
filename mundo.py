"""
mundo.py — só estrutura de mapa e câmera

MAPA (14 faixas):
  0,5,13 → calçada pedra (safe)
  1–4    → rua
  6,12   → calçada bege (safe)
  7–11   → esgoto
"""
import pygame
from config import (LARGURA, ALTURA, FAIXA_H, TAMANHO_RATO,
                    PONTOS_POR_PASSO)

PADRAO = {0:'safe_pedra',1:'road',2:'road',3:'road',4:'road',
          5:'safe_pedra',6:'safe_bege',
          7:'sewer',8:'sewer',9:'sewer',10:'sewer',11:'sewer',
          12:'safe_bege',13:'safe_pedra'}

def tipo_faixa(idx): return PADRAO[abs(idx)%14]
def tile_key(tipo):
    if tipo=='road':      return 'tile_rua'
    if tipo=='sewer':     return 'tile_esgoto'
    if tipo=='safe_bege': return 'tile_calcada_bege'
    return 'tile_calcada_pedra'

class Mundo:
    def __init__(self, assets):
        self.assets = assets
        self.pontos = 0
        self.nivel  = 1

        self.rato_wx = LARGURA//2 - TAMANHO_RATO//2
        self.rato_wy = 0

        self.CAMERA_OFFSET = int(600 * 0.62)
        self.camera_y = float(self.rato_wy - self.CAMERA_OFFSET)

    def atualizar_camera(self):
        alvo = self.rato_wy - self.CAMERA_OFFSET
        self.camera_y += (alvo - self.camera_y) * 0.14

    def world_to_screen_y(self, wy): return int(wy - self.camera_y)

    def mover_rato(self, dx, dy):
        nx = self.rato_wx + dx * TAMANHO_RATO
        ny = self.rato_wy + dy * FAIXA_H
        nx = max(0, min(LARGURA - TAMANHO_RATO, nx))
        if ny > FAIXA_H: ny = self.rato_wy
        moved = (nx != self.rato_wx or ny != self.rato_wy)
        self.rato_wx = nx
        self.rato_wy = ny
        if dy < 0: self.pontos += PONTOS_POR_PASSO
        return moved

    def atualizar(self):
        pass   # obstáculos serão adicionados em seguida

    def verificar_colisoes(self):
        return 'ok', False
