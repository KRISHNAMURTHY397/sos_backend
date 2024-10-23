from rest_framework.decorators import api_view
from rest_framework.response import Response
from twilio.rest import Client

account_sid = 'your_twilio_sid'
auth_token = 'your_twilio_auth_token'
twilio_phone_number = 'your_twilio_number'
emergency_contact = 'emergency_contact_number'

@api_view(['POST'])
def send_sos(request):
    location = request.data.get('location', 'Unknown location')
    message = request.data.get('message', 'Emergency!')

    # Initialize Twilio client
    client = Client(account_sid, auth_token)
    
    try:
        client.messages.create(
            body=f"Location: {location}\nMessage: {message}",
            from_=twilio_phone_number,
            to=emergency_contact
        )
        return Response({"status": "SOS Sent!"}, status=200)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
