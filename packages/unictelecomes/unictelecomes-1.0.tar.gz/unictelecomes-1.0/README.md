Send message from unictelecom provider, this library for send message from unic telecome.

for installation please use

`pip install unictelecome`

for init library

`unictelecome = UnicTelecome(apikey="api_key", sender="sender", user="user_name")`\

create message

`unictelecome.CreateMessage(message="text", recipients="number_phone")`\

change message priority or if demo envirement

`unictelecome.test = True
unictelecome.urgent = True`

send message
`unictelecome.SendMessage()`


