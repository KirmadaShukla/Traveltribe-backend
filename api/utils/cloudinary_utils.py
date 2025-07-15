import cloudinary
import cloudinary.uploader
import os

# You may want to load these from environment variables or Django settings
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)


def upload_image_to_cloudinary(image_file, folder='trip_covers'):
    result = cloudinary.uploader.upload(image_file, folder=folder)
    return result.get('secure_url') 