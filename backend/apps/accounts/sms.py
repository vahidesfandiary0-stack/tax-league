class SMSDeliveryNotConfigured(Exception):
    pass


def send_login_code(phone_number, code):
    """
    SMS provider adapter placeholder.

    Configure a real Iranian SMS provider and credentials through environment
    variables before enabling OTP delivery. Never print or return OTP codes
    from production endpoints.
    """
    raise SMSDeliveryNotConfigured("SMS provider is not configured")
