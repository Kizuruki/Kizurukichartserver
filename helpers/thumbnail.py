from PIL import Image


def create_square_thumbnail(image: Image) -> Image:
    width, height = image.size
    square_size = min(width, height)

    # centered cropping box
    left = (width - square_size) // 2
    top = (height - square_size) // 2
    right = left + square_size
    bottom = top + square_size
    cropped_image = image.crop((left, top, right, bottom))
    return cropped_image
