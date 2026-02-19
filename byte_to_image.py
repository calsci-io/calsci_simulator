from PIL import Image
from professor_panda import professor_panda
WIDTH = 128
HEIGHT = 64
PAGES = 8

def render_bitmap(data, filename="output.png",
                  scale=6, gap=1, margin=20,
                  pixel_color=(0, 0, 0),
                  bg_color=(255, 255, 255)):
    
    if len(data) != WIDTH * PAGES:
        raise ValueError("Data must be exactly 1024 bytes")

    # Calculate final image size
    pixel_block = scale
    total_pixel_size = scale + gap

    img_width = WIDTH * total_pixel_size - gap
    img_height = HEIGHT * total_pixel_size - gap

    final_width = img_width + 2 * margin
    final_height = img_height + 2 * margin

    img = Image.new("RGB", (final_width, final_height), bg_color)
    pixels = img.load()

    index = 0
    for page in range(PAGES):
        for x in range(WIDTH):
            byte = data[index]
            index += 1

            for bit in range(8):
                y = page * 8 + bit
                pixel_on = (byte >> bit) & 0x01

                if pixel_on:
                    draw_x = margin + x * total_pixel_size
                    draw_y = margin + y * total_pixel_size

                    # Draw square block
                    for dx in range(scale):
                        for dy in range(scale):
                            pixels[draw_x + dx, draw_y + dy] = pixel_color

    img.save(filename)
    print(f"Saved as {filename}")
# Render image
render_bitmap(professor_panda, "professor_panda.png", scale=10, gap=0, margin=20)
