import argparse
import json

def fetch_account_ids(env, json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        accounts = data['env'].get(env, [])
        account_ids = [account["accountID"] for account in accounts]
        return account_ids

def main():
    parser = argparse.ArgumentParser(description='Fetch account IDs by environment.')
    parser.add_argument('--environment', type=str, required=True, help='Environment name')
    parser.add_argument('--jsonFile', type=str, required=True, help='Path to JSON file with account data')

    args = parser.parse_args()

    # Fetch account IDs for the specified environment
    account_ids = fetch_account_ids(args.environment, args.jsonFile)

    # Print the account IDs as a JSON string
    print(json.dumps(account_ids))

if __name__ == '__main__':
    main()
