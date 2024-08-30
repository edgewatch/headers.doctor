import requests

class HeadersDoctorClient:
    # BASE_URL = "https://api.headers.doctor/api/v1"
    BASE_URL = "http://localhost:8000"
    results = {}

    def __init__(self):
        self.headers = {
            "Accept": "application/json",
        }

    def check_headers(self, url: str):
        try:
            # Send the request and get the request id
            request_response = requests.post(f"{self.BASE_URL}/results/scan-hostname", headers=self.headers, params={"hostname": url})
            request_response.raise_for_status()
            request_id = request_response.json()['scan_id']

            # Get the results using the request id
            loop = True
            while loop:
                response = requests.get(f"{self.BASE_URL}/results/get_result/{request_id}", headers=self.headers)
                response.raise_for_status() 
                response = response.json()
                if isinstance(response, list):
                    response = response[0]
                    if "scan_id" in response:
                        loop = False
                        self.results = response
            return response

        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                return {"error": "Hostname not found"}
            else:
                raise err
    
    def get_results(self):
        return self.results
            
    def check_csp(self, url: str):
        try:
            response = requests.get(f"{self.BASE_URL}/csp", headers=self.headers, params={"url": url})  
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                return {"error": "Hostname not found"}
            else:
                raise err

    def owasp_compliance(self, url: str):
        try:
            response = requests.get(f"{self.BASE_URL}/owasp", headers=self.headers, params={"url": url})
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                return {"error": "Hostname not found"}
            else:
                raise err

test = HeadersDoctorClient()
print(test.check_headers("https://www.google.com"))
# print(test.check_csp("https://www.google.com"))
# print(test.owasp_compliance("https://www.google.com"))

