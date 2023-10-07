from django.core.exceptions import ValidationError
import os


# validator images input
def allow_only_images_validator(value):
    # get type images
    ext = os.path.splitext(value.name)[1]
    # type images valid
    valid_extensions = ['.png', '.jpg', '.jpeg']

    # check type images
    if not ext.lower() in valid_extensions:
        raise ValidationError(
            'Unsupported file extension. Allowed extensions: ' + str(valid_extensions))
