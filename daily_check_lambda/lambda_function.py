from check import AttendencyCheck

def lambda_handler(event, context):
    check = AttendencyCheck('', '')
    check.make_and_send_absent_message()
    return {
        'statusCode': 200
    }