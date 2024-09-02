import datetime
import os
import re
import requests
import asyncio
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# create a file handler which logs even debug messages
fh = logging.FileHandler('scan_headers.log')
fh.setLevel(logging.DEBUG)

# create a console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

# create a formatter and set the formatter for the handlers
formatter = logging.Formatter('LEVEL: %(levelname)s %(asctime)s %(funcName)s %(message)s', datefmt='%d-%b-%Y %H:%M:%S')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

# API_HEADERS_DOCTOR = "http://localhost:8000"
API_HEADERS_DOCTOR = "https://api.dev.headers.doctor"

def save_uuid(uuid: str, port:int, temp: str):
    """
    Saves a given UUID and port to a file named 'uuids.txt' in the 'temp' directory.

    Args:
        uuid (str): The UUID to be saved.
        port (int): The port associated with the UUID.

    Returns:
        None
    """
    try:
        logger = logging.getLogger(__name__)
        with open(f"{temp}/uuids.txt", "a") as f:
            f.write(f"{uuid}:{port}\n")
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        
def save_not_valid_url(url: str, port: int, temp: str):
    """
    Saves a given URL and port to a file named 'not_valid_urls.txt' in the 'temp' directory.

    Args:
        url (str): The URL to be saved.
        port (int): The port associated with the URL.

    Returns:
        None
    """
    try:
        logger = logging.getLogger(__name__)
        path = f"{temp}/not_valid_urls.txt"
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, "a") as f:
            f.write(f"{url}:{port}\n")
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
        
def save_scan_result(response: any, path: str):
    """
    Saves a given response to a JSON file in the given path.

    Args:
        response (any): The response to be saved.
        path (str): The path to the directory where the file will be saved.

    Returns:
        None
    """
    try:
        logger = logging.getLogger(__name__)
        response = response[0]
        url = response['url']
        port = response['port']
        date_time = response['date']
        
        # if not os.path.exists(path):
        directory = os.path.join(path, f"{url}_{port}")
        os.makedirs(directory, exist_ok=True)
            
            # raise ValueError(f"Path {path} does not exist")
        
        file_path = os.path.join(directory, f"{date_time}.json")
        
        with open(file_path, "w") as f:
            import json
            json.dump(response, f, indent=4)
    except ValueError as e:
        logger.error(f"Error: {e}")
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")
            
def write_response(response: any, temp: str, url: str = '', port: int = 0, path: str = 'scan'):
    """
    Writes a response to a file based on the provided parameters.

    Args:
        response (any): The response to be written.
        url (str): The URL associated with the response. Defaults to an empty string.
        port (int): The port associated with the URL. Defaults to 0.
        path (str): The path to the directory where the file will be saved. Defaults to 'scan'.

    Returns:
        None
    """
    if url == '' and port == 0:
        save_scan_result(response, path)
    else:
        if response is not None:
            save_uuid(response['scan_id'], port, temp)
        else:
            save_not_valid_url(url, port, temp)

def scan_url(url, port):
    """
    Scans a given URL and port and returns the result.

    Args:
        url (str): The URL to be scanned.
        port (int): The port associated with the URL.

    Returns:
        dict: The result of the scan.
    """
    try:
        logger = logging.getLogger(__name__)
        response = requests.post(
            f"{API_HEADERS_DOCTOR}/results/scan-hostname",
            headers={"Accept": "application/json"},
            params={
                "hostname": url,
                "port": port
            },
        )
        if response.status_code == 200:
            logger.info(f"Scan finished for {url}:{port}")
            return response.json()
        else:
            logger.error(f"Error scanning {url}:{port}. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error scanning {url}:{port}. Request exception: {e}")
        return None
    except Exception as e:
        logger.error(f"(scan_url) Error: {e}")
    return None

def validate_hostname(hostname: str) -> bool:
    """
    Validates a given hostname.

    Args:
        hostname (str): The hostname to be validated.

    Returns:
        bool: True if the hostname is valid, False otherwise.
    """
    try:
        logger = logging.getLogger(__name__)
        pattern = r"(?i)^(?:(?:https?://)?(?:([a-z0-9-]+|\*)\.)?([a-z0-9-]{1,61})\.([a-z0-9]{2,7}))?$"
        return bool(re.match(pattern, hostname))
    except Exception as e:
        logger.error(f"(validate_hostname) Error: {e}")
    return False
def format_url(url: str, port: int = 443) -> tuple[dict, int] | None:
    """
    Formats a given URL and port and returns the result of scanning the URL.

    Args:
        url (str): The URL to be formatted.
        port (int): The port associated with the URL. Defaults to 443.

    Returns:
        tuple[dict, int] | None: A tuple containing the result of the scan and the port.
            If the URL is invalid, returns None.
    """
    try:
        logger = logging.getLogger(__name__)
        if not validate_hostname(url):
            logger.error("Error: Invalid URL")
            return None
        if url.endswith('/'):
                url = url[:-1]

        if url.startswith("http://"):
            port = 80
            url = url.replace("http://", "")
        
        if url.startswith("https://"):
            port = 443
            url = url.replace("https://", "")
        
        return scan_url(url, port), port
        
    except ValueError as e:
        logger.error(f"Error: {e}")

async def scan_file(file_path: str, temp:str, port: int = None):
    """
    Scans a given file and writes the results to a file or saves them in a temporary file.

    Args:
        file_path (str): The path to the file to be scanned.
        port (int): The port associated with the URL. Defaults to None.

    Returns:
        None
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Scanning file {file_path}")
    # Almacenar temporalmente los uuids en un archivo
    # Almacenar temporalmente las urls que no funcionan en otro archiv
    def in_case_no_port(url: str):
        """
        Scans a given URL without a port and writes the result to a file or saves it in a temporary file.

        Args:
            url (str): The URL to be scanned.

        Returns:
            None
        """
        logger.info(f"Scanning {url}")
        if ":" in url:
            port = int(url.split(":")[1])
            url = url.split(":")[0]
            response, _ = format_url(url, port)
            write_response(response, temp, url, port)                
                
        elif url.startswith("http://") or url.startswith("https://"):
            response, _port = format_url(url)
            write_response(response, temp, url, _port)
        else:
            port = 443
            response, _ = format_url(url, port)
            if response is not None:
                save_uuid(response['uuid'])
            else:
                port = 80
                response, _ = format_url(url, port)
                write_response(response, temp, url, port)
    
    def with_port(url:str, port:int):
        """
        Scans a given URL with a port and writes the result to a file or saves it in a temporary file.
        
        Args:
            url (str): The URL to be scanned.
            port (int): The port associated with the URL.
        
        Returns:
            None
        """
        response, _ = format_url(url, port)
        write_response(response, temp, url, port)
    
    with open(file_path, 'r') as file:
        for line in file:
            url = line.strip()
            if port is None:
                in_case_no_port(url)
            else:
                with_port(url, port)
                
async def get_result(path: str=None, uuid: str=None, temp: str=None) -> None:
    """
    Gets the result of a scan from the API.

    Args:
        path (str): The path to the directory where the result will be saved.
        uuid (str): The UUID of the scan. If not provided, the function will
            get the UUIDs from the file 'temp/uuids.txt' and get the results
            for all of them.
        save (bool): If True, the result will be saved to a file in the
            given path. Defaults to False.

    Returns:
        None
    """
    try:
        logger = logging.getLogger(__name__)
        response = None
        if uuid:
            while response is None:
                response = requests.get(
                    f"{API_HEADERS_DOCTOR}/results/get_result/{uuid}",
                    headers={"Accept": "application/json"}
                )
                if response.status_code == 200:
                    if response.json():
                        if path:
                            write_response(response.json(), temp=temp, path=path)
                        else:
                            print(response.json())
                    else:
                        response = None
        else:
            with open(f"{temp}/uuids.txt", "r+") as file:
                lines = file.readlines()
                for line in lines:
                    are_results_ready = True
                    line = line.strip()
                    uuid = line.split(":")[0]
                    port = line.split(":")[1]

                    while are_results_ready:
                        response = requests.get(
                            f"{API_HEADERS_DOCTOR}/results/get_result/{uuid}",
                            headers={"Accept": "application/json"}
                        )
                        if response.status_code == 200:
                            if response.json():
                                if path:
                                    write_response(response.json(), temp=temp, path=path)
                                    are_results_ready = False
                                else:
                                    print(response.json())
                                    are_results_ready = False
                            else:
                                are_results_ready = True
                        else:
                            are_results_ready = False
                            
        # while True:
    except ValueError as e:
        logger.error(f"Error: {e}")
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error: {e}")
        return None
    except Exception as e:
        logger.error(f"Error: {e}")
    return None
    
def create_temp():
    """
    Creates a directory named 'temp' if it does not exist.

    Returns:
        str: The path to the 'temp' directory.
    """
    logger = logging.getLogger(__name__)
    try:
        logger = logging.getLogger(__name__)
        today = datetime.datetime.now()
        date_string = today.strftime('%Y-%m-%dT%H:%M:%S')
        if not os.path.exists(f"temp_{date_string}"):
            os.makedirs(f"temp_{date_string}")
        return f"temp_{date_string}"
    except Exception as e:
        logger.error(f"Error: {e}")

async def main():
    """
    This is the main function of the scan_headers script. It is an asynchronous function that 
    scans a website and saves the results to a file. It uses the argparse library to parse 
    command line arguments.

    The function takes no parameters and returns no value. It uses the following command line 
    arguments:

    - scan_by_url: The URL to scan. This is a required argument.
    - port: The port to use when scanning the URL. This is an optional argument with a default 
      value of 443.
    - file: A file containing a list of URLs to scan. This is an optional argument.
    - save_response_to_file: If this argument is given, the script will save the results to a file.
    - save_temp: If this argument is given, the script will save the temporary files.
    - get_result_from_file: If this argument is given, the script will get the results from a file.
    - get_result_from_uuid: If this argument is given, the script will get the result from a UUID.

    The function prints the results of the scan to the console and saves them to a file if 
    requested. It also handles exceptions and cleans up temporary files.
    """
    import argparse
    temp_dir = create_temp()
    
    parser = argparse.ArgumentParser(description='Scan a website and save results to file.')
    parser.add_argument('-u', '--scan_by_url', type=str, nargs='?', help='URL to scan.', required=False)
    parser.add_argument('-p', '--port', type=int, default=443, help='Port (default 443).', required=False)
    parser.add_argument('-f', '--file', type=str, help='File with list of urls to scan.', required=False)
    parser.add_argument('-s', '--save_response_to_file', help='if this param is given, scan_headers will save all the results in your_directory/results/url/url_port.json else it only print the results.', required=False)
    parser.add_argument('--save_temp', action='store_true', help='if this param is given, scan_headers will save all the temp files.', required=False)
    parser.add_argument('--get_result_from_file', action='store_true', help='if this param is given, scan_headers will get all the results from temp/uuids.txt', required=False)
    parser.add_argument('--get_result_from_uuid', type=str, help='if this param is given, scan_headers will get the result from the uuid given.', required=False)
    args = parser.parse_args()

    print(f"""
        Scanning:
        \tURL: {args.scan_by_url if args.scan_by_url else "False"}
        \tPort: {args.port if args.port else "False"}
        \tFile: {args.file if args.file else "False"}
        \tSave response: {args.save_response_to_file if args.save_response_to_file else "False"}
        \tSave temp: {args.save_temp if args.save_temp else "False"}
        \tGet result from file: {args.get_result_from_file if args.get_result_from_file else "False"}
        \tGet result from uuid: {args.get_result_from_uuid if args.get_result_from_uuid else "False"}
    """)
    
    try:
        logger = logging.getLogger(__name__)
        
        if args.scan_by_url:
            response = format_url(args.scan_by_url, args.port)
            if response is not None:
                await get_result(uuid=response[0]['scan_id'], path=args.save_response_to_file, temp=temp_dir)
            else:
                logger.warning("Invalid URL")
                
        elif args.file:
            await asyncio.gather(scan_file(args.file, temp_dir, args.port), get_result(path=args.save_response_to_file, temp=temp_dir))
        
        if args.get_result_from_file:
            if args.save_response_to_file:
                await asyncio.gather(get_result(uuid=args.get_result_from_file, path=args.save_response_to_file, temp=temp_dir))
            else:
                await asyncio.gather(get_result(uuid=args.get_result_from_uuid))
        elif args.get_result_from_uuid:
            if args.save_response_to_file:
                await asyncio.gather(get_result(uuid=args.get_result_from_uuid, path=args.save_response_to_file, temp=temp_dir))
            else:
                await asyncio.gather(get_result(uuid=args.get_result_from_uuid))
            
    except KeyboardInterrupt:
        logger.info("Exiting gracefully")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        try:
            logger = logging.getLogger(__name__)
            if not args.save_temp:
                import shutil
                shutil.rmtree(temp_dir)
        except KeyboardInterrupt:
            logger.info("Exiting gracefully")
        except Exception as e:
            logger.error(f"Error: {e}")


if __name__ == '__main__':
    asyncio.run(main())
