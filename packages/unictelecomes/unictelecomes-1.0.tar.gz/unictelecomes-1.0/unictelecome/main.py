import requests
import ast


class UnicTelecome:
    """
    Send message from unictelecom
    """
    URL_IP_GSM = "http://cp.uniqtele.com/"

    def __init__(self, user, apikey, sender, urgent=1, test=0):
        """
        Set parametrs
        :param user: user name unictelecome
        :type user: str
        :param apikey: access api key
        :type apikey: str
        :param sender: message sender name
        :type sender: str
        :param urgent: message send urgently or not
        :type urgent: bool
        :param test: this message is test or not
        :type test: bool
        """
        self.apikey = apikey
        self.user = user
        self.recipients = None
        self.message = None
        self.sender = sender
        self.urgent = urgent
        self.test = test
        self.__result = None

    def CheckStatus(self, data):
        """
        Check result is success send message
        :param data: response from unictelecom dict
        :type data: str
        :return: result True or false
        :rtype: str
        """
        data_dict = ast.literal_eval(data)
        if data_dict.get("status") == "success":
            return "Message sended success"
        raise Exception(f"Message is not sended: {data_dict.get('message')}")

    def CreateMessage(self, recipients=None, message=None):
        """
        CreateMessage for send
        :param recipients: phone number send sms
        :type recipients: str
        :param message: message text
        :type message: str
        :return: dict parametrs for request
        :rtype: dict
        """
        if recipients and message:
            self.recipients = recipients
            self.message = message
        arguments = {
            "r": "api/msg_send",
            "user": self.user,
            "apikey": self.apikey,
            "recipients": self.recipients,
            "message": self.message,
            "sender": self.sender,
            "urgent": int(self.urgent),
            "test": int(self.test)
        }
        return arguments

    def SendMessage(self):
        """
        Send message
        :return: resul of message true or false
        :rtype: bool
        """
        if (self.recipients and self.message) is False:
            raise ValueError("Please set recipients and message.")
        arguments = self.CreateMessage()
        result = requests.get(url=self.URL_IP_GSM, params=arguments)
        self.__result = self.CheckStatus(result.text)
        return self.__result
