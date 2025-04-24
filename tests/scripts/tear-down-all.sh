#!/usr/bin/env bash

DEPLOY_NAMESPACE="attack-suite"

echo "[+] Deleting namespace $DEPLOY_NAMESPACE"
kubectl delete namespace $DEPLOY_NAMESPACE
if [ $? -ne 0 ]; then
    echo "Failed to delete namespace $DEPLOY_NAMESPACE"
    exit 1
fi

echo "[+] Deleted namespace $DEPLOY_NAMESPACE"

