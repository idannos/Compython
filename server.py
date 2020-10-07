import socket
import select
import sys
import smtplib
import pickle
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
HTTP_FORMATS = ["GET", "POST"]


def valid_http(data):
    """
    :param data:
    :return: if the http is valid and relevant to us.
    """
    temp = data.split(" ")
    if temp[0] in HTTP_FORMATS and "HTTP/1.1" in temp[2]:
        return True
    return False


def focus(data):
    """
    :param data:
    :return: the http format
    """
    temp = data.split(" ")
    if temp[0] == "GET":
        return temp[1]
    elif temp[0] == "POST":
        data = data.split("\r\n\r\n")
        return data[1]


def compile(data):
    """
    :param data:
    :return: the compiled data (or an error)
    """
    orig_stdout = sys.stdout
    f = open('out.txt', 'w')
    sys.stdout = f
    # directing the output to a file instead to its default- in order to save the EXEC output
    try:
        exec (data)
    except:
        return "Error"
    sys.stdout = orig_stdout
    f.close()
    file = open("out.txt", "r").read()
    return file


def clean(data):
    """
    :param data:
    :return: "cleaned" data- now python can understand the data
    """
    data = data.replace("%22", '"', 100)  # we want " instead %22
    data = data.replace("%20", ' ', 100)  # we want space instead %20
    data = data.replace("%3Cbr/%3E","\n",100)
    data = data.replace("<br/>", "\n", 100)
    return data


def send_email(message, email, password,send_to_email, subject):
    """
    :param message: the password to the code together+ link and a little description.
    :param email: a mail that I created for this project- the emails will be sent from this email always,
     so the user wont enter his email
    :param password: the password for the email
    :param send_to_email: the email address we want to send too.
    :param subject: subject of the email message
    :exit: sent or an error message- will appear in the server
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = send_to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        text = msg.as_string()
        server.sendmail(email, send_to_email, text)
        server.quit()
        print "sent email"
    except:
        print "probably not valid email address"


open_client_sockets = []
server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 80))
server_socket.listen(100)
CONST = "idangaming1232"
CONST1 = "robinhood"
CONST2 = "plane727456"
CONST3 = "frommailsection"
CONST5 = "have_update?"
link = "http://idangaming.epizy.com/idan.html"
test = ""
new_data = ""
email = ""  # email to send from
password = ''  # password to the email above
send_to_email = ""  # email to send to
# message = '123'
subject = 'invite to Compython'
pass_and_codes = {}
try:
    with open('filename.pickle', 'rb') as handle:
        pass_and_codes = pickle.load(handle)  # password: code
except:
    pass
code = ""
while True:
    rlist, wlist, xlist = select.select(open_client_sockets+[server_socket], open_client_sockets, [])
    for current_socket in rlist:
        if current_socket is server_socket:
            (new_socket1, address1) = server_socket.accept()
            open_client_sockets.append(new_socket1)

        else:
            data = current_socket.recv(4096)
            if data != "":
                original_data = data
                if valid_http(data):
                    data = focus(data)
                    if data == "/":
                        f = open("website.html", "r")
                        txt = f.read()
                        current_socket.send(txt)
                        f.close()
                    if data == "/favicon.ico":
                        try:
                            with open("plane.jpg", "rb") as image_file:
                                a=image_file.read()
                                current_socket.send(a)
                                image_file.close()
                        except:
                            print "no favicon image in this server"
                    else:
                        data = clean(data)
                        if CONST5 in original_data:  # the user is asking for an update
                            data = data.replace(CONST5, "")
                            try:
                                code = pass_and_codes[data]
                                with open('filename.pickle', 'wb') as handle:
                                    pickle.dump(pass_and_codes, handle, protocol=pickle.HIGHEST_PROTOCOL)
                                current_socket.send("HTTP/1.1 200 Ok\r\n\r\n"+code)
                            except:
                                current_socket.send("HTTP/1.1 200 Ok\r\n\r\n" + "")
                        else:
                            current_socket.send("HTTP/1.1 200 Ok\r\n\r\n" + "")
                        if CONST1 in original_data:  # got new data from first box
                            data=data.replace(CONST1, "")
                            aa = str(compile(data))
                            current_socket.send("HTTP/1.1 200 Ok\r\n\r\n"+aa)
                        if CONST in original_data:  # got new data from the code together box
                            new_data = data.split(CONST)
                            code = new_data[0]
                            password1 = new_data[1]
                            pass_and_codes[password1] = code
                            current_socket.send("HTTP/1.1 200 Ok\r\n\r\n"+code)

                        if CONST2 in original_data:  # the user asked to run the code in the code together
                            data = data.replace(CONST2, "")
                            aa = str(compile(data))
                            current_socket.send("HTTP/1.1 200 Ok\r\n\r\n" + aa)
                        if CONST3 in original_data:  # the user wnts to send an email
                            data = data.split(CONST3)  # [0] is mail. [1] is content
                            content = data[1]  # password for the code segment
                            reciever_mail = data[0]
                            content1 = content + "\nthe password for the compython is above\n"
                            content1 += link
                            message = content1
                            send_email(message, email, password, reciever_mail, subject)

            open_client_sockets.remove(current_socket)
            current_socket.close()
