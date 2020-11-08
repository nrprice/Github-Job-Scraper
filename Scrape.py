import requests
from bs4 import BeautifulSoup
import re
from login import user, password, address
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# Beautiful soup methods to return job information, and distance values.
URL = "https://www.findapprenticeship.service.gov.uk/apprenticeships?SearchField=All&Keywords=data&Location=NW101NB&WithinDistance=20&ApprenticeshipLevel=All&DisabilityConfidentOnly=false&Latitude=51.554445&Longitude=-0.239707&Hash=-1450857957&SearchMode=Keyword&Category=&LocationType=NonNational&GoogleMapApiKey=AIzaSyAg5lwS3ugdAVGf5gdgNvLe_0-7XcMICIM&sortType=Relevancy&SearchAction=Sort&resultsPerPage=50&pid=012592db-4b5f-4fe1-a65b-5289695ac9b5&DisplayDescription=true&DisplayDistance=true&DisplayClosingDate=true&DisplayStartDate=true&DisplayApprenticeshipLevel=false&DisplayWage=true"
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
results = soup.find(id='pagedList')
wages = soup.find('div', attrs={'class': 'grid-row'})

job_elems = results.find_all('a', class_='vacancy-link')
distance_val = results.find_all('span', id='distance-value')
closing_dates = results.find_all('span', id='closing-date-value')
wage_vals = results.find_all('ul', attrs={'class': 'list sfa-no-margins vacancy-details-list'})

job_file = open('/Users/nathanprice/Dropbox/Python/Job-scraping/jobs.txt', "r")
old_jobs = job_file.read().split(',')
job_file.close()
new_jobs = []


html = '''<html><body>\n'''
plain = ''''''

for job, distance, date, wage in zip(job_elems, distance_val, closing_dates, wage_vals):
    job = str(job).split('"')

    job_title = job[-1][1:-4]

    job_url = 'https://www.findapprenticeship.service.gov.uk' + job[-2]

    distance = re.findall(r'\d+', str (distance))
    distance = ".".join(distance)

    date = str(date)[63:-7]

    wage = str(wage)

    try:
        wage = wage[wage.index("£"):]
        wage = wage[:wage.index("<")]
        wage = wage.rstrip()
    except ValueError:
        wage = 'Not Found'

    if job_title not in old_jobs:
        html += f'''<p><a href={job_url}>{job_title}</a> is {distance} 
        miles away from you and is closing in {date}. It pays {wage}.</p><br>\n'''

        plain += f'{job_title} - {job_url} is {distance} miles away from you. It closes in {date}. It pays {wage}'

        new_jobs.append(job_title)

    updated_file = open('/Users/nathanprice/Dropbox/Python/Job-scraping/jobs.txt', 'a')
    updated_file.write(f'{job_title},')

html += '</body></html>'
if len (new_jobs) == 0:
    exit()

message = MIMEMultipart('alternative')
message['Subject'] = 'New Jobs'
message['From'] = user
message['To'] = address

part1 = MIMEText(plain, 'plain')
part2 = MIMEText(html, 'html')

message.attach(part1)
message.attach(part2)

port = 465
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
    server.login(user, password)
    server.sendmail(user, address, message.as_string())