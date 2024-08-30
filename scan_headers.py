import os
import re
import requests
import asyncio

API_HEADERS_DOCTOR = "http://localhost:8000"
# API_HEADERS_DOCTOR = "https://api.dev.headers.doctor"

def save_uuid(uuid: str, port:int):
    try:
        with open("temp/uuids.txt", "a") as f:
            f.write(f"{uuid}:{port}\n")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        
def save_not_valid_url(url: str, port: int):
    try:
        path = "temp/not_valid_urls.txt"
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, "a") as f:
            f.write(f"{url}:{port}\n")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
        
def save_scan_result(response: any, path: str):
    try:
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
            f.write(str(response))
    except ValueError as e:
        print(f"Error: {e}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error: {e}")
            
def write_response(response: any, url: str = '', port: int = 0, path: str = 'scan'):
    if url == '' and port == 0:
        save_scan_result(response, path)
    else:
        if response is not None:
            save_uuid(response['scan_id'], port)
        else:
            save_not_valid_url(url, port)

def scan_url(url, port):
    try:
        response = requests.post(
            f"{API_HEADERS_DOCTOR}/results/scan-hostname",
            headers={"Accept": "application/json"},
            params={
                "hostname": url,
                "port": port
            },
        )
        if response.status_code == 200:
            print(200)
            return response.json()
        else:
            return None
    except requests.exceptions.RequestException:
        return None
    except Exception as e:
        print(f"Error: {e}")
    return None

def validate_hostname(hostname: str) -> bool:
    try:
        pattern = r"(?i)^(?:(?:https?://)?(?:([a-z0-9-]+|\*)\.)?([a-z0-9-]{1,61})\.([a-z0-9]{2,7}))?$"
        return bool(re.match(pattern, hostname))
    except Exception as e:
        print(f"Error: {e}")
    return False

def format_url(url: str, port: int = 443):
    try:
        if not validate_hostname(url):
            raise ValueError("Invalid URL")
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
        print(f"Error: {e}")

async def scan_file(file_path: str, port: int = None):
    # Almacenar temporalmente los uuids en un archivo
    # Almacenar temporalmente las urls que no funcionan en otro archiv
    def in_case_no_port(url:str):
        if ":" in url:
            port = int(url.split(":")[1])
            url = url.split(":")[0]
            response, _ = format_url(url, port)
            write_response(response, url, port)                
                
        elif url.startswith("http://") or url.startswith("https://"):
            response, _port = format_url(url)
            write_response(response, url, _port)
        else:
            port = 443
            response, _ = format_url(url, port)
            if response is not None:
                save_uuid(response['uuid'])
            else:
                port = 80
                response, _ = format_url(url, port)
                write_response(response, url, port)
    
    def with_port(url:str, port:int):
        response, _ = format_url(url, port)
        write_response(response, url, port)
    
    with open(file_path, 'r') as file:
        for line in file:
            url = line.strip()
            if port is None:
                in_case_no_port(url)
            else:
                with_port(url, port)
                
async def get_result(path:str):
    try:
        while True:
            with open("temp/uuids.txt", "r+") as file:
                lines = file.readlines()
                file.truncate(0)
            
            for line in lines:
                line = line.strip()
                uuid = line.split(":")[0]
                port = line.split(":")[1]
                response = requests.get(
                    f"{API_HEADERS_DOCTOR}/results/get_result/{uuid}",
                    headers={"Accept": "application/json"}
                )
                if response.status_code == 200:
                    if response.json() is not None:
                        write_response(response.json(), path=path)
    except ValueError as e:
        print(f"Error: {e}")
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
    return None    
    

def create_temp():
    try:
        if not os.path.exists("temp"):
            os.makedirs("temp")
        return "temp"
    except Exception as e:
        print(f"Error: {e}")

async def main():
    import argparse
    temp_dir = create_temp()
    
    parser = argparse.ArgumentParser(description='Scan a website and save results to file.')
    parser.add_argument('url', type=str, nargs='?', help='URL to scan.')
    parser.add_argument('-p', '--port', type=int, default=443, help='Port (default 443).')
    parser.add_argument('-f', '--file', type=str, help='File with list of urls to scan.')
    parser.add_argument('-s', '--save_response', help='if this param is given, scan_headers will save all the results in your_directory/results/url/url_port.json else it only print the results.')
    args = parser.parse_args()

    print(f"""
        Scanning:
        \tURL: {args.url if args.url else "False"}
        \tPort: {args.port if args.port else "False"}
        \tFile: {args.file if args.file else "False"}
        \tSave response: {args.save_response if args.save_response else "False"}
    """)
    
    try:
        if args.file:
            await asyncio.gather(scan_file(args.file, args.port), get_result(args.save_response))
        elif args.url:
            response = format_url(args.url, args.port)
            if response is not None:
                print(response)
            else:
                print("Invalid URL")
    except KeyboardInterrupt:
        print("\nExiting gracefully")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        try:
            import shutil
            shutil.rmtree(temp_dir)
        except KeyboardInterrupt:
            print("\nExiting gracefully")
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == '__main__':
    asyncio.run(main())
