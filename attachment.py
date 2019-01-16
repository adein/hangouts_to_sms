class Attachment:
    """MMS message attachment.

    Model that describes an attachment to an MMS message.
    """
    album_id = None  # Google Photos ID (not used)
    photo_id = None  # Google Photos ID (not used)
    media_type = None  # Type of attachment: PHOTO, ANIMATED_PHOTO, VIDEO
    original_content_url = None
    download_url = None  # This is used to get file extension

    def __init__(self, album_id=None, photo_id=None, media_type=None, original_content_url=None, download_url=None):
        self.album_id = album_id
        self.photo_id = photo_id
        self.media_type = media_type
        self.original_content_url = original_content_url
        self.download_url = download_url
