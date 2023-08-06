Send message from unictelecom provider, this library for send message from unic telecome.

for installation please use

`pip install unictelecomes`

for init library

`from unictelecome import unictelecome`

`unictelecome = unictelecome(apikey="api_key", sender="sender", user="user_name")`\

create message

`unictelecome.createmessage(message="text", recipients="number_phone")`\

change message priority or if demo envirement

`unictelecome.test = True
unictelecome.urgent = True`

send message
`unictelecome.sendmessage()`


