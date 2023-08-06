import requests
import ast


class unictelecome:
    """
    Send message from unictelecom
    """
    __URL_IP_GSM = "http://cp.uniqtele.com/"

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
        self.__apikey = apikey
        self.__user = user
        self.__sender = sender
        self.__result = None
        self.__recipients = None
        self.__message = None
        self.urgent = urgent
        self.test = test

    def createmessage(self, recipients=None, message=None):
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
            self.__recipients = recipients
            self.__message = message
        arguments = {
            "r": "api/msg_send",
            "user": self.__user,
            "apikey": self.__apikey,
            "recipients": self.__recipients,
            "message": self.__message,
            "sender": self.__sender,
            "urgent": int(self.urgent),
            "test": int(self.test)
        }
        return arguments

    def __checkstatus(self, data):
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

    def sendmessage(self):
        """
        Send message
        :return: resul of message true or false
        :rtype: bool
        """
        if (self.__recipients and self.__message) is False:
            raise ValueError("Please set recipients and message.")
        arguments = self.createmessage()
        result = requests.get(url=self.__URL_IP_GSM, params=arguments)
        self.__result = self.__checkstatus(result.text)
        return self.__result
