#!/usr/bin/env bash

DEPLOY_NAMESPACE="attack-suite"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DEPLOY_FILE="$SCRIPT_DIR/deploy-all.yaml"

echo "[+] Script directory: $SCRIPT_DIR"

echo "[+] Creating namespace $DEPLOY_NAMESPACE"
kubectl create namespace $DEPLOY_NAMESPACE
if [ $? -ne 0 ]; then
    echo "Failed to create namespace $DEPLOY_NAMESPACE"
    exit 1
fi

echo "[+] Applying $DEPLOY_FILE"
kubectl apply -f $DEPLOY_FILE -n $DEPLOY_NAMESPACE
if [ $? -ne 0 ]; then
    echo "Failed to apply $DEPLOY_FILE"
    exit 1
fi

# Wait for all pods to be ready
echo "[+] Waiting for all pods to be running..."
kubectl wait --for=condition=ready pod --all -n $DEPLOY_NAMESPACE --timeout=300s
if [ $? -ne 0 ]; then
    echo "Some pods failed to reach running state within timeout"
    kubectl get pods -n $DEPLOY_NAMESPACE
    exit 1
fi

# Double check pod status
echo "[+] Verifying pod status..."
if [ "$(kubectl get pods -n $DEPLOY_NAMESPACE -o jsonpath='{.items[*].status.phase}' | tr ' ' '\n' | sort -u)" != "Running" ]; then
    echo "Not all pods are in Running state"
    kubectl get pods -n $DEPLOY_NAMESPACE
    exit 1
fi


echo "[+] Deployed all resources to namespace $DEPLOY_NAMESPACE"


