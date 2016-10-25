import httplib2

from apiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow

# List the scopes your app requires:
SCOPES = ['https://www.googleapis.com/auth/plus.me',
          'https://www.googleapis.com/auth/plus.stream.write']

# The following redirect URI causes Google to return a code to the user's
# browser that they then manually provide to your app to complete the
# OAuth flow.
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

# For a breakdown of OAuth for Python, see
# https://developers.google.com/api-client-library/python/guide/aaa_oauth
# CLIENT_ID and CLIENT_SECRET come from your Developers Console project
flow = OAuth2WebServerFlow(client_id='174353696507-9ma9jni3bl5crhrqbnkpv6d7g0nt062q.apps.googleusercontent.com',
                           client_secret='OXKTS0EbGmZDEvm5adGmYMjW',
                           scope=SCOPES,
                           redirect_uri=REDIRECT_URI)

auth_uri = flow.step1_get_authorize_url()

# This command-line server-side flow example requires the user to open the
# authentication URL in their browser to complete the process. In most
# cases, your app will use a browser-based server-side flow and your
# user will not need to copy and paste the authorization code. In this
# type of app, you would be able to skip the next 3 lines.
# You can also look at the client-side and one-time-code flows for other
# options at https://developers.google.com/+/web/signin/
print 'Please paste this URL in your browser to authenticate this program.'
print auth_uri
code = raw_input('Enter the code it gives you here: ')

# Set authorized credentials
credentials = flow.step2_exchange(code)

# Create a new authorized API client.
http = httplib2.Http()
http = credentials.authorize(http)
service = build('plusDomains', 'v1', http=http)
people_service = service.people()
people_document = people_service.get(userId='me').execute()

print 'ID: %s' % people_document.get('id')
print 'Display name: %s' % people_document.get('displayName')
print 'Image URL: %s' % people_document.get('image').get('url')
print 'Profile URL: %s' % people_document.get('url')
