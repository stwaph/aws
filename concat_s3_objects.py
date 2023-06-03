import boto3

# Create an S3 client
s3 = boto3.client('s3')

# Source bucket and objects to be concatenated
source_bucket_name = 'stwaph12345678'
source_object_keys = ['test-big-file1.log', 'test-big-file2.log']

# Destination bucket and object
destination_bucket_name = 'multipart-copy-test1'
destination_object_key = 'concated-objects'

# Get the size of each source object
object_sizes = []
for key in source_object_keys:
    response = s3.head_object(Bucket=source_bucket_name, Key=key)
    object_sizes.append(response['ContentLength'])

# Initialize the multipart upload
response = s3.create_multipart_upload(Bucket=destination_bucket_name, Key=destination_object_key)
upload_id = response['UploadId']

# Initialize an empty list to store the uploaded parts
parts = []

# Upload each part of the object
part_number = 1
offset = 0
for i, key in enumerate(source_object_keys):
    while offset < object_sizes[i]:
        # Determine the range of the source object to copy
        start_range = offset
        end_range = min(offset + 5 * 1024 * 1024 - 1, object_sizes[i] - 1)

        # Copy the part from the source object to the destination object
        response = s3.upload_part_copy(
            Bucket=destination_bucket_name,
            Key=destination_object_key,
            PartNumber=part_number,
            CopySource={
                'Bucket': source_bucket_name,
                'Key': key
            },
            CopySourceRange=f"bytes={start_range}-{end_range}",
            UploadId=upload_id
        )

        # Record the uploaded part
        part = {
            'PartNumber': part_number,
            'ETag': response['CopyPartResult']['ETag']
        }
        parts.append(part)

        # Move to the next part
        part_number += 1
        offset += (end_range - start_range + 1)

# Complete the multipart upload
response = s3.complete_multipart_upload(
    Bucket=destination_bucket_name,
    Key=destination_object_key,
    MultipartUpload={
        'Parts': parts
    },
    UploadId=upload_id
)

# Print the response
print(response)

