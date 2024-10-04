import os
import sqlite3
import csv
import json
import argparse


def export_db_to_csv(db_path, output_csv):
    """
    Exports the contents of a SQLite database to a CSV file for the samples table 
    and a JSON file for metadata and labels.

    Parameters:
    - db_path (str): The path to the SQLite database file. Can be an absolute path or a path relative 
                     to the user's home directory (using '~' expansion).
    - output_csv (str): The path to the output CSV file, which will contain the filepath and label columns 
                        from the 'samples' table. The JSON file will be named after the CSV file 
                        (with a '.json' extension) and will store metadata and labels.

    The function performs the following tasks:
    1. Connects to the SQLite database.
    2. Extracts the data from the 'samples' table (file path and label) and writes it to a CSV file.
    3. Extracts metadata (dataset name and base directory) and labels (list of all labels) from the 
       database and saves them into a JSON file.
    
    Raises:
    - sqlite3.DatabaseError: If there are any issues with database access or queries.
    - IOError: If there is a problem writing to the CSV or JSON file.
    """
    db_path = os.path.expanduser(db_path);
    
    output_json = output_csv+".json"

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Exportar os samples para CSV
    c.execute('SELECT filepath, label FROM samples')
    samples = c.fetchall()
    
    with open(output_csv, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['filepath', 'label'])
        csv_writer.writerows(samples)

    # Exportar metadata e labels para JSON
    c.execute('SELECT * FROM metadata')
    metadata = c.fetchone()
    c.execute('SELECT label FROM labels')
    labels = [row[0] for row in c.fetchall()]

    data = {
        "dataset_name": metadata[0],
        "base_dir": metadata[1],
        "labels": labels
    }

    with open(output_json, 'w') as jsonfile:
        json.dump(data, jsonfile, indent=4)

    conn.close()


################################################################################

def main():
    EXAMPLE_USE='''
Example of use:

image-label-convert -i "~/.config/image-label-server/sqlite_dbs/ber2024-body.db" -o "some_name.csv"
    '''
    
    # Inicializa o parser
    parser = argparse.ArgumentParser(
        description="Program to convert the sqlite dataset to csv file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXAMPLE_USE
    )
    
    # Adiciona os argumentos
    parser.add_argument(
        '-i', '--input', 
        type=str, 
        help='The path of input SQLite dataset', 
        required=True
    )
    
    parser.add_argument(
        '-o', '--output', 
        type=str, 
        help='The path of output csv dataset', 
        required=True
    )
    
    ####################################
    # Faz o parsing dos argumentos
    args = parser.parse_args()
    
    export_db_to_csv(args.input,args.output)
    
    
if __name__ == "__main__":
    main()

