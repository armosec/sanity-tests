#!/usr/bin/env bash

echo "[+] Updating node-agent learning periods"

helm upgrade kubescape kubescape/kubescape-operator -n kubescape --reuse-values --set nodeAgent.config.learningPeriod=1m \
        --set nodeAgent.config.updatePeriod=1m \
        --set nodeAgent.config.maxLearningPeriod=3m 

echo "[+] Deploying clean pod"

kubectl apply -f ./supplychain_deployments/clean.yml

echo "[+] Waiting for 5 minutes"

sleep 300

echo "[+] Deploying supplychain attack"

kubectl apply -f ./supplychain_deployments/malicious.yml

sleep 300

echo "[+] Waiting for 5 minutes"

echo "[+] Please take a look at ARMO UI for the attack"
