from pyautogui import pixel
from PIL import ImageGrab

from yaml import safe_load

with open("config.yaml") as config_file:
    config = safe_load(config_file)

VERY_FAST_THRESHOLD = config["VERY_FAST_THRESHOLD"]


def check_pixel_color(x, y, threshold=20):
    # Get the pixel color at the given coordinates
    actual_color = pixel(x, y)

    # Check if any RGB value exceeds the threshold
    for value in actual_color:
        if value > threshold:
            return True

    return False


def check_pixel_color_range(start_x, start_y, end_x, end_y, num_pixels, threshold=20):
    # Grab the region of interest
    screenshot = ImageGrab.grab(bbox=(start_x, start_y, end_x + 1, end_y + 1))

    # Convert the screenshot to grayscale format
    screenshot = screenshot.convert("L")

    # Save the screenshot to an image file
    # screenshot.save("screenshot.png")

    very_fast_range = screenshot.height - 105

    top = very_fast_range
    bottom = screenshot.height
    solid = {"L": 0, "R": 0}
    # Check if it is a very fast note
    for y in range(top, bottom):
        # Check the pixel at (0, y)
        # print(f"checking 0, {y}")
        if screenshot.getpixel((0, y)) > threshold:
            solid["L"] += 1
        # Check the pixel at (-1, y), i.e., the last column
        if screenshot.getpixel((-1, y)) > threshold:
            solid["R"] += 1

    if ((solid["L"] / very_fast_range) >= VERY_FAST_THRESHOLD) or (
        (solid["R"] / very_fast_range) >= VERY_FAST_THRESHOLD
    ):
        # screenshot.save(f"{perf_counter()}.png")
        return 2

    # Check if there is valid pixel within the screenshot
    # Iterate over the first num_pixels in the 0th and -1th columns
    for y in range(num_pixels):
        # Check the pixel at (0, y)
        if screenshot.getpixel((0, y)) > threshold:
            return 1
        # Check the pixel at (-1, y), i.e., the last column
        if screenshot.getpixel((-1, y)) > threshold:
            return 1

    return 0
