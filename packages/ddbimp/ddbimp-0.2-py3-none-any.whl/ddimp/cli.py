import argparse
import boto3
import ddimp.importer as importer

def main():
    parser = argparse.ArgumentParser(
        description='Loads CSV into a DynamoDB table. This script is only meant for protoyping small amounts of data, not for production use.')
    parser.add_argument('--table', dest='table', type=str,
                        required=True, help='DynamoDB table')
    parser.add_argument('--region', dest='region', type=str,
                        default='eu-west-1', help='AWS region')
    parser.add_argument('--skip', dest='skip_rows', type=int,
                        default=2, help='Skip N lines from input file')
    parser.add_argument('filename', type=str,
                        help='CSV file to load, see example.csv')
    args = parser.parse_args()

    dynamodb = boto3.resource('dynamodb', region_name=args.region)
    table = dynamodb.Table(args.table)

    importer.run_import(args.filename, table, args.skip_rows)
