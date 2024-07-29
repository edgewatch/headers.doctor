import requests

class HeadersDoctorClient:
    # BASE_URL = "https://api.headers.doctor/api/v1"
    BASE_URL = "http://localhost:8000"

    def __init__(self):
        self.headers = {
            "Accept": "application/json",
        }

    def check_headers(self, url: str):
        try:
            request_id = requests.post(f"{self.BASE_URL}/results/scan-hostname", headers=self.headers, params={"hostname": url})
            request_id = request_id.json()['id_request']
            loop = True
            while loop:
                response = requests.get(f"{self.BASE_URL}/results/get_result/{request_id}", headers=self.headers)
                response = response.json()
                if 'No result founded.' in response['message']:
                    loop=False
                    return response
            return response
        except requests.exceptions.HTTPError as err:
            if err.response.status_code == 404:
                return {"error": "Hostname not found"}
            else:
                raise err

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
print(test.check_csp("https://www.google.com"))
print(test.owasp_compliance("https://www.google.com"))

