#!/bin/bash

if [ -z $HOST ] || [ -z $WEBHOOK_URL ]
then
	echo "Add environment variables HOST and WEBHOOK_URL to continue"
	exit 2
fi

SCRIPT_PATH=$(pwd)
response=""

days_left=$(${SCRIPT_PATH}/ssl_checker.py -H ${HOST} -j | jq -r .\"${HOST}\".days_left )
# response=$(printf "${response}\n<br>Host: ${HOST} ${days_left} days left")
if (( $days_left < 10 ))
then
	response=$(printf "${response}\n<br>Found ${HOST} - ${hostip} - $days_left")
fi

if [ "$response" != "" ]
then
       # Convert formating.
	MESSAGE=$( echo ${response} | sed 's/"/\"/g' | sed "s/'/\'/g" )
	JSON="{\"title\": \"SSL Expiration alert\", \"themeColor\": \"0078D7\", \"text\": \"${MESSAGE}\" }"

	# Post to Microsoft Teams.
	/usr/bin/curl -H "Content-Type: application/json" -d "${JSON}" "${WEBHOOK_URL}"
else
    echo "No issues"
fi

exit 0;
