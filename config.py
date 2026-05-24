from os import path


LARGURA = 600
ALTURA  = 600
FPS = 30

TAMANHO_RATO = 40
FAIXA_H = 80

PONTOS_POR_PASSO  = 10
PONTOS_POR_QUEIJO = 50

PONTOS_POR_NIVEL             = 100
AUMENTO_VELOCIDADE           = 0.45
VELOCIDADE_INICIAL_CARRO     = 2.8
VELOCIDADE_MAXIMA_CARRO      = 12.0
VELOCIDADE_INICIAL_TRONCO    = 1.5
VELOCIDADE_MAXIMA_TRONCO     = 6.0

IMG_DIR  = path.join(path.dirname(__file__), 'assets', 'imagens')
SND_DIR  = path.join(path.dirname(__file__), 'sons')
FNT_DIR  = path.join(path.dirname(__file__), 'assets', 'fontes')

TELA_INICIO     = 0
TELA_INSTRUCOES = 1
TELA_JOGO       = 2
TELA_PAUSA      = 3
TELA_GAME_OVER  = 4
SAIR            = 5

PRETO        = (  0,   0,   0)
BRANCO       = (255, 255, 255)
CINZA        = (120, 120, 120)
CINZA_ESCURO = ( 22,  18,  14)
VERDE_CLARO  = (130, 200,  70)
AMARELO      = (240, 200,  20)
VERMELHO     = (210,  40,  35)
LARANJA      = (225,  95,  20)
MARROM_CLARO = (195, 165, 115)
