
from PIL import Image
import requests
from io import BytesIO
import json
from requests.auth import HTTPBasicAuth
import argparse


def get_size(base_url, user_data, dataset_name):
    """
    Retrieves the size (i.e., the number of samples) of a given dataset from the server.

    This function sends a POST request to the `/size` endpoint of a Flask-based server 
    to obtain the size of a specified dataset. The server should respond with a JSON object 
    containing the dataset name and the total number of samples in that dataset.

    Parameters:
    -----------
    base_url : str
        The base URL of the server. This should not include the `/size` endpoint, 
        as that will be added automatically.
        
    user_data : dict
        A dictionary containing user authentication credentials. This dictionary 
        must have two keys:
        - "user": The username to authenticate the request.
        - "password": The password to authenticate the request.
        
    dataset_name : str
        The name of the dataset for which the size is requested. This is passed 
        to the server in the JSON body of the request.

    Returns:
    --------
    dict
        A dictionary representing the JSON response from the server. The expected 
        fields include:
        - "dataset_name": The name of the dataset.
        - "size": The number of samples in the dataset.

    Raises:
    -------
    requests.exceptions.RequestException
        If there is an issue with the network or the server, this exception is 
        raised. Ensure proper error handling when calling this function.
        
    Example Usage:
    --------------
    >>> base_url = "http://localhost:44444"
    >>> user_data = {"user": "username", "password": "userpassword"}
    >>> dataset_name = "my_dataset"
    >>> response = get_size(base_url, user_data, dataset_name)
    >>> print(response)
    {'dataset_name': 'my_dataset', 'size': 500}
    """
    response = requests.post(   f"{base_url}/size", 
                                json={"dataset_name": dataset_name}, 
                                auth=HTTPBasicAuth(user_data["user"],user_data["password"]))
    return response.json()

def obtain_sample(base_url,user_data, dataset_name, image_id):
    """
    Sends a POST request to obtain a specific sample image from a dataset hosted on a server.
    The function communicates with an endpoint, retrieves the image, and returns it as a PIL Image object.

    Args:
        base_url (str): The base URL of the server hosting the dataset.
        user_data (dict): A dictionary containing user credentials. 
                          Must have keys 'user' and 'password' for HTTP basic authentication.
        dataset_name (str): The name of the dataset from which to retrieve the sample.
        image_id (int): The ID of the image to retrieve from the dataset. This can be a 0-based index for specific samples.

    Returns:
        tuple: A tuple containing:
            - image (PIL.Image or None): The retrieved image as a PIL Image object. 
                                         None if the image could not be retrieved.
            - response_data (dict or None): A dictionary containing additional information from the response headers, 
                                            if available. None if no such data exists or if the request fails.

    Raises:
        requests.exceptions.RequestException: If the HTTP request fails for any reason.
        PIL.UnidentifiedImageError: If the content returned from the server is not a valid image format.
    """
    response = requests.post(   f"{base_url}/obtain", 
                                json={"dataset_name": dataset_name, "id": image_id}, 
                                auth=HTTPBasicAuth(user_data["user"],user_data["password"]) )
    
    if response.status_code == 200:
        # Criar uma PIL Image diretamente do conteúdo da resposta
        image = Image.open(BytesIO(response.content))
        
        # Obter o JSON do cabeçalho (se disponível)
        response_json = response.headers.get('X-Response-Json')
        
        if response_json:
            # Converter o JSON do cabeçalho em um dicionário e retornar junto com a imagem
            return image, json.loads(response_json)
        
        return image, None
    
    return None, None

def classify_sample(base_url,user_data, image_data):
    """
    Sends a classification request to a remote server to classify an image sample in a dataset.

    This function sends a POST request to the `/classify` endpoint of a remote server to classify an image sample 
    in a dataset. The image sample is identified by its file path and the classification is performed based on 
    the provided label. The request is authenticated using HTTP Basic Authentication.

    Parameters:
    ----------
    base_url : str
        The base URL of the remote server (e.g., 'http://localhost:44444'). This URL will be concatenated 
        with the `/classify` endpoint to create the full request URL.
        
    user_data : dict
        A dictionary containing user authentication details with the following keys:
        - 'user' (str): The username for HTTP Basic Authentication.
        - 'password' (str): The password for HTTP Basic Authentication.
        
        Example:
        {
            "user": "my_username",
            "password": "my_password"
        }
        
    image_data : dict
        A dictionary containing image classification data with the following keys:
        - 'dataset_name' (str): The name of the dataset where the image is stored.
        - 'base_dir' (str): The base directory where the dataset is stored.
        - 'filepath' (str): The full file path to the image that needs to be classified.
        - 'label' (str): The label assigned to the image for classification.
        
        Example:
        {
            "dataset_name": "animals",
            "base_dir": "/some/path/of/datasets",
            "filepath": "animals/dog.png",
            "label": "dog"
        }

    Returns:
    -------
    dict
        The JSON response from the server, which typically contains information about the classification status.
        The structure of the response will depend on the server's implementation.
        
        Example response:
        {
            "response": True
        }
        
        If the response is not successful or the server cannot classify the image, the response could look like:
        {
            "response": False
        }
        
    Raises:
    -------
    requests.exceptions.RequestException
        This exception is raised for network-related errors, such as failed connections or timeouts.
    
    Notes:
    -----
    The server is expected to have an endpoint `/classify` that accepts a POST request containing the JSON 
    payload described above. The server must handle HTTP Basic Authentication and perform classification 
    of the image based on the provided data.
    
    Example Usage:
    --------------
    ```python
    base_url = "http://localhost:44444"
    user_data = {
        "user": "my_username",
        "password": "my_password"
    }
    image_data = {
        "dataset_name": "animals",
        "base_dir": "/some/path/of/datasets",
        "filepath": "animals/cute/cat.png",
        "label": "cat"
    }
    
    response = classify_sample(base_url, user_data, image_data)
    print(response)  # Example: {'response': True}
    ```
    """
    response = requests.post(f"{base_url}/classify", json={
        "dataset_name": image_data["dataset_name"],
        "base_dir": image_data["base_dir"],
        "filepath": image_data["filepath"],
        "label": image_data["label"]
    }, auth=HTTPBasicAuth(user_data["user"],user_data["password"]))
    return response.json()

################################################################################

def main():
    EXAMPLE_USE='''
Example of use:

image-label-client -u MYUSER -p MYPASSWORD -b "http://127.0.0.1:44444" -d DATASET_NAME size

image-label-client -u MYUSER -p MYPASSWORD -b "http://127.0.0.1:44444" -d DATASET_NAME obtain --id 0

image-label-client -u MYUSER -p MYPASSWORD -b "http://127.0.0.1:44444" -d DATASET_NAME classify --basedir BASEDIR --filepath FILEPATH --label LABEL
    '''
    # Inicializa o parser
    parser = argparse.ArgumentParser(
        description="Client to image-label-server program.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXAMPLE_USE
    )

    # Adiciona os argumentos
    parser.add_argument(
        '-u', '--user', 
        type=str, 
        help='Your user name', 
        required=True
    )
    
    parser.add_argument(
        '-p', '--password', 
        type=str, 
        help='Your password', 
        required=True
    )
  
    parser.add_argument(
        '-b', '--base', 
        type=str, 
        help='Your base url by example http://127.0.0.1:44444', 
        required=True
    )
    
    parser.add_argument(
        '-d', '--dataset', 
        type=str, 
        help='Your dataset name', 
        required=True
    )
    
    # Argumento de subcomando
    subparsers = parser.add_subparsers(title='Commands', dest='command')
    
    # Subcomando size
    size_parser = subparsers.add_parser('size', help='Size of dataset')
    
    # Subcomando obtain
    obtain_parser = subparsers.add_parser('obtain', help='Obtain a sample of dataset')
    obtain_parser.add_argument('-i', '--id', help='ID of sample in the dataset',type=int, default=-1)
    obtain_parser.add_argument('-o', '--outimg', help='Path to save the image obtained from sample in the dataset',type=str, default="outimg.png")
    
    # Subcomando classify
    classify_parser = subparsers.add_parser('classify', help='Classify a sample of dataset')
    classify_parser.add_argument('-a', '--basedir' , help='Base directory of sample in the dataset',type=str, required=True)
    classify_parser.add_argument('-f', '--filepath', help='File path of sample in the dataset',type=str, required=True)
    classify_parser.add_argument('-l', '--label', help='Label of sample in the dataset',type=str, required=True)
    
    ####################################
    # Faz o parsing dos argumentos
    args = parser.parse_args()

    # Lógica para os argumentos
    if args.command == 'size':
        res_json = get_size(args.base, {"user":args.user,"password":args.password}, args.dataset)
        print(res_json)
        
    elif args.command == 'obtain':
        res_img, res_json = obtain_sample(args.base, {"user":args.user,"password":args.password}, args.dataset, args.id)
        print(res_json)
        res_img.save(args.outimg)
        
    elif args.command == 'classify':
        res_json=classify_sample(args.base, {"user":args.user,"password":args.password}, {"dataset_name":args.dataset,"base_dir":args.basedir,"filepath":args.filepath,"label":args.label})
        print(res_json)

if __name__ == "__main__":
    main()

