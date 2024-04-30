#!/bin/bash

# Set file extension for search
FILE_EXTENSION=".txt"

# Get the list of accounts in the organization
ACCOUNTS=$(aws organizations list-accounts --query 'Accounts[*].Id' --output text)

# Iterate through each account
for ACCOUNT_ID in $ACCOUNTS
do
    echo "Account: $ACCOUNT_ID"

    # Switch to the account
    AWS_ACCESS_KEY_ID=$(aws sts get-caller-identity --query 'Arn' --output text | cut -d'/' -f2)
    AWS_SECRET_ACCESS_KEY=$(aws sts get-session-token --serial-number "arn:aws:iam::$ACCOUNT_ID:user/$AWS_ACCESS_KEY_ID" --token-code $TOKEN_CODE --query 'Credentials.SecretAccessKey' --output text)
    AWS_SESSION_TOKEN=$(aws sts get-session-token --serial-number "arn:aws:iam::$ACCOUNT_ID:user/$AWS_ACCESS_KEY_ID" --token-code $TOKEN_CODE --query 'Credentials.SessionToken' --output text)
    export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
    export AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN

    # Get the list of buckets in the account
    BUCKETS=$(aws s3 ls --output text --query 'Buckets[].Name')

    # Iterate through each bucket
    for BUCKET in $BUCKETS
    do
        echo "  Bucket: $BUCKET"

        # List objects in the bucket with the specified file extension
        aws s3 ls "s3://$BUCKET" --recursive | grep "$FILE_EXTENSION$"
    done
done


#!/bin/bash

# Get a list of AWS account IDs in the organization
account_ids=$(aws organizations list-accounts --output text --query 'Accounts[*].Id')

# Iterate through each account
for account_id in $account_ids; do
    echo "Checking account: $account_id"
    
    # Assume role in the member account
    assumed_role=$(aws sts assume-role --role-arn "arn:aws:iam::$account_id:role/OrganizationAccountAccessRole" --role-session-name "AssumeRoleSession")

    # Set the assumed role credentials
    export AWS_ACCESS_KEY_ID=$(echo $assumed_role | jq -r '.Credentials.AccessKeyId')
    export AWS_SECRET_ACCESS_KEY=$(echo $assumed_role | jq -r '.Credentials.SecretAccessKey')
    export AWS_SESSION_TOKEN=$(echo $assumed_role | jq -r '.Credentials.SessionToken')

    # List S3 buckets in the account
    buckets=$(aws s3api list-buckets --output json | jq -r '.Buckets[].Name')

    # Iterate through each bucket
    for bucket in $buckets; do
        echo "Checking bucket: $bucket"
        
        # List objects in the bucket with .torrent extension
        torrent_objects=$(aws s3api list-objects --bucket $bucket --output json --query "Contents[?contains(Key, '.torrent')].Key")
        
        # Output any .torrent objects
        if [ -n "$torrent_objects" ]; then
            echo "Torrent objects in bucket $bucket:"
            echo "$torrent_objects"
        fi
    done

    # Unset assumed role credentials
    unset AWS_ACCESS_KEY_ID
    unset AWS_SECRET_ACCESS_KEY
    unset AWS_SESSION_TOKEN
done
