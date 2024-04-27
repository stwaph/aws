#!/bin/bash

# Set file extension for search
FILE_EXTENSION=".torrent"

# Get the list of accounts in the organization
ACCOUNTS=$(aws organizations list-accounts --query 'Accounts[*].Id' --output text)

# Iterate through each account
for ACCOUNT_ID in $ACCOUNTS
do
    echo "Account: $ACCOUNT_ID"

    # Get the list of buckets in the account
    BUCKETS=$(aws s3 ls --output text --query 'Buckets[].Name' --account-id $ACCOUNT_ID)

    # Iterate through each bucket
    for BUCKET in $BUCKETS
    do
        echo "  Bucket: $BUCKET"

        # List objects in the bucket with the specified file extension
        aws s3 ls "s3://$BUCKET" --recursive --human-readable --summarize | grep "$FILE_EXTENSION"
    done
done
