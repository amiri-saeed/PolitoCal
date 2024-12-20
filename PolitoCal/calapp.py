from flask import Flask, redirect, url_for, session, request, render_template, flash
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
# from concurrent.futures import ThreadPoolExecutor

from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

import logging
import os
import pathlib
import pytz
from datetime import datetime, timedelta
from parser.parse import parse_university_calendar  # Import your parser function

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

if app.debug:
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only

CLIENT_SECRETS_FILE = pathlib.Path(__file__).parent / "creds/credentials.json"
SCOPES = ['https://www.googleapis.com/auth/calendar']
REDIRECT_URI = os.environ.get('REDIRECT_URI', 'http://localhost:8000/oauth2callback')

LOCAL_TIMEZONE = pytz.timezone('Europe/Rome')

@app.route('/')
def index():
    if 'credentials' in session:
        return redirect(url_for('calendar_page'))
    return render_template('index.html')

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    session['state'] = state
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=REDIRECT_URI
    )
    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    session['credentials'] = credentials_to_dict(credentials)

    return redirect(url_for('calendar_page'))

@app.route('/calendar')
def calendar_page():
    if 'credentials' not in session:
        return redirect(url_for('index'))

    credentials = Credentials(**session['credentials'])

    try:
        service = build('calendar', 'v3', credentials=credentials)
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])

        # Update credentials in session after refreshing
        session['credentials'] = credentials_to_dict(credentials)

    except Exception:
        session.clear()  # Clear session on refresh error
        # flash('Session expired, please log in again.', 'error')
        return redirect(url_for('index'))

    return render_template('calendar.html', calendars=calendars)

@app.route('/calendar', methods=['POST'])
def calendar_post():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))

    credentials = Credentials(**session['credentials'])
    service = build('calendar', 'v3', credentials=credentials)

    calendar_id = request.form['calendar_id']
    calendar_url = request.form['calendar_url']
    start_date = request.form['start_date']

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

    try:
        corrected_url = validate_and_correct_url(calendar_url, start_date)
    except ValueError as e:
        flash(f"Invalid URL: {e}", 'error')
        return redirect(url_for('calendar_page'))

    try:
        events = parse_university_calendar(corrected_url)
    except Exception as e:
        flash(f"Error parsing calendar: {e}", 'error')
        return redirect(url_for('calendar_page'))

    try:
        for event in events:
            logging.debug(f"Original event: {event['summary']} | Start: {event['start']['dateTime']} | End: {event['end']['dateTime']}")

            logging.debug(f"Converted event: {event['summary']} | Start: {event['start']['dateTime']} | End: {event['end']['dateTime']}")

            insert_event(service, calendar_id, event)

        flash("Events have been successfully added to your calendar!", 'success')
    except Exception as e:
        flash(f"Error adding events: {e}", 'error')

    return redirect(url_for('calendar_page'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def insert_event(service, calendar_id, event):
    try:
        event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
        print(f"Event created: {event_result['summary']}")
    except Exception as e:
        print(f"Failed to insert event: {event['summary']}")
        print(f"Error: {e}")

def validate_and_correct_url(url, start_date):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)

    idImtNumcor = query_params.get('idImtNumcor', [None])[0]
    if idImtNumcor is None or not all(part.count('-') == 1 for part in idImtNumcor.split('/')):
        raise ValueError("URL must contain 'idImtNumcor' with value formatted as 'id-course-id' separated by '/'. Look for Where to find the URL?")

    query_params['xml'] = 'S'
    query_params['datarif'] = start_date.strftime('%d/%m/%Y')

    new_query_string = urlencode(query_params, doseq=True)
    corrected_url = urlunparse((
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        parsed_url.params,
        new_query_string,
        parsed_url.fragment
    ))

    return corrected_url

def credentials_to_dict(credentials):
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

if __name__ == '__main__':
    app.run('localhost', 8000, debug=True)









# # # from flask import Flask, redirect, url_for, session, request, render_template, flash
# # # from google.oauth2.credentials import Credentials
# # # from google_auth_oauthlib.flow import Flow
# # # from googleapiclient.discovery import build
# # # from concurrent.futures import ThreadPoolExecutor

# # # from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# # # import logging
# # # logging.basicConfig(level=logging.DEBUG)

# # # import os
# # # import pathlib
# # # from parser.parse import parse_university_calendar  # Import your parser function


# # # app = Flask(__name__)
# # # # app.secret_key = '0d33fb35e6e7732afd573ab45d0da63a'
# # # app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')


# # # if app.debug:
# # #     os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only

# # # CLIENT_SECRETS_FILE = pathlib.Path(__file__).parent / "creds/credentials.json"
# # # SCOPES = ['https://www.googleapis.com/auth/calendar']

# # # # REDIRECT_URI = "http://localhost:8000/oauth2callback"
# # # REDIRECT_URI = os.environ.get('REDIRECT_URI', 'http://localhost:8000/oauth2callback')


# # # @app.route('/')
# # # def index():
# # #     if 'credentials' in session:
# # #         return redirect(url_for('calendar_page'))
# # #     return render_template('index.html')  # Show raw page with login option

# # # @app.route('/authorize')
# # # def authorize():
# # #     flow = Flow.from_client_secrets_file(
# # #         CLIENT_SECRETS_FILE,
# # #         scopes=SCOPES,
# # #         redirect_uri=REDIRECT_URI
# # #     )
# # #     authorization_url, state = flow.authorization_url(
# # #         access_type='offline',
# # #         include_granted_scopes='true'
# # #     )
# # #     session['state'] = state
# # #     return redirect(authorization_url)

# # # @app.route('/oauth2callback')
# # # def oauth2callback():
# # #     state = session['state']
# # #     flow = Flow.from_client_secrets_file(
# # #         CLIENT_SECRETS_FILE,
# # #         scopes=SCOPES,
# # #         state=state,
# # #         redirect_uri=REDIRECT_URI
# # #     )
# # #     authorization_response = request.url
# # #     flow.fetch_token(authorization_response=authorization_response)

# # #     credentials = flow.credentials
# # #     session['credentials'] = credentials_to_dict(credentials)

# # #     return redirect(url_for('calendar_page'))

# # # @app.route('/calendar')
# # # def calendar_page():
# # #     if 'credentials' not in session:
# # #         return redirect(url_for('index'))

# # #     credentials = Credentials(**session['credentials'])
# # #     service = build('calendar', 'v3', credentials=credentials)

# # #     # Get the list of calendars
# # #     calendar_list = service.calendarList().list().execute()
# # #     calendars = calendar_list.get('items', [])

# # #     return render_template('calendar.html', calendars=calendars)


# # # @app.route('/calendar', methods=['POST'])
# # # def calendar_post():
# # #     if 'credentials' not in session:
# # #         return redirect(url_for('authorize'))

# # #     credentials = Credentials(**session['credentials'])
# # #     service = build('calendar', 'v3', credentials=credentials)

# # #     calendar_id = request.form['calendar_id']
# # #     calendar_url = request.form['calendar_url']

# # #     # Validate and correct the URL
# # #     try:
# # #         corrected_url = validate_and_correct_url(calendar_url)
# # #     except ValueError as e:
# # #         flash(f"Invalid URL: {e}", 'error')
# # #         return redirect(url_for('calendar_page'))

# # #     # Parse events from university calendar
# # #     try:
# # #         events = parse_university_calendar(corrected_url)
# # #     except Exception as e:
# # #         flash(f"Error parsing calendar: {e}", 'error')
# # #         return redirect(url_for('calendar_page'))

# # #     # Parallelize the event insertion
# # #     # try:
# # #     #     with ThreadPoolExecutor() as executor:
# # #     #         futures = [executor.submit(insert_event, service, calendar_id, event) for event in events]

# # #     #     # Optionally, wait for all futures to complete
# # #     #     for future in futures:
# # #     #         future.result()
# # #     try:
# # #         for event in events:
# # #             insert_event(service, calendar_id, event)

# # #         flash("Events have been successfully added to your calendar!", 'success')
# # #     except Exception as e:
# # #         flash(f"Error adding events: {e}", 'error')

# # #     return redirect(url_for('calendar_page'))


# # # @app.route('/logout')
# # # def logout():
# # #     session.clear()  # Clear the session
# # #     return redirect(url_for('index'))  # Redirect to raw page

# # # def insert_event(service, calendar_id, event):
# # #     try:
# # #         event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
# # #         print(f"Event created: {event_result['summary']}")
# # #     except Exception as e:
# # #         print(f"Failed to insert event: {event['summary']}")
# # #         print(f"Error: {e}")

# # # def validate_and_correct_url(url):
# # #     # Parse the URL
# # #     parsed_url = urlparse(url)
# # #     query_params = parse_qs(parsed_url.query)

# # #     # Check if 'idImtNumcor' is present and correctly formatted
# # #     idImtNumcor = query_params.get('idImtNumcor', [None])[0]
# # #     if idImtNumcor is None or not all(part.count('-') == 1 for part in idImtNumcor.split('/')):
# # #         raise ValueError("URL must contain 'idImtNumcor' with value formatted as 'id-course-id' separated by '/'. Look for Where to find the URL?")

# # #     # Ensure 'xml' parameter is set to 'S'
# # #     query_params['xml'] = 'S'

# # #     # Reconstruct the URL with the corrected parameters
# # #     new_query_string = urlencode(query_params, doseq=True)
# # #     corrected_url = urlunparse((
# # #         parsed_url.scheme,
# # #         parsed_url.netloc,
# # #         parsed_url.path,
# # #         parsed_url.params,
# # #         new_query_string,
# # #         parsed_url.fragment
# # #     ))

# # #     return corrected_url

# # # def credentials_to_dict(credentials):
# # #     return {
# # #         'token': credentials.token,
# # #         'refresh_token': credentials.refresh_token,
# # #         'token_uri': credentials.token_uri,
# # #         'client_id': credentials.client_id,
# # #         'client_secret': credentials.client_secret,
# # #         'scopes': credentials.scopes
# # #     }

# # # if __name__ == '__main__':
# # #     app.run('localhost', 8000, debug=True)



# # # WORKING
# # from flask import Flask, redirect, url_for, session, request, render_template, flash
# # from google.oauth2.credentials import Credentials
# # from google_auth_oauthlib.flow import Flow
# # from googleapiclient.discovery import build
# # from concurrent.futures import ThreadPoolExecutor

# # from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# # import logging
# # import os
# # import pathlib
# # import pytz
# # from datetime import datetime
# # from parser.parse import parse_university_calendar  # Import your parser function

# # logging.basicConfig(level=logging.DEBUG)

# # app = Flask(__name__)
# # app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# # if app.debug:
# #     os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only

# # CLIENT_SECRETS_FILE = pathlib.Path(__file__).parent / "creds/credentials.json"
# # SCOPES = ['https://www.googleapis.com/auth/calendar']
# # REDIRECT_URI = os.environ.get('REDIRECT_URI', 'http://localhost:8000/oauth2callback')

# # LOCAL_TIMEZONE = pytz.timezone('Europe/Rome')

# # @app.route('/')
# # def index():
# #     if 'credentials' in session:
# #         return redirect(url_for('calendar_page'))
# #     return render_template('index.html')

# # @app.route('/authorize')
# # def authorize():
# #     flow = Flow.from_client_secrets_file(
# #         CLIENT_SECRETS_FILE,
# #         scopes=SCOPES,
# #         redirect_uri=REDIRECT_URI
# #     )
# #     authorization_url, state = flow.authorization_url(
# #         access_type='offline',
# #         include_granted_scopes='true'
# #     )
# #     session['state'] = state
# #     return redirect(authorization_url)

# # @app.route('/oauth2callback')
# # def oauth2callback():
# #     state = session['state']
# #     flow = Flow.from_client_secrets_file(
# #         CLIENT_SECRETS_FILE,
# #         scopes=SCOPES,
# #         state=state,
# #         redirect_uri=REDIRECT_URI
# #     )
# #     authorization_response = request.url
# #     flow.fetch_token(authorization_response=authorization_response)

# #     credentials = flow.credentials
# #     session['credentials'] = credentials_to_dict(credentials)

# #     return redirect(url_for('calendar_page'))

# # @app.route('/calendar')
# # def calendar_page():
# #     if 'credentials' not in session:
# #         return redirect(url_for('index'))

# #     credentials = Credentials(**session['credentials'])
# #     service = build('calendar', 'v3', credentials=credentials)

# #     calendar_list = service.calendarList().list().execute()
# #     calendars = calendar_list.get('items', [])

# #     return render_template('calendar.html', calendars=calendars)

# # @app.route('/calendar', methods=['POST'])
# # def calendar_post():
# #     if 'credentials' not in session:
# #         return redirect(url_for('authorize'))

# #     credentials = Credentials(**session['credentials'])
# #     service = build('calendar', 'v3', credentials=credentials)

# #     calendar_id = request.form['calendar_id']
# #     calendar_url = request.form['calendar_url']

# #     try:
# #         corrected_url = validate_and_correct_url(calendar_url)
# #     except ValueError as e:
# #         flash(f"Invalid URL: {e}", 'error')
# #         return redirect(url_for('calendar_page'))

# #     try:
# #         events = parse_university_calendar(corrected_url)
# #     except Exception as e:
# #         flash(f"Error parsing calendar: {e}", 'error')
# #         return redirect(url_for('calendar_page'))

# #     try:
# #         for event in events:
# #             # Log original event times before conversion
# #             logging.debug(f"Original event: {event['summary']} | Start: {event['start']['dateTime']} | End: {event['end']['dateTime']}")

# #             # convert_event_to_utc(event)

# #             # Log converted event times
# #             logging.debug(f"Converted event: {event['summary']} | Start: {event['start']['dateTime']} | End: {event['end']['dateTime']}")

# #             insert_event(service, calendar_id, event)

# #         flash("Events have been successfully added to your calendar!", 'success')
# #     except Exception as e:
# #         flash(f"Error adding events: {e}", 'error')

# #     return redirect(url_for('calendar_page'))

# # @app.route('/logout')
# # def logout():
# #     session.clear()
# #     return redirect(url_for('index'))

# # def convert_event_to_utc(event):
# #     """Convert the event's start and end times to UTC."""
# #     start_time = datetime.fromisoformat(event['start']['dateTime']).astimezone(LOCAL_TIMEZONE)
# #     end_time = datetime.fromisoformat(event['end']['dateTime']).astimezone(LOCAL_TIMEZONE)

# #     # Now convert to UTC
# #     event['start']['dateTime'] = start_time.astimezone(pytz.utc).isoformat()
# #     event['end']['dateTime'] = end_time.astimezone(pytz.utc).isoformat()
# #     event['start']['timeZone'] = 'UTC'
# #     event['end']['timeZone'] = 'UTC'

# # def insert_event(service, calendar_id, event):
# #     try:
# #         event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
# #         print(f"Event created: {event_result['summary']}")
# #     except Exception as e:
# #         print(f"Failed to insert event: {event['summary']}")
# #         print(f"Error: {e}")

# # def validate_and_correct_url(url):
# #     parsed_url = urlparse(url)
# #     query_params = parse_qs(parsed_url.query)

# #     idImtNumcor = query_params.get('idImtNumcor', [None])[0]
# #     if idImtNumcor is None or not all(part.count('-') == 1 for part in idImtNumcor.split('/')):
# #         raise ValueError("URL must contain 'idImtNumcor' with value formatted as 'id-course-id' separated by '/'. Look for Where to find the URL?")

# #     query_params['xml'] = 'S'

# #     new_query_string = urlencode(query_params, doseq=True)
# #     corrected_url = urlunparse((
# #         parsed_url.scheme,
# #         parsed_url.netloc,
# #         parsed_url.path,
# #         parsed_url.params,
# #         new_query_string,
# #         parsed_url.fragment
# #     ))

# #     return corrected_url

# # def credentials_to_dict(credentials):
# #     return {
# #         'token': credentials.token,
# #         'refresh_token': credentials.refresh_token,
# #         'token_uri': credentials.token_uri,
# #         'client_id': credentials.client_id,
# #         'client_secret': credentials.client_secret,
# #         'scopes': credentials.scopes
# #     }

# # if __name__ == '__main__':
# #     app.run('localhost', 8000, debug=True)


# from flask import Flask, redirect, url_for, session, request, render_template, flash
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# from concurrent.futures import ThreadPoolExecutor

# from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

# import logging
# import os
# import pathlib
# import pytz
# from datetime import datetime
# from parser.parse import parse_university_calendar  # Import your parser function

# app = Flask(__name__)
# app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# if app.debug:
#     os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # For development only

# CLIENT_SECRETS_FILE = pathlib.Path(__file__).parent / "creds/credentials.json"
# SCOPES = ['https://www.googleapis.com/auth/calendar']
# REDIRECT_URI = os.environ.get('REDIRECT_URI', 'http://localhost:8000/oauth2callback')

# LOCAL_TIMEZONE = pytz.timezone('Europe/Rome')

# @app.route('/')
# def index():
#     if 'credentials' in session:
#         return redirect(url_for('calendar_page'))
#     return render_template('index.html')

# @app.route('/authorize')
# def authorize():
#     flow = Flow.from_client_secrets_file(
#         CLIENT_SECRETS_FILE,
#         scopes=SCOPES,
#         redirect_uri=REDIRECT_URI
#     )
#     authorization_url, state = flow.authorization_url(
#         access_type='offline',
#         include_granted_scopes='true'
#     )
#     session['state'] = state
#     return redirect(authorization_url)

# @app.route('/oauth2callback')
# def oauth2callback():
#     state = session['state']
#     flow = Flow.from_client_secrets_file(
#         CLIENT_SECRETS_FILE,
#         scopes=SCOPES,
#         state=state,
#         redirect_uri=REDIRECT_URI
#     )
#     authorization_response = request.url
#     flow.fetch_token(authorization_response=authorization_response)

#     credentials = flow.credentials
#     session['credentials'] = credentials_to_dict(credentials)

#     return redirect(url_for('calendar_page'))

# @app.route('/calendar')
# def calendar_page():
#     if 'credentials' not in session:
#         return redirect(url_for('index'))

#     credentials = Credentials(**session['credentials'])

#     try:
#         service = build('calendar', 'v3', credentials=credentials)
#         calendar_list = service.calendarList().list().execute()
#         calendars = calendar_list.get('items', [])

#         # Update credentials in session after refreshing
#         session['credentials'] = credentials_to_dict(credentials)

#     except Exception:
#         session.clear()  # Clear session on refresh error
#         # flash('Session expired, please log in again.', 'error')
#         return redirect(url_for('index'))

#     return render_template('calendar.html', calendars=calendars)

# @app.route('/calendar', methods=['POST'])
# def calendar_post():
#     if 'credentials' not in session:
#         return redirect(url_for('authorize'))

#     credentials = Credentials(**session['credentials'])
#     service = build('calendar', 'v3', credentials=credentials)

#     calendar_id = request.form['calendar_id']
#     calendar_url = request.form['calendar_url']

#     try:
#         corrected_url = validate_and_correct_url(calendar_url)
#     except ValueError as e:
#         flash(f"Invalid URL: {e}", 'error')
#         return redirect(url_for('calendar_page'))

#     try:
#         events = parse_university_calendar(corrected_url)
#     except Exception as e:
#         flash(f"Error parsing calendar: {e}", 'error')
#         return redirect(url_for('calendar_page'))

#     try:
#         for event in events:
#             logging.debug(f"Original event: {event['summary']} | Start: {event['start']['dateTime']} | End: {event['end']['dateTime']}")

#             logging.debug(f"Converted event: {event['summary']} | Start: {event['start']['dateTime']} | End: {event['end']['dateTime']}")

#             insert_event(service, calendar_id, event)

#         flash("Events have been successfully added to your calendar!", 'success')
#     except Exception as e:
#         flash(f"Error adding events: {e}", 'error')

#     return redirect(url_for('calendar_page'))

# @app.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('index'))

# def insert_event(service, calendar_id, event):
#     try:
#         event_result = service.events().insert(calendarId=calendar_id, body=event).execute()
#         print(f"Event created: {event_result['summary']}")
#     except Exception as e:
#         print(f"Failed to insert event: {event['summary']}")
#         print(f"Error: {e}")

# def validate_and_correct_url(url):
#     parsed_url = urlparse(url)
#     query_params = parse_qs(parsed_url.query)

#     idImtNumcor = query_params.get('idImtNumcor', [None])[0]
#     if idImtNumcor is None or not all(part.count('-') == 1 for part in idImtNumcor.split('/')):
#         raise ValueError("URL must contain 'idImtNumcor' with value formatted as 'id-course-id' separated by '/'. Look for Where to find the URL?")

#     query_params['xml'] = 'S'

#     new_query_string = urlencode(query_params, doseq=True)
#     corrected_url = urlunparse((
#         parsed_url.scheme,
#         parsed_url.netloc,
#         parsed_url.path,
#         parsed_url.params,
#         new_query_string,
#         parsed_url.fragment
#     ))

#     return corrected_url

# def credentials_to_dict(credentials):
#     return {
#         'token': credentials.token,
#         'refresh_token': credentials.refresh_token,
#         'token_uri': credentials.token_uri,
#         'client_id': credentials.client_id,
#         'client_secret': credentials.client_secret,
#         'scopes': credentials.scopes
#     }

# if __name__ == '__main__':
#     app.run('localhost', 8000, debug=True)


