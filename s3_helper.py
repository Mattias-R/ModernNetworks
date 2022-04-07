import boto3


def upload(file_name, bucket, object_name):
    s3_client = boto3.client('s3')
    response = s3_client.upload_file(file_name, bucket, object_name)
    return response


def download(file_name, bucket):
    s3 = boto3.client('s3',
                      aws_access_key_id="ASIA32QL3DO7FMLDIZKT",
                      aws_secret_access_key="R+b/mZe8F/tf2lq9M9PYXpOLa36y7tTdakxgC8Zz",
                      aws_session_token="FwoGZXIvYXdzEDsaDCE2NoJBb83Jc8NihSLXAfC+A7p32QMSUWWeDAEYIBMmwx479L3nvPdtLocd2+LIVxq/eQI6Dx4AkHc44ZW9NoWSUVYRkvxmwxN+beeGq8Sn3PZ44VC16q8SJnf+nhG0zCQOBA4d8xfB+vInNZ94nUgms6MAZoptGhjfBNWOcyv167ylFPeY0IquWC2oMUl8CupjjXPQr6n9niTQcSBSfKeKBiEpTVYxpWRfUFTozdYjuOXVtYS1c9AhszeNMMYW5UYXVStHb2rafNsAOWqTe8XJUn4zawkP2uKWOMlSa9Mlyj1W3XA5KP7KvJIGMi13ytr33eg+DzdTXorvrm/hcIrMWEWaztnQvK9LoMmvTFlBYpjKIBy+sVT3Lt0="
                      )
    output = f"download_files/{file_name}"
    s3.Bucket(bucket).download_file(file_name, output)
    return output


def list_all_files(bucket):
    s3 = boto3.client('s3')
    contents = []
    for item in s3.list_objects(Bucket=bucket)['Contents']:
        contents.append(item)
    return contents