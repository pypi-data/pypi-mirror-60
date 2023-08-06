from botbuilder.core import ActivityHandler

import coco


class CoCoActivityHandler(ActivityHandler):
    def __init__(self, conversation_state):
        self.conversation_state = conversation_state

        self.conversation_state.create_property("coco_context")
        self.conversation_state.coco_context = False
        self.conversation_state.create_property("active_component")
        self.conversation_state.active_component = None
        self.conversation_state.create_property("session_id")
        self.conversation_state.session_id = None

        self.conversation_state.create_property("context_params")
        self.conversation_state.context_params = {}

    def _update_context(self, turn_context, component_id):
        self.conversation_state.coco_context = True
        self.conversation_state.active_component = component_id
        self.conversation_state.session_id = turn_context.activity.conversation.id

    def is_component_active(self):
        if self.conversation_state.coco_context:
            return True
        return False

    async def call_active_component(self, turn_context):
        coco_response = coco.exchange(self.conversation_state.active_component,
                                      self.conversation_state.session_id,
                                      turn_context.activity.text,
                                      **self.conversation_state.context_params)

        self.conversation_state.context_params.update(coco_response.updated_context)

        if coco_response.component_done or coco_response.component_failed:
            self.conversation_state.coco_context = False
            self.conversation_state.active_component = None
            self.conversation_state.session_id = None

        await turn_context.send_activity(coco_response.response)

    async def activate_component(self, turn_context, component_id):
        self._update_context(turn_context, component_id)
        await self.call_active_component(turn_context)
