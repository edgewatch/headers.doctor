# scan_headers.py

This script scans websites for security headers and saves the results to a file. It uses the Headers Doctor API ([https://headers.doctor/](https://headers.doctor/)) to perform the scans.

## Features

- Scan a single URL or a list of URLs from a file.
- Specify the port to use for scanning.
- Save the scan results to a JSON file.
- Save temporary files for later retrieval of results.
- Get scan results from previously saved temporary files or by providing a specific UUID.

## Requirements

- Python 3.7 or higher
- requests library

## Installation

1. Install the requests library:

```bash
pip install requests
```

2. Clone the repository or download the `scan_headers.py` file.

## Usage

```bash
python scan_headers.py [OPTIONS]
```
### Options

| Option | Description |
|---|---|
| `-u`, `--scan_by_url` | URL to scan. |
| `-p`, `--port` | Port to use for scanning (default: 443). |
| `-f`, `--file` | File containing a list of URLs to scan. |
| `-s`, `--save_response_to_file` | Directory path to save the scan results to a JSON file. |
| `--save_temp` | Save temporary files for later retrieval of results. |
| `--get_result_from_file` | Get scan results from a file containing a list of UUIDs and ports. |
| `--get_result_from_uuid` | Get the scan result for a specific UUID. |

### Examples

**Scan a single URL and print the results to the console:**

```bash
python scan_headers.py -u https://www.example.com
```

**Scan a list of URLs from a file and save the results to a file:**

```bash
python scan_headers.py -f urls.txt -s results.json
```

**Scan a URL on a specific port:**

```bash
python scan_headers.py -u https://www.example.com -p 8080
```

**Save temporary files and retrieve the results later:**

```bash
python scan_headers.py -u https://www.example.com --save_temp python scan_headers.py --get_result_from_file
```

**Get the scan result for a specific UUID:**

```bash
python scan_headers.py --get_result_from_uuid
```

## Notes

- The script uses asynchronous operations to speed up the scanning process.
- The temporary files are saved in a directory named `temp_<timestamp>`.
- The scan results are saved in JSON format.
- The script logs events to the console and to a file named `scan_headers.log`.

## License

This project is licensed under the terms of the [GNU General Public License (GPL) Version 3](LICENSE).
