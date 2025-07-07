from PIL import Image, ImageDraw
import random
import os
import math

# ==== CONFIG ====
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600
BACKGROUND_COLOR = (255, 255, 255)
MIN_MOVE_STEP = 5
MAX_MOVE_STEP = 80
MIN_SHAPE_SIZE = 10
MAX_SHAPE_SIZE = 100
MIN_ROTATION_STEP = 1
MAX_ROTATION_STEP = 20
MIN_SCALE_FACTOR = 0.5
MAX_SCALE_FACTOR = 2.0

NUM_FRAMES = 3
NUM_TRAIN_CLIPS = 8000
NUM_TEST_CLIPS = 2000

TRANSLATION_ON = True
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

def generate_motion(draw, shape, frame):
    move_step_x = shape["move_step_x"]
    move_step_y = shape["move_step_y"]
    direction_x = shape["direction_x"]
    direction_y = shape["direction_y"]

    base_x = shape["base_x"]
    base_y = shape["base_y"]
    color = shape["color"]
    base_rotation = shape["base_rotation"]
    rotation_step = shape["rotation_step"]
    scale_factor = shape["scale_factor"]
    size = shape["size"]
    shape_type = shape["type"]

    current_x = base_x + frame * move_step_x * direction_x if TRANSLATION_ON else base_x
    current_y = base_y + frame * move_step_y * direction_y if TRANSLATION_ON else base_y
    current_rotation = base_rotation + frame * rotation_step if ROTATION_ON else base_rotation
    current_scale = 1.0 + (scale_factor * frame / NUM_FRAMES) if SCALE_ON else 1.0

    if shape_type == "circle":
        current_size = size * current_scale
        draw.ellipse((current_x - current_size, current_y - current_size, current_x + current_size, current_y + current_size), fill=color)

    elif shape_type == "rectangle":
        current_size = (int(size[0] * current_scale), int(size[1] * current_scale))
        x1, y1 = current_x, current_y
        x2, y2 = current_x + current_size[0], current_y
        x3, y3 = current_x + current_size[0], current_y + current_size[1]
        x4, y4 = current_x, current_y + current_size[1]

        if ROTATION_ON:
            cx, cy = current_x + current_size[0] // 2, current_y + current_size[1] // 2
            x1, y1 = rotate_point(x1, y1, cx, cy, current_rotation)
            x2, y2 = rotate_point(x2, y2, cx, cy, current_rotation)
            x3, y3 = rotate_point(x3, y3, cx, cy, current_rotation)
            x4, y4 = rotate_point(x4, y4, cx, cy, current_rotation)

        draw.polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)], fill=color)

    elif shape_type == "triangle":
        current_size = (int(size[0] * current_scale), int(size[1] * current_scale))
        x1, y1 = current_x, current_y
        x2, y2 = current_x + current_size[0], current_y
        x3, y3 = current_x + current_size[0] // 2, current_y - current_size[1]

        if ROTATION_ON:
            cx, cy = current_x + current_size[0] // 2, current_y - current_size[1] // 2
            x1, y1 = rotate_point(x1, y1, cx, cy, current_rotation)
            x2, y2 = rotate_point(x2, y2, cx, cy, current_rotation)
            x3, y3 = rotate_point(x3, y3, cx, cy, current_rotation)

        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=color)



def save_clip(image, mode, clip_name, frame):
    """Save the generated clip as an image file."""
    output_path = os.path.join(OUTPUT_DIR, mode, clip_name)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    image.save(os.path.join(output_path, f"frame_{frame + 1}.png"))

def generate_clip(mode, clip_name):
    shape_types = ["circle", "rectangle", "triangle"]

    # Initialize shared properties for each shape
    shapes = []
    for shape_type in shape_types:
        base_x = random.randint(0, IMAGE_WIDTH - MAX_SHAPE_SIZE)
        base_y = random.randint(0, IMAGE_HEIGHT - MAX_SHAPE_SIZE)
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        base_rotation = random.randint(0, 360)
        rotation_step = random.randint(MIN_ROTATION_STEP, MAX_ROTATION_STEP)
        scale_factor = random.uniform(MIN_SCALE_FACTOR, MAX_SCALE_FACTOR)
        move_step_x = random.randint(MIN_MOVE_STEP, MAX_MOVE_STEP)
        move_step_y = random.randint(MIN_MOVE_STEP, MAX_MOVE_STEP)
        direction_x = random.choice([-1, 1])
        direction_y = random.choice([-1, 1])


        if shape_type == "circle":
            size = random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE)
        elif shape_type in ["rectangle", "triangle"]:
            size = (random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE), 
                    random.randint(MIN_SHAPE_SIZE, MAX_SHAPE_SIZE))

        shapes.append({
            "type": shape_type,
            "base_x": base_x,
            "base_y": base_y,
            "color": color,
            "base_rotation": base_rotation,
            "rotation_step": rotation_step,
            "scale_factor": scale_factor,
            "move_step_x": move_step_x,
            "move_step_y": move_step_y,
            "direction_x": direction_x,
            "direction_y": direction_y,
            "size": size
        })

    # Generate frames with motion for each shape
    for frame in range(NUM_FRAMES):
        image, draw = create_image(IMAGE_WIDTH, IMAGE_HEIGHT, BACKGROUND_COLOR)
        for shape in shapes:
            generate_motion(
                draw,
                shape, 
                frame
            )
        save_clip(image, mode, clip_name, frame)


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "train"), exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, "test"), exist_ok=True)

    print("Generating training clips...")
    for i in range(NUM_TRAIN_CLIPS):
        clip_name = f"clip_{i + 1:04d}"
        generate_clip("train", clip_name)
    print("Generating test clips...")
    for i in range(NUM_TEST_CLIPS):
        clip_name = f"clip_{i + 1:04d}"
        generate_clip("test", clip_name)
    print("All clips generated successfully.")
