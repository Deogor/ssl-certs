import re
import sqlite3
import sys
import ssl
import socket
# connect to base
conn = sqlite3.connect('/tmp/history')
cursor = conn.cursor()
# getting lines by lines starting from the last line up
cursor.execute("SELECT url FROM urls WHERE id=(SELECT max(id) FROM urls);")
taken_url = cursor.fetchall()[0][0]

# regex to find trigger words
overlap = re.findall('https://.*(onl)?.*((sber).*(onl)?.*|(.*(gos).*(uslugi).*))', str(taken_url))
conn.close()
overlap = str(overlap)

# stop program if overlap is empty
if overlap == "[]":
    sys.exit(0)

taken_url_full = taken_url
taken_url = taken_url.replace("https://", "")
taken_url, sep, tail = taken_url.partition('/')

# get cert issuer
hostname = taken_url
ctx = ssl.create_default_context()
with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
    s.connect((hostname, 443))
    cert = s.getpeercert()
subject = dict(x[0] for x in cert['subject'])
issued_to = subject['commonName']
issuer = dict(x[0] for x in cert['issuer'])
issued_by = issuer['commonName']
print(issued_by)
issuer = re.findall('.*(Let\'s Encrypt).*', str(issued_by))

# stop program if issuer is empty
if str(issuer) != "":
    from notifypy import Notify
    notification = Notify()
    notification.title = "ВНИМАНИЕ"
    notification.message = "Этот сайт, возможно, мошеннический. Проверьте URI сайта"
    notification.send()
sys.exit(0)
