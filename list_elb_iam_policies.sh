#!/bin/bash

# Get all IAM roles and users
roles=$(aws iam list-roles --output text --query 'Roles[*].RoleName')
users=$(aws iam list-users --output text --query 'Users[*].UserName')

# Iterate over roles and users
for role in $roles; do
  # Get IAM policies attached to the role
  policies=$(aws iam list-role-policies --role-name "$role" --output text --query 'PolicyNames[*]')

  # Iterate over the policies
  for policy in $policies; do
    # Get the policy document
    policy_doc=$(aws iam get-role-policy --role-name "$role" --policy-name "$policy" --output text --query 'PolicyDocument')

    # Check if the policy document contains the word "elasticloadbalancing"
    if [[ "$policy_doc" == *"elasticloadbalancing"* ]]; then
      echo "Policy '$policy' attached to role '$role' contains 'elasticloadbalancing'."
    fi
  done
done

for user in $users; do
  # Get IAM policies attached to the user
  policies=$(aws iam list-user-policies --user-name "$user" --output text --query 'PolicyNames[*]')

  # Iterate over the policies
  for policy in $policies; do
    # Get the policy document
    policy_doc=$(aws iam get-user-policy --user-name "$user" --policy-name "$policy" --output text --query 'PolicyDocument')

    # Check if the policy document contains the word "elasticloadbalancing"
    if [[ "$policy_doc" == *"elasticloadbalancing"* ]]; then
      echo "Policy '$policy' attached to user '$user' contains 'elasticloadbalancing'."
    fi
  done
done
