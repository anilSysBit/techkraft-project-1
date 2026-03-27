import os
from datetime import datetime
from django.utils.text import slugify

def upload_to_model_folder(instance, filename):
    """
    Uploads files into a lowercase folder named after the model.
    Example:
        brand/20251103_093212_logo.png
        product/20251103_093215_image.jpg
    """

    # Split filename and extension
    base_name, ext = os.path.splitext(filename)

    # Timestamp format: YYYYMMDD_HHMMSS
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Clean and slugify filename
    safe_name = slugify(base_name)

    # Get model name in lowercase
    model_name = instance.__class__.__name__.lower()

    # Build final path
    return f"{model_name}/{timestamp}_{safe_name}{ext.lower()}"
