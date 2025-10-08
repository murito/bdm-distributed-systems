import pygame

class LoadSprite(pygame.sprite.Sprite):
    def __init__(self, pos, width, height, image):
        super().__init__()
        cropped = pygame.Rect(pos, (width, height))
        self.image = image
        self.rect = self.image.get_rect(center=pos)
        self.cropped = self.image.subsurface(cropped)

    def update(self):
        # Add any sprite-specific logic here, e.g., movement
        pass
