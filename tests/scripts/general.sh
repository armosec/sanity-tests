#!/usr/bin/env bash

DEPLOY_NAMESPACE="attack-suite"

# Get service urls
echo "[+] Getting service urls"
# Get service URLs and store in map
services_output=$(kubectl get svc -n $DEPLOY_NAMESPACE -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.loadBalancer.ingress[0].ip}{"\t"}{.spec.ports[0].port}{"\n"}{end}')
if [ $? -ne 0 ]; then
    echo "Failed to get service URLs"
    exit 1
fi

declare -A service_map
while IFS=$'\t' read -r name ip port; do
    # Skip if IP is empty or less than 3 items
    if [ "$ip" = "" ] || [ "$port" = "" ]; then
        continue
    fi

    service_map[$name]="$ip:$port"
done <<< "$services_output"

export service_map

if [ "$DEBUG" = "true" ]; then
    # Print service URLs
    echo "[+] Service URLs:"
    for service in "${!service_map[@]}"; do
        echo "$service: http://${service_map[$service]}"
    done
fi
