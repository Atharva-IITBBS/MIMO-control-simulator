from PIL import Image
import os

color = (200, 140, 0) #   0->255
# (200, 140, 0) -->Orange

def change_color(directory, new_color):
    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            img = Image.open(os.path.join(directory, filename))
            img = img.convert("RGBA")  # Ensure the image is in RGBA mode
            data = img.load()
            print(filename)
            if filename == 'play-button.png':continue
            width, height = img.size
            for y in range(height):
                for x in range(width):
                    r, g, b, a = data[x, y]
                    if a != 0:  # If pixel is not transparent
                        data[x, y] = new_color + (a,)

            img.save(os.path.join(directory,filename))

# Usage
change_color('C:/StudyMaterial/MTech/Internship/tclab/CodeBase/GUI_PyQt/res', color)  # 