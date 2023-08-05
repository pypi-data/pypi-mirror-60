import csv
from decimal import Decimal

"""
This script reads a CSV and inserts it into a DynamoDB table.

- columns 0 and 1 are used for the key: partition key `pk: S` and sort key `sk: S` - your table needs these keys defined
- column 2, if not an empty string, is set to `data: S`
- all other columns are added as non-key attributes. the column should be formatted `<attribute_name>: <attribute_value>`

Only meant for protoyping with small amounts of data, not for production use.

See README for more information.
"""


def row_to_item(row):
    """
    Converts a row from CSV into a DynamoDB item with keys `pk` and `sk`, indices 0 and 1 from input row.
    Index 2 is `data` and all other columns (formatted attribute_name: attribute_value) are added to the item.
    """

    def format_att_name(att_name):
        return att_name.lower().replace(' ', '_')

    def crudely_try_numeric(val):
        try:
            return Decimal(val)
        except:
            return val

    # create item with partition and sort key
    item = {
        'pk': row[0],
        'sk': row[1]
    }

    # if data has been provided, add it
    if row[2] != '':
        item['data'] = row[2]

    # all other attributes should be encoded attribute_name: value
    # crudely attempt to make it a number
    for att in row[3:]:
        if att != '':
            (att_name, value) = att.split(": ", 1)
            item[format_att_name(att_name)] = crudely_try_numeric(value)

    return item


def run_import(filename, table, header_rows=2):
    """
    Bulk imports data from CSV file, see example.csv.
    """
    with open(filename, newline='') as csvfile:
        print(f"Importing {filename}...")
        reader = csv.reader(csvfile)

        # skip n header rows
        for i in range(0, header_rows):
            next(reader)

        with table.batch_writer() as batch:
            for row in reader:
                item = row_to_item(row)
                print(f"PutItem: {item['pk']}, {item['sk']}")
                batch.put_item(item)
