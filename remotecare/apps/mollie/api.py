from apps.mollie.exceptions import *
import urllib2
import urllib
from xml.dom.minidom import parseString


class Mollie:
    """
        The Mollie class allows you to send multiple sms
        messages using a single
        configuration. As an alternative, you can specify all
        arguments using the
        'sendsms' classmethod
    """
    DEFAULT_MOLLIEGW = "http://www.mollie.nl/xml/sms/"
    SECURE_MOLLIEGW = "https://www.mollie.nl/xml/sms/"

    DUTCH_GW = 1
    FOREIGN_GW = 2

    NORMAL_SMS = "normal"
    WAPPUSH_SMS = "wappush"
    VCARD_SMS = "vcard"

    __urllib = urllib
    __urllib2 = urllib2

    def __init__(self, username, password, originator=None,
                 molliegw=None, gateway=None):
        """
            Initialize the Mollie class. This configuration will be reused
            with each 'send' call.

            username
                    authentication username
            password
                    authentication password
            originator
                    SMS originator phonenumber, i.e. +31612345678
            molliegw
                    Full url of the Mollie SMS gateway. Two predefined
                    gateways are available,

                    Mollie.DEFAULT_MOLLIEGW
                        Standard (non secure) production gateway

                    Mollie.Secure_MOLLIEGW
                        Secure production gateway (https)
        """
        self.username = username
        self.password = password
        self.originator = originator
        self.molliegw = molliegw or Mollie.DEFAULT_MOLLIEGW
        self.gateway = gateway or Mollie.FOREIGN_GW

    def send(self, recipients, message, originator=None, deliverydate=None,
             smstype=None):
        """
            Send a single SMS using the instances default configuration
        """
        originator = originator or self.originator

        return self.sendsms(
            self.username, self.password, originator, recipients,
            message, self.molliegw, self.gateway, deliverydate, smstype)

    def sendsms(cls, username, password, originator, recipients,
                message, molliegw=None, gateway=None, deliverydate=None,
                smstype=None):
        if type(recipients) not in (tuple, list):
            recipients = [recipients]
        args = {}
        args['username'] = username
        args['password'] = password
        args['originator'] = originator
        args['recipients'] = ",".join(recipients)
        args['message'] = message
        args['gateway'] = gateway
        molliegw = molliegw or Mollie.DEFAULT_MOLLIEGW

        # optional arguments
        url = molliegw + "?" + cls.__urllib.urlencode(args)
        response = cls.__urllib2.urlopen(url)
        responsexml = response.read()
        dom = parseString(responsexml)
        recipients =\
            int(dom.getElementsByTagName("recipients")[0].childNodes[0].data)
        success = dom.getElementsByTagName("success")[0].childNodes[0].data
        resultcode =\
            int(dom.getElementsByTagName("resultcode")[0].childNodes[0].data)
        resultmessage =\
            dom.getElementsByTagName("resultmessage")[0].childNodes[0].data

        if success != "true":
            e = by_code[resultcode]
            raise e(resultmessage)

        return recipients

    sendsms = classmethod(sendsms)
