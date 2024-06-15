# Download the helper library from https://www.twilio.com/docs/python/install
# import os
# from twilio.rest import Client
#
#
# # Find your Account SID and Auth Token at twilio.com/console
# # and set the environment variables. See http://twil.io/secure
# account_sid = os.environ['TWILIO_ACCOUNT_SID']
# auth_token = os.environ['TWILIO_AUTH_TOKEN']
# client = Client(account_sid, auth_token)
#
# validation_request = client.validation_requests \
#                            .create(
#                                 friendly_name='My Home Phone Number',
#                                 phone_number='+447896286127'
#                             )
#
# print(validation_request.friendly_name)
import http.client

conn = http.client.HTTPSConnection("textflow-sms-api.p.rapidapi.com")

payload = "{\"testing\":\"true\"}"

headers = {
    'x-rapidapi-key': "d42f68d9bfmsh597540a8266a3dep1140f1jsnc32c7ba76702",
    'x-rapidapi-host': "textflow-sms-api.p.rapidapi.com",
    'Content-Type': "application/json"
}

conn.request("POST", "/service/check", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))
