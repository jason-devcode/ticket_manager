import cloudinary
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from djangopwa.constants import FILE_UPLOAD_MAX_MEMORY_SIZE

def config_cloudinary():
    cloudinary.config(
        cloud_name="dusa5qwvg",
        api_key="944626978748449",
        api_secret="KnzUC5rKeppKhG5v_HzZHSd29A8",
        secure=True,
    )


# for test
# def config_cloudinary():
#     # cloudinary.config(
#     #     cloud_name="dusa5qwvg",
#     #     api_key="944626978748449",
#     #     api_secret="KnzUC5rKeppKhG5v_HzZHSd29A8",
#     #     secure=True,
#     # )
#     cloudinary.config(
#         cloud_name="duurnadl1",
#         api_key="937335851538736",
#         api_secret="2l1zjuhVBo7zfEJCrAKImXSxehc",  # Click 'View Credentials' below to copy your API secret
#         secure=True,
#     )




def file_validation(file):
    if not file:
        raise ValidationError("No file selected.")

    # For regular upload, we get UploadedFile instance, so we can validate it.
    # When using direct upload from the browser, here we get an instance of the CloudinaryResource
    # and file is already uploaded to Cloudinary.
    # Still can perform all kinds on validations and maybe delete file, approve moderation, perform analysis, etc.
    if isinstance(file, UploadedFile):
        if file.size > FILE_UPLOAD_MAX_MEMORY_SIZE:
            raise ValidationError("File shouldn't be larger than 10MB.")
