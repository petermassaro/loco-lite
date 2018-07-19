import boto3, botocore
from flask import current_app



def get_presigned_url(filename, expires_in=500):
	url = current_app.s3.generate_presigned_url(
			ClientMethod='get_object', 
			Params={
			'Bucket' : current_app.config['S3_BUCKET'], 
			'Key' : filename,
		}, ExpiresIn=expires_in)
	return url




def upload_file_to_s3(file, bucket_name):

    try:
        current_app.s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )

    except Exception as e:
        print("Something Happened: ", e)
        return e

    return file.filename