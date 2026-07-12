import pygame

class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
    
    def draw(self, surface):
        action = False

        # prendi la posizione del mouse
        pos = pygame.mouse.get_pos()

        # controlla se il mouse è sopra il bottone e le condizioni del click

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = True
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        # disegna il bottone
        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action

class TextButton:
    """Bottone testuale con pannello semi-trasparente ed evidenziazione al passaggio del mouse."""

    PAD_X = 16
    PAD_Y = 10

    def __init__(self, center, text, font):
        self.font = font
        self.center = center
        # True ignora un click già in corso quando il bottone compare
        self.was_pressed = True
        self.set_text(text)

    def arm(self):
        """Ignora il click eventualmente in corso (da chiamare al cambio schermata)."""
        self.was_pressed = True

    def set_text(self, text):
        self.text = text
        self.label = self.font.render(text, True, (255, 255, 255))
        self.rect = pygame.Rect(
            0, 0,
            self.label.get_width() + 2 * self.PAD_X,
            self.label.get_height() + 2 * self.PAD_Y,
        )
        self.rect.center = self.center

    def draw(self, surface):
        action = False
        hover = self.rect.collidepoint(pygame.mouse.get_pos())

        bg = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        bg.fill((0, 0, 0, 170 if hover else 110))
        surface.blit(bg, self.rect.topleft)
        if hover:
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)
        surface.blit(self.label, self.label.get_rect(center=self.rect.center))

        pressed = pygame.mouse.get_pressed()[0]
        if hover and pressed and not self.was_pressed:
            action = True
        self.was_pressed = pressed
        return action
