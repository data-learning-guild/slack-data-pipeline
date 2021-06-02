import base64


def subscribe_test(event, context):
    # Print out the data from Pub/Sub, to prove that it worked
    print(base64.b64decode(event['data']))

def load_to_warehouse():
    pass
