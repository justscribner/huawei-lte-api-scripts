#!/bin/sh

MODEM_IP="192.168.8.1"
curl -s -S -X GET "http://$MODEM_IP/api/webserver/SesTokInfo" > ses_tok.xml
COOKIE=`grep "SessionID=" ses_tok.xml | cut -b 10-147`
TOKEN=`grep "TokInfo" ses_tok.xml | cut -b 10-41`

curl -s -S -X GET "http://$MODEM_IP/api/monitoring/status" \
-H "Cookie: $COOKIE" -H "__RequestVerificationToken: $TOKEN" \
-H "Content-Type: text/xml" > modem_status.xml

IP=`/home/pi/xgrep.py -m "//WanIPAddress/text()" /home/pi/modem_status.xml`
echo $IP
