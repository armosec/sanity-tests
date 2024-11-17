import requests
import time
import datetime
import csv
import os
import argparse
from datetime import datetime, timedelta, timezone

class ApiTester:
    def __init__(self, base_url, login_endpoint, email, customer, password, customer_guid):
        self.base_url = base_url
        self.login_endpoint = login_endpoint
        self.email = email
        self.customer = customer
        self.password = password
        self.customer_guid = customer_guid
        self.session = requests.Session()
        self.auth_cookie = None
                
    def get_current_timestamp(self, format_type="default"):
        if format_type == "special":
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    def save_to_csv(self, log_data, file_name):
        file_exists = os.path.isfile(file_name)
        with open(file_name, "a") as f:
            if not file_exists:
                f.write(','.join(log_data.keys()) + '\n')  # write header if file doesn't exist
            f.write(','.join(str(log_data[key]) for key in log_data) + '\n')  # write log data

    def login(self):
        url = f"{self.base_url}{self.login_endpoint}"
        payload = {
            "email": self.email,
            "customer": self.customer,
            "password": self.password,
            "customerGUID": self.customer_guid
        }
        headers = {
            "Content-Type": "application/json",
            "Origin": "https://cloud.armosec.io",
            "Referer": "https://cloud.armosec.io/"
        }
        start_time = time.time()
        response = self.session.post(url, json=payload, headers=headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"Login API response time: {response_time:.2f} seconds")
        # print(f"Login response status code: {response.status_code}")
        if response.status_code != 200:
            print(f"Login failed with status code {response.status_code}")
            return False, response_time
        # print(f"Logged in successfully in {response_time:.2f} seconds!")
        self.auth_cookie = response.cookies.get('auth')  # Extract the 'auth' cookie
        # print("Auth cookie:", self.auth_cookie)
        return True, response_time

    def test_api(self, endpoint, payload, api_name, customer_guid=None):
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "accept": "application/json",
            "Origin": "https://cloud.armosec.io",
            "Referer": "https://cloud.armosec.io/",
            "x-requested-with": "XMLHttpRequest",
            "Cookie": f"auth={self.auth_cookie}"
        }
        if customer_guid:
            url += f"?customerGUID={customer_guid}"
        
        start_time = time.time()
        response = self.session.post(url, json=payload, headers=headers)
        end_time = time.time()
        
        response_time = end_time - start_time
        print(f"{api_name} API response time: {response_time:.2f} seconds")
        if response.status_code != 200:
            print(f"{api_name} request failed with status code {response.status_code}")
            print("Response content:", response.content)
            return response_time
        else:
            try:
                response.json()
            except ValueError:
                print("Failed to parse JSON response")
                print("Response content:", response.content)
        return response_time

    def cve_view_no_filter(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "cvssInfo.baseScore:desc,name:desc",
            "innerFilters": []
        }
        return self.test_api("/api/v1/vulnerability_v2/vulnerability/list", payload, "cve_view_no_filter", self.customer_guid)

    def cve_view_with_risk_spotlight(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "cvssInfo.baseScore:desc,name:desc",
            "innerFilters": [
                {
                    "riskFactors": "External facing",
                    "isRelevant": "Yes",
                    "isFixed": "true",
                    "exploitable": "Known Exploited,High Likelihood",
                    "severity": "Critical,High"
                }
            ]
        }
        return self.test_api("/api/v1/vulnerability_v2/vulnerability/list", payload, "cve_view_with_risk_spotlight", self.customer_guid)


    def workload_view_table_no_filter(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "criticalCount:desc,highCount:desc,mediumCount:desc,lowCount:desc",
            "innerFilters": [{}]
        }
        return self.test_api("/api/v1/vulnerability_v2/workload/list", payload, "workload_view_table_no_filter", self.customer_guid)
    
    def workload_view_table_with_risk_spotlight(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "criticalCount:desc,highCount:desc,mediumCount:desc,lowCount:desc",
            "innerFilters": [
                {
                    "riskFactors": "External facing",
                    "isRelevant": "Yes",
                    "isFixed": "true",
                    "exploitable": "Known Exploited,High Likelihood",
                    "severity": "Critical,High"
                }
            ]
        }
        return self.test_api("/api/v1/vulnerability_v2/workload/list", payload, "workload_view_table_with_risk_spotlight", self.customer_guid)
    
    def images_view_table_no_filter(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "criticalCount:desc,highCount:desc,mediumCount:desc,lowCount:desc",
            "innerFilters": [{}]
        }
        return self.test_api("/api/v1/vulnerability_v2/image/list", payload, "images_view_table_no_filter", self.customer_guid)
    
    def images_view_table_with_risk_spotlight(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "criticalCount:desc,highCount:desc,mediumCount:desc,lowCount:desc",
            "innerFilters": [
                {
                    "riskFactors": "External facing",
                    "isRelevant": "Yes",
                    "isFixed": "true",
                    "exploitable": "Known Exploited,High Likelihood",
                    "severity": "Critical,High"
                }
            ]
        }
        return self.test_api("/api/v1/vulnerability_v2/image/list", payload, "images_view_table_with_risk_spotlight", self.customer_guid)

    def sbom_view_table_no_filter(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "criticalCount:desc,highCount:desc,mediumCount:desc,lowCount:desc",
            "innerFilters": [{}]
        }
        return self.test_api("/api/v1/vulnerability_v2/component/list", payload, "sbom_view_table_no_filter", self.customer_guid)
    
    def sbom_view_table_with_risk_spotlight(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "since": "2024-08-01T22:25:58.362Z",
            "orderBy": "criticalCount:desc,highCount:desc,mediumCount:desc,lowCount:desc",
            "innerFilters": [
                {
                    "riskFactors": "External facing",
                    "isRelevant": "Yes",
                    "isFixed": "true",
                    "exploitable": "Known Exploited,High Likelihood",
                    "severity": "Critical,High"
                }
            ]
        }
        return self.test_api("/api/v1/vulnerability_v2/component/list", payload, "sbom_view_table_with_risk_spotlight", self.customer_guid)
    
    def attackchains(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "timestamp:desc,viewedMainScreen:desc",
            "innerFilters": [{}]
        }
        return self.test_api("/api/v1/attackchains", payload, "attackchains", self.customer_guid)
    
    def vulnerability_overtime(self):
        # Calculate the current date and the date 30 days ago with timezone awareness
        until_date = datetime.now(timezone.utc)
        since_date = until_date - timedelta(days=30)
        
        # Format the dates to include milliseconds
        until_str = until_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        since_str = since_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
        payload = {
            "since": since_str,
            "until": until_str,
            "innerFilters": [{}]
        }
        response_time = self.test_api("/api/v1/vulnerability_v2/vulnerability/overtime", payload, "vulnerability_overtime", self.customer_guid)
        return response_time
        


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run API tests with provided credentials.')
    parser.add_argument('--email', required=True, help='Your email address')
    parser.add_argument('--customer', required=True, help='Your customer name')
    parser.add_argument('--password', required=True, help='Your password')
    parser.add_argument('--customer_guid', required=True, help='Your customer GUID')
    parser.add_argument('--log_name', required=True, help='Descriptive name for the log file')

    args = parser.parse_args()

    base_url = "https://api.armosec.io"
    login_endpoint = "/login"
    email = args.email
    customer = args.customer
    password = args.password
    customer_guid = args.customer_guid
    log_name = args.log_name
    
    log_file = f"./logs/api_test_log_{log_name}.csv"

    api_tester = ApiTester(base_url, login_endpoint, email, customer, password, customer_guid)
    print("Timestamp:", api_tester.get_current_timestamp())
    login_successful, login_time = api_tester.login()
    if login_successful:
        cve_view_no_filter_time = api_tester.cve_view_no_filter()
        cve_view_with_risk_spotlight_time = api_tester.cve_view_with_risk_spotlight()
        workload_view_table_no_filter_time = api_tester.workload_view_table_no_filter()
        workload_view_table_with_risk_spotlight_time = api_tester.workload_view_table_with_risk_spotlight()
        images_view_table_no_filter_time = api_tester.images_view_table_no_filter()
        images_view_table_with_risk_spotlight_time = api_tester.images_view_table_with_risk_spotlight()
        sbom_view_table_no_filter_time = api_tester.sbom_view_table_no_filter()
        # sbom_view_table_with_risk_spotlight_time = api_tester.sbom_view_table_with_risk_spotlight()
        attackchains_time = api_tester.attackchains()
        vulnerability_overtime_time = api_tester.vulnerability_overtime()
        

        log_data = {
            'timestamp': api_tester.get_current_timestamp("special"),
            'login_time': f"{float(login_time):.2f}",
            'cve_view_no_filter': f"{float(cve_view_no_filter_time):.2f}",
            'cve_view_with_risk_spotlight': f"{float(cve_view_with_risk_spotlight_time):.2f}",
            'workload_view_table_no_filter': f"{float(workload_view_table_no_filter_time):.2f}",
            'workload_view_table_with_risk_spotlight': f"{float(workload_view_table_with_risk_spotlight_time):.2f}",
            'images_view_table_no_filter': f"{float(images_view_table_no_filter_time):.2f}",
            'images_view_table_with_risk_spotlight': f"{float(images_view_table_with_risk_spotlight_time):.2f}",
            'sbom_view_table_no_filter': f"{float(sbom_view_table_no_filter_time):.2f}",
            # 'sbom_view_table_with_risk_spotlight': f"{float(sbom_view_table_with_risk_spotlight_time):.2f}",
            'sbom_view_table_with_risk_spotlight': 0,
            'attackchains': f"{float(attackchains_time):.2f}",
            'vulnerability_overtime': f"{float(vulnerability_overtime_time):.2f}"
        }

        api_tester.save_to_csv(log_data, log_file)