import boto3

# Create an AWS Organizations client
org_client = boto3.client('organizations')

# Get the list of accounts in the organization
accounts = org_client.list_accounts()['Accounts']

# Iterate through each account
for account in accounts:
    account_id = account['Id']
    
    # Create an S3 resource for the account
    s3_resource = session.resource('s3')
    
    # List all buckets in the account
    for bucket in s3_resource.buckets.all():
        bucket_name = bucket.name
        print(f"Bucket: {bucket_name} (Account: {account_id})")
        
        # List objects in the bucket with .torrent
        for obj in bucket.objects.filter(Prefix='', Suffix="".torrent"):
            key = obj.key
            print(f"  Object: {key}")
