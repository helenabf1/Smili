import pygame

pygame.init()
pygame.mixer.init()

LARGURA, ALTURA = 600, 600
window = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption('Smili, o rato')

clock = pygame.time.Clock()
rodando = True
while rodando:
    clock.tick(30)
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            rodando = False

pygame.quit()
