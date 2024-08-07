import pygame

def scale_image(image: pygame.Surface, scale_factor: float) -> pygame.Surface:
    if scale_factor == 1: 
        return image
    width, height = image.get_rect().size[0], image.get_rect().size[1]
    return pygame.transform.scale(image, (int(width * scale_factor), int(height * scale_factor)))

def extract_platforms(source_path='assets/images/jungle tileset.png', scale_factor=1) -> list:
    sheet = pygame.image.load(source_path).convert_alpha()
    platform_coords = [(0, 16, 27, 25), (26, 16, 27, 25), (53, 16, 27, 25)]
    return [scale_image(sheet.subsurface(coords), scale_factor) for coords in platform_coords]

def extract_vines(source_path='assets/images/jungle tileset.png', scale_factor=1):
    sheet = pygame.image.load(source_path).convert_alpha()
    vine_coords = [(21*16, 12*16, 24*16, 15 * 16)] 
    return [scale_image(sheet.subsurface(coords), scale_factor) for coords in vine_coords]

def extract_images(path: str, sprite_width: int, scale_factor=1) -> list:
    sheet = pygame.image.load(path) 
    width, h = sheet.get_size()
    sprites = int(width / sprite_width)
    images = []
    for x in range(sprites):
        images.append(scale_image(sheet.subsurface(x * sprite_width, 0, sprite_width, h), scale_factor))
    return images

