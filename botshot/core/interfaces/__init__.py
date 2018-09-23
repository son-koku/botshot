from botshot.tasks import run_async
from botshot.models import ChatConversation, ChatUser, ChatMessage
from botshot.core.parsing.raw_message import RawMessage
from botshot.core import config
from django.http.response import HttpResponse, HttpResponseBadRequest
import json
import logging
import time

class BotshotInterface():
    name = None

    def webhook(self, request):
        raise NotImplementedError()

    def send_responses(self, user: ChatUser, responses):
        raise NotImplementedError()

    def broadcast_responses(self, users, responses):
        raise NotImplementedError()

    def fill_conversation_details(self, conversation: ChatConversation):
        pass

    def fill_user_details(self, user: ChatUser):
        pass

    def on_message_processing_start(self, message: ChatMessage):
        pass

    def on_server_startup(self):
        # TODO: run this function at startup
        pass


class BasicAsyncInterface(BotshotInterface):

    def __init__(self):
        self.msg_limit_seconds = config.get('MSG_LIMIT_SECONDS', 15)

    def webhook(self, request):
        from botshot.core.message_manager import MessageManager
        if request.method == "POST":
            manager = MessageManager()
            request_body = json.loads(request.body.decode('utf-8'))
            raw_messages = self.parse_raw_messages(request_body)
            print(raw_messages)
            for raw_message in raw_messages:
                print(raw_message)
                diff_seconds = time.time() - raw_message.timestamp / 1000
                if diff_seconds > self.msg_limit_seconds:
                    logging.warning("Delay {} seconds too big, ignoring message!".format(diff_seconds))
                    continue
                self.on_message_received(raw_message)
                run_async(manager.process, raw_message=raw_message)
            return HttpResponse()

        elif request.method == "GET":
            return self.webhook_get(request)

        return HttpResponseBadRequest()

    def on_message_received(self, raw_message: RawMessage):
        pass

    def webhook_get(self, request):
        pass

    def parse_raw_messages(self, request):
        raise NotImplementedError()

    def on_server_startup(self):
        pass