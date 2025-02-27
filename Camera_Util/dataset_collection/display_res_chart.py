import pygame
import sys
import os

def transform_scale_keep_ratio(image, size):
    iwidth, iheight = image.get_size()
    scale = min(size[0] / iwidth, size[1] / iheight)
    new_size = (round(iwidth * scale), round(iheight * scale))
    scaled_image = pygame.transform.scale(image, new_size)
    image_rect = scaled_image.get_rect(center=(size[0] // 2, size[1] // 2))
    return scaled_image, image_rect

def main():
    # Initialize pygame
    pygame.init()
    
    # Set display dimensions
    display_x, display_y = 1920, 1080
    img_size_x, img_size_y = 1065, 600
    img_offset_x, img_offset_y = 0, 0
    
    try:
        screen = pygame.display.set_mode((display_x, display_y), pygame.FULLSCREEN, display=1)
    except:
        print("No second monitor available, using main monitor.")
        screen = pygame.display.set_mode((display_x, display_y), pygame.FULLSCREEN)
    
    # Load image
    image_path = r"C:\Users\menon\Documents\Camera_Operation\resolution_charts\Res_Charts_3\(255,255,255).jpg"
    if not os.path.exists(image_path):
        print(f"Error: Image not found at {image_path}")
        pygame.quit()
        sys.exit()
    
    image = pygame.image.load(image_path)
    image, image_rect = transform_scale_keep_ratio(image, (img_size_x, img_size_y))
    image_rect.center = (display_x // 2 + img_offset_x, display_y // 2 + img_offset_y)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                running = False
        
        screen.fill((0, 0, 0))
        screen.blit(image, image_rect)
        pygame.display.flip()
        pygame.display.set_caption("Image Display")
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pygame.quit()
        sys.exit()
