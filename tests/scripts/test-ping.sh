#!/usr/bin/env bash

source "$(dirname "$0")/general.sh"

echo "[+] Testing ping on ${service_map[ping-app]}"

echo "[+] Trying to ping 8.8.8.8"
output=$(curl -s "http://${service_map[ping-app]}/ping.php?ip=8.8.8.8")
if [ $? -ne 0 ]; then
    echo "[-] Failed to ping 8.8.8.8"
    exit 1
fi

if echo "$output" | grep -q "ping"; then
    echo "[+] Ping 8.8.8.8 executed successfully"
else
    echo "[-] Ping 8.8.8.8 failed"
fi


