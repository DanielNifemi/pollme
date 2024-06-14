from twilio.rest import Client

account_sid = 'AC5491bc626c21b14b8109d9b4feeb5699'
auth_token = '9cf49567b3b401077bc917a4f3218ae4'
client = Client(account_sid, auth_token)

message = client.messages.create(
  body=' I need 2000 for my plastic student ID card, and i am owing the bag collector 1000',
  from_='+13144709530',
  to='+2348023214464'
)

print(message.sid)
