from PIL import Image, ImageDraw
import random
import os

# ==== CONFIG ====
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600
BACKGROUND_COLOR = (255, 255, 255)
MIN_MOVE_STEP = 5
MAX_MOVE_STEP = 100
MIN_SHAPE_SIZE = 10
MAX_SHAPE_SIZE = 150

NUM_FRAMES = 3
NUM_TRAIN_CLIPS = 8000
NUM_TEST_CLIPS = 2000

OUTPUT_DIR = "outputs"


def create_image(width, height, color):
    """Create a blank image with the specified color."""
    image = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(image)
    return image, draw

def draw_circle(draw, x, y, radius, color):
    draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)

def draw_rectangle(draw, x, y, width, height, color):
    draw.rectangle((x, y, x + width, y + height), fill=color)

def draw_triangle(draw, x1, y1, x2, y2, x3, y3, color):
    draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=color)

def generate_circle_motion(mode, clip_name):
    move_step_x = random.randint(MIN_MOVE_STEP, MAX_MOVE_STEP)
    move_step_y = random.randint(MIN_MOVE_STEP, MAX_MOVE_STEP)
    direction_x = random.choice([-1, 1])
    direction_y = random.choice([-1, 1])
    base_x = random.randint(0, IMAGE_WIDTH)
    base_y = random.randint(0, IMAGE_HEIGHT)
    circle_radius = random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    for frame in range(NUM_FRAMES):
        image, draw = create_image(IMAGE_WIDTH, IMAGE_HEIGHT, BACKGROUND_COLOR)

        current_x = base_x + frame * move_step_x * direction_x
        current_y = base_y + frame * move_step_y * direction_y

        draw_circle(draw, current_x, current_y, circle_radius, color)

        if not os.path.exists(os.path.join(OUTPUT_DIR, mode, clip_name)):
            os.makedirs(os.path.join(OUTPUT_DIR, mode, clip_name))

        image.save(os.path.join(OUTPUT_DIR, mode,clip_name, f"frame_{frame + 1}.png"))

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "train"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "test"), exist_ok=True)
    for i in range(NUM_TRAIN_CLIPS):
        clip_name = f"clip_{i + 1:04d}"  
        generate_circle_motion("train", clip_name)
    for i in range(NUM_TEST_CLIPS):
        clip_name = f"clip_{i + 1:04d}"  
        generate_circle_motion("test", clip_name)

