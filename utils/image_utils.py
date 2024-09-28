from PIL import Image, ImageOps

class ImageHandler:
    def resize_image(self, image_path, target_width, target_height):
        image = Image.open(image_path)
        image.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Create a new image with white background
        new_image = Image.new("RGB", (target_width, target_height), "white")
        paste_position = (
            (target_width - image.width) // 2,
            (target_height - image.height) // 2
        )
        new_image.paste(image, paste_position)
        return new_image