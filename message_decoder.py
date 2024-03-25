import base64

def decode_message(message):
    """
    Decode the message payload, extracting only text content.

    Args:
        message: Message object.

    Returns:
        Decoded text content of the message.
    """
    payload = message['payload']
    text_content = ''
    if 'parts' in payload:
        parts = payload['parts']
        for part in parts:
            if part['mimeType'] == 'text/plain':
                text_content += base64.urlsafe_b64decode(part['body']['data']).decode()
    elif 'body' in payload:
        text_content += base64.urlsafe_b64decode(payload['body']['data']).decode()
    return text_content.strip()  # Strip leading and trailing whitespace
