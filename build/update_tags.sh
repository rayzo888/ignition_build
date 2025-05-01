#!/bin/sh

# Set variables
UPDATE_TAGS_URL="http://liew-home.ddns.net/system/webdev/HomeAutomation/utility/tagControl/updateTags"
TAGFOLDER="/usr/local/bin/ignition/data/tags"
CHECK_GWINFO_URL="http://liew-home.ddns.net/system/gwinfo"

echo "Waiting for Gateway to report RUNNING..."

# Poll until the gateway is fully running
while true; do
  STATUS=$(curl -s "$CHECK_GWINFO_URL")
  echo "$STATUS" | grep -q "ContextStatus=RUNNING"
  if [ $? -eq 0 ]; then
    echo "OK: Gateway is RUNNING. Continuing..."
    break
  else
    echo "Waiting for Gateway status to fully RUNNING..."
    sleep 3
  fi
done

# Post tag folder path
echo "Updating tags from tag folder..."
curl -X POST \
  -H "Accept: application/json" \
  -H "Content-Type: application/json" \
  -d "{\"tagFileFolder\":\"$TAGFOLDER\"}" \
  "$UPDATE_TAGS_URL"

echo "Script completed successfully."
sleep 5
exit 0
