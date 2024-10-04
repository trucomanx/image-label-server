# Image Label Server

## Overview

`image-label-server` is a Python-based server for managing image datasets and their associated labels. It allows users to authenticate, query the size of datasets, obtain unclassified images, and classify them through a REST API. This server supports both JSON and SQLite for database management.

## Prerequisites

- Python 3.6+
- Flask
- SQLite3
- Pillow (for image handling)
- `requests` library (for client interactions)

## Installation

1. **Clone the repository**:

```bash
git clone https://github.com/trucomanx/image-label-server.git
cd image-label-server
```

2. **Install required Python libraries**:

```bash
pip install -r requirements.txt
```

3. **Create the configuration file:**:

Create a `config.json` in the root directory or at `~/.config/image-label-server/config.json`. 
This configuration file will define where the server looks for the JSON datasets and SQLite databases.

Example `config.json`:

```json
{
    "json_db_dir": "/path/to/json_datasets",
    "sqlite_db_dir": "/path/to/sqlite_dbs",
    "json_user_dir": "/path/to/json_users"
}
```

You can adjust these paths as needed for your environment.

## Running the Server

1. **Ensure you have dataset and user JSON files**:

* For dataset files, place the JSON files in the `json_db_dir`. The structure of the dataset file should look like this:

```json
{
    "dataset_name": "NAMEDB",
    "labels": ["positive", "negative", "neutral", "pain", "other"],
    "base_dir": "/path/to/images",
    "samples": [
        {"filepath": "image1.png", "label": "neutral"},
        {"filepath": "image2.jpeg", "label": ""},
        {"filepath": "image3.bmp", "label": "positive"}
    ]
}
```

* For user authentication, place the JSON files in the `json_user_dir`. The structure should be as follows:

```json
{
    "user": "your_username",
    "password": "your_password"
}
```

2. **Start the server**:

The server can be run using the following command:

```bash
python3 image-label-server
```

By default, the server will be accessible at http://127.0.0.1:44444/.

## Endpoints provided by the serve

The following are the main endpoints provided by the server:

1. **`/size` [POST]**

* **Description**: Retrieves the number of samples in a dataset.

* **Authorization**: Basic Authentication required.

* **Request body**:

```json

{
    "dataset_name": "NAMEDB"
}
```
* **Response**:

```json
{
    "dataset_name": "NAMEDB",
    "size": 123
}
```

2. **`/obtain` [POST]**

* **Description**: Obtains an image (by its ID or an unclassified image) and the dataset metadata.

* **Authorization**: Basic Authentication required.

* **Request body**:

```json
{
    "dataset_name": "NAMEDB",
    "id": 0  # Optional. If not provided, the next unclassified sample is returned.
}
```

* **Response**: Returns the image file and metadata about the dataset.

```json
{
    "dataset_name": "NAMEDB",
    "base_dir": "/path/to/images",
    "filepath": "image1.png",
    "labels": ["negative","neutral","positive"]
}
```

3. **`/classify` [POST]**

* **Description**: Classifies an image by updating its label in the dataset.

* **Authorization**: Basic Authentication required.

* **Request body**:

```json
{
    "dataset_name": "NAMEDB",
    "base_dir": "/path/to/images",
    "filepath": "image1.png",
    "label": "positive"
}
```

* **Response**:

```json
    {
        "response": true
    }
```


## Client program Usage

To interact with the server, you can use the provided `client.py`. Below are the usage examples for common operations.

1. **Checking dataset size**:

```bash
python image-label-client -u username -p password -b http://127.0.0.1:44444 -d NAMEDB size
```

2. **Obtaining an image**:

```bash
python image-label-client -u username -p password -b http://127.0.0.1:44444 -d NAMEDB obtain --id 0
```

3. **Classifying an image**:

```bash
python image-label-client -u username -p password -b http://127.0.0.1:44444 -d NAMEDB classify --basedir /path/to/images --filepath image1.png --label positive
```

## CSV Exporter program usage

To export data from the SQLite database to a CSV file, use the `export_csv.py` script. This utility will help you generate CSV files from your database.

### Usage:

```bash
python image-label-export-csv.py
```

Make sure the SQLite database exists in the `SQLITE_DB_DIR` directory and contains data to be exported.
## Troubleshooting

* Ensure the `json_db_dir`, `sqlite_db_dir`, and `json_user_dir` are correctly configured in `config.json`.
* Verify that the JSON dataset and user files follow the required structure.
* Check that the server is running on the correct port and accessible via the provided URL.

