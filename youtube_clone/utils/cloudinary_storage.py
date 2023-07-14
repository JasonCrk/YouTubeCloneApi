import os

import cloudinary

cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET'),
    secure=True
)

import cloudinary.uploader

def upload_video_with_cloudinary(video):
    upload_response = cloudinary.uploader.upload_large(
        video,
        folder=f'YOUTUBE_CLONE/videos',
        resource_type='video'
    )
    return dict(upload_response).get('url')

def upload_image_with_cloudinary(image, folder):
    upload_response = cloudinary.uploader.upload(image, folder=f'YOUTUBE_CLONE/{folder}')
    return dict(upload_response).get('url')
