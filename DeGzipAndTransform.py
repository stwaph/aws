import boto3
import gzip
import csv
import io
from collections import defaultdict

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    bucket_name = 'stwaph-cur-qhackathon'
    prefix = 'cur/QCUR/data/'

    # Initialize a stack to keep track of prefixes to process
    stack = [prefix]

    # Initialize results dictionaries for different groupings
    summed_costs_by_product_code = defaultdict(float)
    summed_costs_by_instance_type = defaultdict(float)

    while stack:
        current_prefix = stack.pop()

        # List objects in the bucket with the current prefix
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=current_prefix, Delimiter='/')

        if 'Contents' in response:
            for item in response['Contents']:
                file_key = item['Key']

                # Check if the file is a gziped CSV file
                if file_key.endswith('.csv.gz'):
                    process_csv_file(bucket_name, file_key, summed_costs_by_product_code, summed_costs_by_instance_type)

        # Add subfolders to the stack for further processing
        if 'CommonPrefixes' in response:
            for common_prefix in response['CommonPrefixes']:
                prefix_value = common_prefix['Prefix']
                stack.append(prefix_value)

    # Convert results to CSV
    output_csv = convert_to_csv(summed_costs_by_product_code, summed_costs_by_instance_type)

    # Append results for product_instance_type to CSV
    # output_csv += '\n' + convert_to_csv(summed_costs_by_instance_type)

    # Use the same S3 key as the input file but with a different filename
    combined_file_key = file_key.replace('.csv.gz', '_combined.csv').replace(prefix, '')

    # Upload the combined results to S3
    s3_client.put_object(Bucket=bucket_name, Key=combined_file_key, Body=output_csv.encode('utf-8'))

    return {
        'statusCode': 200,
        'body': 'Processed and combined all gziped CSV files in the S3 bucket'
    }
    
def process_csv_file(bucket_name, file_key, summed_costs_by_product_code, summed_costs_by_instance_type):
    # Read the gziped CSV file from S3
    obj = s3_client.get_object(Bucket=bucket_name, Key=file_key)

    # Uncompress the gziped file
    with gzip.GzipFile(fileobj=obj['Body']) as gzip_file:
        # Read the uncompressed CSV content
        csv_content = gzip_file.read().decode('utf-8')

        # Parse the CSV content
        parse_csv(csv_content, summed_costs_by_product_code, summed_costs_by_instance_type)

def parse_csv(csv_content, summed_costs_by_product_code, summed_costs_by_instance_type):
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    
    for row in csv_reader:
        product_code = row['line_item_product_code']
        instance_type = row['product_instance_type']
        billing_period_start_date = row['bill_billing_period_start_date']
        
        try:
            blended_cost = float(row['line_item_blended_cost'])
            
            key_product_code = (product_code, billing_period_start_date)
            summed_costs_by_product_code[key_product_code] += blended_cost
            
            key_instance_type = (instance_type, billing_period_start_date)
            summed_costs_by_instance_type[key_instance_type] += blended_cost
        except ValueError:
            print(f"Skipping non-numeric value for blended_cost in file: {row}")

def convert_to_csv(results_product_code, results_instance_type):
    output = io.StringIO()
    csv_writer = csv.writer(output)
    
    # Write header for summed_costs_by_product_code
    csv_writer.writerow(['Service', 'bill_billing_period_start_date', 'total_blended_cost'])
    
    for (group, billing_period_start_date), total_cost in results_product_code.items():
        csv_writer.writerow([group, billing_period_start_date, total_cost])
    
    # Write separator between the two groups of data
    csv_writer.writerow([])
    
    # Write header for summed_costs_by_instance_type
    csv_writer.writerow(['Instance Type', 'bill_billing_period_start_date', 'total_blended_cost'])
    
    for (group, billing_period_start_date), total_cost in results_instance_type.items():
        csv_writer.writerow([group, billing_period_start_date, total_cost])
    
    return output.getvalue()
