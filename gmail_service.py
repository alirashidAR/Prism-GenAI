import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def get_messages(service, user_id="me", max_results=10):
    try:
        response = service.users().messages().list(userId=user_id, maxResults=max_results).execute()
        messages = response.get("messages", [])
        return messages
    except HttpError as error:
        print(f"An error occurred while fetching messages: {error}")
        return None

def get_message(service, user_id="me", msg_id=""):
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id).execute()
        return message
    except HttpError as error:
        print(f"An error occurred while fetching the message: {error}")
        return None





def print_labels(service, user_id="me"):
    """
    Prints the labels of a Gmail account.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. Default is 'me'.
    """
    try:
        labels = service.users().labels().list(userId=user_id).execute()
        if 'labels' in labels:
            print("Labels:")
            for label in labels['labels']:
                print(label['name'])
        else:
            print("No labels found.")
    except HttpError as error:
        print(f"An error occurred while fetching labels: {error}")

def get_important_label_id(service, user_id="me"):
    """
    Retrieves the label ID for the "IMPORTANT" label.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. Default is 'me'.

    Returns:
        Label ID for the "IMPORTANT" label.
    """
    try:
        labels = service.users().labels().list(userId=user_id).execute()
        for label in labels['labels']:
            if label['name'] == 'IMPORTANT':
                return label['id']
    except HttpError as error:
        print(f"An error occurred while fetching labels: {error}")
    return None

def get_important_messages(service, user_id="me", max_results=10):
    """
    Retrieves important messages from the specified Gmail account.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. Default is 'me'.
        max_results: Maximum number of messages to retrieve. Default is 10.

    Returns:
        List of important message objects.
    """
    label_id = get_important_label_id(service, user_id=user_id)
    if label_id:
        query = f"label:{label_id}"
        try:
            response = service.users().messages().list(userId=user_id, maxResults=max_results, q=query).execute()
            messages = response.get("messages", [])
            return messages
        except HttpError as error:
            print(f"An error occurred while fetching important messages: {error}")
    return None
