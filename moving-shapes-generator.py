from PIL import Image, ImageDraw
import random
import os
import math

# ==== CONFIG ====
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600
BACKGROUND_COLOR = (255, 255, 255)
MIN_MOVE_STEP = 5
MAX_MOVE_STEP = 100
MIN_SHAPE_SIZE = 10
MAX_SHAPE_SIZE = 150
MIN_ROTATION_STEP = 1
MAX_ROTATION_STEP = 20
MIN_SCALE_FACTOR = 0.5
MAX_SCALE_FACTOR = 2.0

NUM_FRAMES = 3
NUM_TRAIN_CLIPS = 8000
NUM_TEST_CLIPS = 2000

TRASLATION_ON = True
ROTATION_ON = True
SCALE_ON = True

OUTPUT_DIR = "outputs"


def create_image(width, height, color):
    """Create a blank image with the specified color."""
    image = Image.new("RGB", (width, height), color)
    draw = ImageDraw.Draw(image)
    return image, draw

def rotate_point(x, y, cx, cy, angle):
    """Rotate a point (x, y) around a center (cx, cy) by an angle in degrees."""
    radians = math.radians(angle)
    cos_theta = math.cos(radians)
    sin_theta = math.sin(radians)
    x_new = cos_theta * (x - cx) - sin_theta * (y - cy) + cx
    y_new = sin_theta * (x - cx) + cos_theta * (y - cy) + cy
    return x_new, y_new

def generate_motion(mode, clip_name, shape_type):
    move_step_x = random.randint(MIN_MOVE_STEP, MAX_MOVE_STEP)
    move_step_y = random.randint(MIN_MOVE_STEP, MAX_MOVE_STEP)
    direction_x = random.choice([-1, 1])
    direction_y = random.choice([-1, 1])
    base_x = random.randint(0, IMAGE_WIDTH - IMAGE_WIDTH // 4)
    base_y = random.randint(0, IMAGE_HEIGHT - IMAGE_HEIGHT // 4)
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    base_rotation = random.randint(0, 360)
    rotation_step = random.randint(MIN_ROTATION_STEP, MAX_ROTATION_STEP)
    scale_factor = random.uniform(MIN_SCALE_FACTOR, MAX_SCALE_FACTOR)

    if shape_type == "circle":
        size = random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE)
    elif shape_type in ["rectangle", "triangle"]:
        size = (random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE), 
                random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE))

    for frame in range(NUM_FRAMES):
        image, draw = create_image(IMAGE_WIDTH, IMAGE_HEIGHT, BACKGROUND_COLOR)

        current_x = base_x + frame * move_step_x * direction_x
        current_y = base_y + frame * move_step_y * direction_y

        current_rotation = base_rotation + frame * rotation_step

    if shape_type == "circle":
        size = random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE)
    elif shape_type in ["rectangle", "triangle"]:
        size = (random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE), 
                random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE))

    for frame in range(NUM_FRAMES):
        image, draw = create_image(IMAGE_WIDTH, IMAGE_HEIGHT, BACKGROUND_COLOR)

        current_x = base_x + frame * move_step_x * direction_x
        current_y = base_y + frame * move_step_y * direction_y

        current_rotation = base_rotation + frame * rotation_step

        if shape_type == "circle":
            current_scale = 1.0 + (scale_factor * frame / NUM_FRAMES)
            current_size = size * current_scale
            draw.ellipse((current_x - current_size, current_y - current_size, current_x + current_size, current_y + current_size), fill=color)

        elif shape_type == "rectangle":
            current_scale = 1.0 + (scale_factor * frame / NUM_FRAMES)
            current_size = (int(size[0] * current_scale), int(size[1] * current_scale))
            x1, y1 = current_x, current_y
            x2, y2 = current_x + current_size[0], current_y
            x3, y3 = current_x + current_size[0], current_y + current_size[1]
            x4, y4 = current_x, current_y + current_size[1]

            # Apply rotation
            cx, cy = current_x + current_size[0] // 2, current_y + current_size[1] // 2  # Center of rectangle
            x1, y1 = rotate_point(x1, y1, cx, cy, current_rotation)
            x2, y2 = rotate_point(x2, y2, cx, cy, current_rotation)
            x3, y3 = rotate_point(x3, y3, cx, cy, current_rotation)
            x4, y4 = rotate_point(x4, y4, cx, cy, current_rotation)

            draw.polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)], fill=color)

        elif shape_type == "triangle":
            current_scale = 1.0 + (scale_factor * frame / NUM_FRAMES)
            current_size = (int(size[0] * current_scale), int(size[1] * current_scale))
            x1, y1 = current_x, current_y
            x2, y2 = current_x + current_size[0], current_y
            x3, y3 = current_x + current_size[0] // 2, current_y - current_size[1]

            # Apply rotation
            cx, cy = current_x + current_size[0] // 2, current_y - current_size[1] // 2  # Center of triangle
            x1, y1 = rotate_point(x1, y1, cx, cy, current_rotation)
            x2, y2 = rotate_point(x2, y2, cx, cy, current_rotation)
            x3, y3 = rotate_point(x3, y3, cx, cy, current_rotation)

            draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=color)

        output_path = os.path.join(OUTPUT_DIR, mode, clip_name)
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        image.save(os.path.join(output_path, f"frame_{frame + 1}.png"))

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "train"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "test"), exist_ok=True)
    shape_types = (["circle", "rectangle", "triangle"])


    for i in range(NUM_TRAIN_CLIPS):
        shape_type = random.choice(shape_types)
        clip_name = f"clip_{i + 1:04d}"
        generate_motion("train", clip_name, shape_type)
    for i in range(NUM_TEST_CLIPS):
        shape_type = random.choice(shape_types)
        clip_name = f"clip_{i + 1:04d}"
        generate_motion("test", clip_name, shape_type)
