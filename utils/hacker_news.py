import requests
from bs4 import BeautifulSoup as soup
from email.mime.text import MIMEText
from email.mime.multipart import  MIMEMultipart
import smtplib
import datetime as dt
from decouple import config
import os

now = dt.datetime.now()
class HackerNews():
    def __init__(self, url: str):
        self.url = url
        
    def get_headlines(self) -> list:
        with requests.Session() as session:
            response = session.get(self.url).text
            new_soup = soup(response, 'lxml')
            head_table = new_soup.find('table', class_='itemlist')
            list_row = head_table.find_all('tr')
            highlights = []
            for row in list_row:
                
                try:
                    if row.find('td', class_='title'):
                        rank = str(row.find('span', class_='rank').string)
                        title = str(row.find('a', class_='storylink').string)
                        highlights.append([rank, title])
                    
                    elif row.find('td', class_='subtext'):
                        story_points = str(row.find('span', class_='score').string)
                        written_by = str(row.find('a', class_='hnuser').string)
                        a_comm = str(row.find('span')['id']).split('_')[1]
                        comm_value = str(row.find('a', {'href': f'item?id={a_comm}'}).string)
                        highlights.append([story_points, written_by, comm_value])
                        
                    else:
                        continue                    
                    
                except:
                    pass
            
            return highlights

    def get_content(self) -> str:
        info = self.get_headlines()
        # Create the message body
        body = ""
        body +="<p>The current top headlines in Hacker News</p><br>"
        for x in range(len(info)):
            if x%2==0:
                body +="<br>"
                c=0
                for y in info[x]:
                    if c==1:
                        body += f"<strong>{y}</strong>"
                    else:
                        body  +=f"{y}&nbsp;&nbsp;"
                    c+=1
                body+="<br>"
            else:
                for y in info[x]:
                    body += f"{y}&nbsp;&nbsp;"

    
        body+="<br><br><b>Thank you Subscribing to this newsletter!😉</b>"

        return body

    def mail_headlines(self, email: str, passcode: str):
        body = self.get_content()
        message = MIMEMultipart()
        message['Subject'] = f'Top New Stories {now.day}/{now.month}/{now.year}'
        message['From'] = email
        message['To'] = config('EMAIL_1', cast=str)
        message.attach(MIMEText(body, 'html'))
        # initiating the SMTP server
        try:
            SERVER = config('SERVER', cast=str)
            PORT = config('PORT', cast=int)
            server = smtplib.SMTP(SERVER, PORT)
            # Use in development environment only, otherwise not ot be called
            # server.set_debuglevel(1)
            server.ehlo()
            #######
            server.starttls()
            server.login(email, passcode)
            server.sendmail(email, config('EMAIL_1', cast=str), message.as_string())
            print('Email sent')
            # Email sent
            server.close()
        except smtplib.SMTPAuthenticationError as auth:
            print(auth)
            os._exit(1)
        except smtplib.SMTPResponseException as resp:
            print(resp)
            os._exit(1)
        except smtplib.SMTPException as ex:
            print(ex)
            os._exit(1)
        except Exception as e:
            print(e)
            os._exit(1)
