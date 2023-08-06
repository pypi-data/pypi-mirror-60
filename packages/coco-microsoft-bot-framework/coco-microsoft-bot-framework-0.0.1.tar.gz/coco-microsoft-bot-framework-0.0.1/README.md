
# A Toolkit to work with components in Microsoft Bot Framework

### Installation (We recommend using a virtualenv):
```
pip install coco-microsoft-bot-framework 
```

### Setup:
#### Setting Conversation State 
in `app.py`, include the lines below.

```python
from coco_microsoft_bot_framework import CoCoActivityHandler
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
    UserState,
    MemoryStorage,
    ConversationState,
)

MEMORY = MemoryStorage()
CONVERSATION_STATE = ConversationState(MEMORY)
# Create the Bot
BOT = MyBot(CONVERSATION_STATE)
```


#### Setting Activity Handler
in `bot.py`

Import CoCo custom Activity Handler, then use it to create your bot.
At the `on_message_activity` method add the three lines as below, in order to
manage CoCo context during the conversation.
```python
from coco_microsoft_bot_framework import CoCoActivityHandler

class MyBot(CoCoActivityHandler):

    async def on_message_activity(self, turn_context: TurnContext):
        if self.is_component_active():
            await self.call_active_component(turn_context)
            return
```


#### Activate CoCo Component
Activate CoCo register component, which ID is: "register_vp3".
```python
class MyBot(CoCoActivityHandler):

    async def on_message_activity(self, turn_context: TurnContext):
        if self.is_component_active():
            await self.call_active_component(turn_context)
            return
    
        if intent == "register":
            await self.activate_component(turn_context, "register_vp3")
        else:
            await turn_context.send_activity("I don't understand.")
```
