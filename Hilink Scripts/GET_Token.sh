#!/bin/sh

MODEM_IP = "192.168.8.1"
curl - s - X GET "http://$MODEM_IP/api/webserver/SesTokInfo" > ses_tok.xml
COOKIE =`grep "SessionID=" ses_tok.xml | cut - b 10 - 147`
TOKEN =`grep "TokInfo" ses_tok.xml | cut - b 10 - 41`
LOGIN_REQ = '<request><Username>admin</Username><Password>PenguinParty$19</Password><password_type>3</password_type></request>'

curl - X POST - d $LOGIN_REQ "http://$MODEM_IP/api/user/login" \
- c $COOKIE - -header "__RequestVerificationToken: $TOKEN" \
- -header "Content-Type: text/xml" - -dump - header login_resp_hdr.txt > /dev/null

grep "SessionID=" login_resp_hdr.txt | cut - d ':' - f2 | cut - d ';' - f1 > session_id.txt
grep "__RequestVerificationTokenone" login_resp_hdr.txt | cut - d ':' - f2 > token.txt

SESSION_ID =`cat session_id.txt`
TOKEN =`cat token.txt`

echo "admin session_id\n$SESSION_ID\n"
echo "$TOKEN\n"
