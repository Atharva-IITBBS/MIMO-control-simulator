from PIL import Image

def append_images(images, direction='horizontal', alignment='center', bg_color=(255, 255, 255,0)):
    # Determine the dimensions of the final image
    widths, heights = zip(*(img.size for img in images))
    total_width = sum(widths)
    max_height = max(heights)

    # Create a new empty image with an RGBA mode (to support transparency)
    new_image = Image.new('RGBA', (total_width, max_height), bg_color)

    # Paste each image onto the new image
    x_offset = 0
    for img in images:
        if direction == 'horizontal':
            new_image.paste(img, (x_offset, 0), img)
            x_offset += img.width
        elif direction == 'vertical':
            y_offset = max_height - img.height if alignment == 'bottom' else 0
            new_image.paste(img, (0, y_offset), img)

    return new_image

# Example usage
image1 = Image.open('res/bin.png').convert('RGBA')  # Ensure RGBA mode
image2 = Image.open('res/bin.png').convert('RGBA')  # Ensure RGBA mode
image3 = Image.open('res/bin.png').convert('RGBA')  # Ensure RGBA mode
image4 = Image.open('res/bin.png').convert('RGBA')

# Append images horizontally
combined_image = append_images([image1, image2, image3,image4], direction='horizontal')

# Save the combined image with transparency
combined_image.save('combined_image.png', format='PNG')
