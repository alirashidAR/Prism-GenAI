from gmail_service import get_service, get_messages, get_message
from message_decoder import decode_message

def email_service():
    service = get_service()
    messages = get_messages(service, user_id="303wspartan@gmail.com", max_results=10)
    message_array = []
    decoded_content_array = []
    if messages:
        for message in messages[7:8]:
            msg_id = message['id']
            msg_details = get_message(service, user_id="303wspartan@gmail.com", msg_id=msg_id)
            message_array.append(msg_details)
            decoded_content = decode_message(msg_details)
            decoded_content_array.append(decoded_content)
    return message_array, decoded_content_array

if __name__ == "__main__":
    email_service()
