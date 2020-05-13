#!/bin/sh

MODEM_IP="192.168.8.1"
curl -s -X GET "http://$MODEM_IP/api/webserver/SesTokInfo" > ses_tok.xml
COOKIE=`grep "SessionID=" ses_tok.xml | cut -b 10-147`
TOKEN=`grep "TokInfo" ses_tok.xml | cut -b 10-41`

echo $COOKIE
echo $TOKEN

curl -X POST "http://$MODEM_IP/api/device/control" \
-H "Cookie: $COOKIE" -H "__RequestVerificationToken: $TOKEN" \
-H "Content-Type: text/xml" -d "<request><Control>1</Control></request>" > modem_restart_response.xml

cat modem_restart_response.xml
