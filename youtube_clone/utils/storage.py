import os

from .azure_storage import upload_image_with_azure_storage, upload_video_with_azure_storage
from .cloudinary_storage import upload_image_with_cloudinary, upload_video_with_cloudinary

debug = os.environ.get('DEBUG')

def upload_image(image, folder):
    if eval(debug):
        return upload_video_with_cloudinary(image, folder)

    return upload_image_with_azure_storage(image)

def upload_video(video, folder):
    if eval(debug):
        return upload_video_with_cloudinary(video, folder)

    return upload_video_with_azure_storage(video)
