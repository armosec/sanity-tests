import requests
import time
import os
import argparse
from datetime import datetime, timedelta, timezone

class ApiTester:
    def __init__(self, env, login_endpoint, email, customer, password, customer_guid):
        self.env = env
        self.base_url, self.headers = self._configure_environment()
        self.login_endpoint = login_endpoint
        self.email = email
        self.customer = customer
        self.password = password
        self.customer_guid = customer_guid
        self.session = requests.Session()
        self.auth_cookie = None
        print(f"Running in '{self.env}' environment.")

    def _configure_environment(self):
        if self.env == "dev":
            base_url = "https://api-dev.armosec.io"
            headers = {
                "Content-Type": "application/json",
                "Origin": "https://cloud-predev.armosec.io",
                "Referer": "https://cloud-predev.armosec.io/"
            }
        else:  # default to production
            base_url = "https://api.armosec.io"
            headers = {
                "Content-Type": "application/json",
                "Origin": "https://cloud.armosec.io",
                "Referer": "https://cloud.armosec.io/"
            }
        return base_url, headers

    def get_current_timestamp(self, format_type="default"):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S" if format_type == "special" else "%Y-%m-%d_%H-%M-%S")

    def login(self):
        url = f"{self.base_url}{self.login_endpoint}"
        payload = {
            "email": self.email,
            "customer": self.customer,
            "password": self.password,
            "customerGUID": self.customer_guid
        }

        start_time = time.time()
        response = self.session.post(url, json=payload, headers=self.headers)
        end_time = time.time()

        response_time = end_time - start_time
        print(f"Login API response time: {response_time:.2f} seconds")
        if response.status_code != 200:
            print(f"Login failed with status code {response.status_code}")
            return False, response_time
        self.auth_cookie = response.cookies.get('auth')
        return True, response_time

    def test_api(self, endpoint, payload, api_name):
        url = f"{self.base_url}{endpoint}?customerGUID={self.customer_guid}"
        headers = self.headers.copy()
        headers["Cookie"] = f"auth={self.auth_cookie}" if self.auth_cookie else ""

        start_time = time.time()
        response = self.session.post(url, json=payload, headers=headers)
        end_time = time.time()

        response_time = end_time - start_time
        print(f"{api_name} API response time: {response_time:.2f} seconds")
        if response.status_code != 200:
            print(f"{api_name} request failed with status code {response.status_code}")
            print("Response content:", response.content)
            return response_time
        return response_time

    def cve_view_no_filter(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "cvssInfo.baseScore:desc,name:desc",
            "innerFilters": []
        }
        return self.test_api("/api/v1/vulnerability_v2/vulnerability/list", payload, "cve_view_no_filter")
    
    def cve_view_with_severity(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "cvssInfo.baseScore:desc,name:desc",
            "innerFilters": [
                {
                    "severity": "Critical,High,Medium,Low"
                }
            ]
        }
        return self.test_api("/api/v1/vulnerability_v2/vulnerability/list", payload, "cve_view_with_severity")

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
        return self.test_api("/api/v1/vulnerability_v2/vulnerability/list", payload, "cve_view_with_risk_spotlight")

    def workload_view_table_no_filter(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "criticalCount:desc,highCount:desc,mediumCount:desc,lowCount:desc",
            "innerFilters": [{}]
        }
        return self.test_api("/api/v1/vulnerability_v2/workload/list", payload, "workload_view_table_no_filter")

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
        return self.test_api("/api/v1/vulnerability_v2/workload/list", payload, "workload_view_table_with_risk_spotlight")

    def images_view_table_no_filter(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "criticalCount:desc,highCount:desc,mediumCount:desc,lowCount:desc",
            "innerFilters": [{}]
        }
        return self.test_api("/api/v1/vulnerability_v2/image/list", payload, "images_view_table_no_filter")

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
        return self.test_api("/api/v1/vulnerability_v2/image/list", payload, "images_view_table_with_risk_spotlight")

    def sbom_view_table_no_filter(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "criticalCount:desc,highCount:desc,mediumCount:desc,lowCount:desc",
            "innerFilters": [{}]
        }
        return self.test_api("/api/v1/vulnerability_v2/component/list", payload, "sbom_view_table_no_filter")

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
        return self.test_api("/api/v1/vulnerability_v2/component/list", payload, "sbom_view_table_with_risk_spotlight")

    def attackchains(self):
        payload = {
            "pageSize": 50,
            "pageNum": 1,
            "orderBy": "timestamp:desc,viewedMainScreen:desc",
            "innerFilters": [{}]
        }
        return self.test_api("/api/v1/attackchains", payload, "attackchains")

    def vulnerability_overtime(self):
        until_date = datetime.now(timezone.utc)
        since_date = until_date - timedelta(days=30)

        until_str = until_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        since_str = since_date.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

        payload = {
            "since": since_str,
            "until": until_str,
            "innerFilters": [{}]
        }
        return self.test_api("/api/v1/vulnerability_v2/vulnerability/overtime", payload, "vulnerability_overtime")

    def save_to_csv(self, log_data, file_name):
        all_keys = [
            'timestamp',
            'login_time',
            'cve_view_no_filter',
            'cve_view_with_risk_spotlight',
            'workload_view_table_no_filter',
            'workload_view_table_with_risk_spotlight',
            'images_view_table_no_filter',
            'images_view_table_with_risk_spotlight',
            'sbom_view_table_no_filter',
            'sbom_view_table_with_risk_spotlight',
            'attackchains',
            'vulnerability_overtime',
            'cve_view_with_severity'
        ]

        file_exists = os.path.isfile(file_name)
        
        if file_exists:
            # Align existing rows with the new column structure
            with open(file_name, 'r') as f:
                lines = [line.strip() for line in f]
            header = lines[0].split(',')
            missing_columns = len(all_keys) - len(header)

            if missing_columns > 0:
                # Add missing columns to the header
                updated_header = header + all_keys[len(header):]
                updated_lines = [','.join(updated_header)]

                # Add `0` for missing columns to existing rows
                for line in lines[1:]:
                    row = line.split(',')
                    updated_row = row + ['0'] * missing_columns
                    updated_lines.append(','.join(updated_row))

                # Write updated lines back to the file
                with open(file_name, 'w') as f:
                    f.write('\n'.join(updated_lines) + '\n')

        # Write new log entry
        with open(file_name, 'a') as f:
            if not file_exists:
                f.write(','.join(all_keys) + '\n')  # Write header for new file
            f.write(','.join(str(log_data.get(key, '0')) for key in all_keys) + '\n')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run API tests with provided credentials.')
    parser.add_argument('--env', choices=['dev', 'prod'], default='prod', help='Environment to run the API tests (default: prod)')
    parser.add_argument('--email', required=True, help='Your email address')
    parser.add_argument('--customer', required=True, help='Your customer name')
    parser.add_argument('--password', required=True, help='Your password')
    parser.add_argument('--customer_guid', required=True, help='Your customer GUID')
    parser.add_argument('--log_name', required=True, help='Descriptive name for the log file')

    args = parser.parse_args()

    api_tester = ApiTester(
        env=args.env,
        login_endpoint="/login",
        email=args.email,
        customer=args.customer,
        password=args.password,
        customer_guid=args.customer_guid
    )

    login_successful, login_time = api_tester.login()
    if login_successful:
        print("Logged in successfully!")
        cve_view_no_filter_time = api_tester.cve_view_no_filter()
        cve_view_with_risk_spotlight_time = api_tester.cve_view_with_risk_spotlight()
        workload_view_table_no_filter_time = api_tester.workload_view_table_no_filter()
        workload_view_table_with_risk_spotlight_time = api_tester.workload_view_table_with_risk_spotlight()
        images_view_table_no_filter_time = api_tester.images_view_table_no_filter()
        images_view_table_with_risk_spotlight_time = api_tester.images_view_table_with_risk_spotlight()
        # sbom_view_table_no_filter_time = api_tester.sbom_view_table_no_filter()
        # sbom_view_table_with_risk_spotlight_time = api_tester.sbom_view_table_with_risk_spotlight()
        attackchains_time = api_tester.attackchains()
        vulnerability_overtime_time = api_tester.vulnerability_overtime()
        cve_view_with_severity_time = api_tester.cve_view_with_severity()

        log_data = {
            'timestamp': api_tester.get_current_timestamp("special"),
            'login_time': f"{float(login_time):.2f}",
            'cve_view_no_filter': f"{float(cve_view_no_filter_time):.2f}",
            'cve_view_with_risk_spotlight': f"{float(cve_view_with_risk_spotlight_time):.2f}",
            'workload_view_table_no_filter': f"{float(workload_view_table_no_filter_time):.2f}",
            'workload_view_table_with_risk_spotlight': f"{float(workload_view_table_with_risk_spotlight_time):.2f}",
            'images_view_table_no_filter': f"{float(images_view_table_no_filter_time):.2f}",
            'images_view_table_with_risk_spotlight': f"{float(images_view_table_with_risk_spotlight_time):.2f}",
            'sbom_view_table_no_filter': 0,
            'sbom_view_table_with_risk_spotlight': 0,
            'attackchains': f"{float(attackchains_time):.2f}",
            'vulnerability_overtime': f"{float(vulnerability_overtime_time):.2f}",
            'cve_view_with_severity': f"{float(cve_view_with_severity_time):.2f}",
            
        }

    log_file = f"./logs/api_test_log_{args.log_name}.csv"
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    api_tester.save_to_csv(log_data, log_file)