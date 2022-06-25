# Python Goolge API Wrapper for Takeuchi Lab
***tlab-google*** is a Python package that provides
an easier way to use Google API such as [Gmail API](https://developers.google.com/gmail/api).

*Google* have already provided Python packages for Google API, such as [google-api-python-client](https://github.com/googleapis/google-api-python-client).
However, it is complicated a little for Python beginners.
That is why we created the package.


## Requirements

- Python 3.10 or above
- Waseda email address (which ends with `.waseda.jp`)


## Installation
You can install it with `pip` + `git`.
```sh
$ pip install git+https://github.com/Waseda-TakeuchiLab/tlab-google
```


## Getting started

### Gmail API
#### Send a message
```python
from tlab_google import Credentials, GmailAPI
from email.mime import text

# Get a new credentials for Google API
creds = Credentials.new()

# Create a GmailAPI instance
api = GmailAPI(creds)

# Create a message
to = "foobar@example.com"  # Replace it with your email address
subject = "API Test"
body = "This is a test mail of Gmail API."
message = text.MIMEText(body)
message["to"] = to
message["subject"] = subject

# Send a message
api.send_email(message)

# You can save the credentials and reuse it
creds_file = "credentials.json"
creds.save(creds_file)                     # Save
creds = Gredentials.from_file(creds_file)  # Load again
```


#### Search messages and Get a message
```python
from tlab_google import Credentials, GmailAPI

creds_file = "credentials.json"
creds = Credentials.from_file(creds_file)
api = GmailAPI(creds)

# The query format is the same as that of the search box of Gmail app
query = "subject:(Laboratory)"
# Search messages in Gmail box
results, next_page_token, size = api.search_email(query)

# Get a message
msg_id = results[0]["id"]
gmail = api.get_email(msg_id)

# Get its subject
headers = {header["name"]: header["value"] for header in gmail["payload"]["headers"]}
subject = headers["Subject"]
```


## License
MIT License
