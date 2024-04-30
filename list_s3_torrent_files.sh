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
