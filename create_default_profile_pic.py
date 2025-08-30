from PIL import Image, ImageDraw, ImageFont
import os

# Create a simple default profile picture
def create_default_profile_pic():
    # Create a 300x300 image with a light gray background
    img = Image.new('RGB', (300, 300), color='#f0f0f0')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple user icon (circle with a smaller circle for head and oval for body)
    # Head
    draw.ellipse([100, 80, 200, 180], fill='#cccccc')
    # Body
    draw.ellipse([75, 160, 225, 260], fill='#cccccc')
    
    # Save the image
    os.makedirs('media/profile_pics', exist_ok=True)
    img.save('media/profile_pics/default.jpg', 'JPEG')
    print("Default profile picture created successfully!")

if __name__ == "__main__":
    create_default_profile_pic()
