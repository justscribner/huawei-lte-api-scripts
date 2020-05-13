#!/bin/sh

MODEM_IP="192.168.8.1"
curl -s -S -X GET "http://$MODEM_IP/api/webserver/SesTokInfo" > ses_tok.xml
COOKIE=`grep "SessionID=" ses_tok.xml | cut -b 10-147`
TOKEN=`grep "TokInfo" ses_tok.xml | cut -b 10-41`

curl -s -S -X GET "http://$MODEM_IP/api/device/information" \
-H "Cookie: $COOKIE" -H "__RequestVerificationToken: $TOKEN" \
-H "Content-Type: text/xml" > device_info.xml

cat device_info.xml
