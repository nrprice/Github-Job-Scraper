import requests
from bs4 import BeautifulSoup
import re
from login import user, password, address
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# The url contains a lot of key information and can be modified fairly easily.
# You can specify address & distance from
# Job title search, current url is searching 'data'

# "Sort&resultsPerPage=50&pid" is important as it specifies how many results to load to a single page.
# Loading 50 means you don't have to worry about code to check subsequent pages
# should there be more than one page worth of information

URL = "https://www.findapprenticeship.service.gov.uk/apprenticeships?SearchField=All&Keywords=data&Location=NW101NB&WithinDistance=20&ApprenticeshipLevel=All&DisabilityConfidentOnly=false&Latitude=51.554445&Longitude=-0.239707&Hash=-1450857957&SearchMode=Keyword&Category=&LocationType=NonNational&GoogleMapApiKey=AIzaSyAg5lwS3ugdAVGf5gdgNvLe_0-7XcMICIM&sortType=Relevancy&SearchAction=Sort&resultsPerPage=50&pid=012592db-4b5f-4fe1-a65b-5289695ac9b5&DisplayDescription=true&DisplayDistance=true&DisplayClosingDate=true&DisplayStartDate=true&DisplayApprenticeshipLevel=false&DisplayWage=true"

# Requests the page and reads in the HTML information.
page = requests.get(URL)
soup = BeautifulSoup(page.content, 'html.parser')
# pagedlist is the section of the page that has the majority of the information
results = soup.find(id='pagedList')
# grid-row is a subsection of pagedlist that contains information regarding wages
wages = soup.find('div', attrs={'class': 'grid-row'})

# Creates list of the various pieces of information needed.
job_elems = results.find_all('a', class_='vacancy-link')
distance_val = results.find_all('span', id='distance-value')
closing_dates = results.find_all('span', id='closing-date-value')
wage_vals = results.find_all('ul', attrs={'class': 'list sfa-no-margins vacancy-details-list'})
# Reads in the list of previously found jobs, and splits them on the comma to create a list of job titles.
job_file = open('jobs.txt', "r")
old_jobs = job_file.read().split(',')
job_file.close()
# List to track whether or not there are new job postings. We later call len() of this list to see
new_jobs = []

# First part of the email message to myself.
html = '''<html><body>\n'''
plain = ''''''

# Iterates over each list to return job, distance, data and wage information for each individual job.
for job, distance, date, wage in zip(job_elems, distance_val, closing_dates, wage_vals):


    # The html information being returned in job is always the same format & similar length.
    # Split on the " to try and find the href=" code block.
    job = str(job).split('"')
    # The last entry of the split is the text containing the job title
    job_title = job[-1][1:-4]
    # Second to last entry is the url to append to create the direct link to the job posting
    job_url = 'https://www.findapprenticeship.service.gov.uk' + job[-2]
    # regex to find the digits in the distance string as two seperate integers
    distance = re.findall(r'\d+', str (distance))
    # join them together with a period to give 4.3 / 6.7
    distance = ".".join(distance)
    # The first section of data is always the same HTML code + a datetime format.
    # So we can just give the index position of the end of that block.
    date = str(date)[63:-7]
    # The wage value we just have easy access to
    wage = str(wage)

    try:
        # Wage becomes a string from the first £ symbol to the first html block.
        wage = wage[wage.index("£"):]
        wage = wage[:wage.index("<")]
        wage = wage.rstrip()
    except ValueError:
        # Some entries list the wage as 'competitive', in that case it will just return not found.
        wage = 'Not Found'
    # If the job title was not in the jobs.txt file and was not read into the list,
    # it will add that job information to the email.
    if job_title not in old_jobs:

        # appends information to the existing strings for the email
        html += f'''<p><a href={job_url}>{job_title}</a> is {distance} 
        miles away from you and is closing in {date}. It pays {wage}.</p><br>\n'''
        plain += f'{job_title} - {job_url} is {distance} miles away from you. It closes in {date}. It pays {wage}'

        # adds any new job found to the new_jobs list
        new_jobs.append(job_title)
    # writes all job titles to the job.txt file
    updated_file = open('jobs.txt', 'a')
    updated_file.write(f'{job_title},')

# finishes the html email code
html += '</body></html>'

# checks to see if there are actually any new jobs, if not will exit the script
if len (new_jobs) == 0:
    exit()

# Creates and sends the email using the scraped information
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