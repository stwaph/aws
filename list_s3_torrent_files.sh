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
