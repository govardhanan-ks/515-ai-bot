from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from scripts.utils import Utils

from dotenv import load_dotenv

from scripts.altertable import AlterTable

load_dotenv()

class Main:
    def __init__(self):
        self.app = App(token=os.environ.get("SLACK_TOKEN"))


        self.utils_app = Utils()
        self.alter_app = AlterTable()
        self.register_listeners()

    def register_listeners(self):

        @self.app.event("app_mention")
        def handle_mention(event,say,client):
            inp = event.get("text")
            user_id = event.get("user").lstrip('@')
            print(user_id)
            user_info = client.users_info(user=user_id)
            username = user_info["user"]["profile"].get("display_name") or user_info["user"]["profile"].get("real_name")

            response = self.utils_app.generate_content(inp)
            print(f"Sending {response} as 515 to confluence")

            data = {}
            data["username"] = username
            data["response"] = response

            self.alter_app.get_updated_table_details(data)

            say(f"Sending {response} as 515 to confluence",thread_ts=event["ts"])

    def start(self):
        handler = SocketModeHandler(self.app, os.environ["SLACK_APP_TOKEN"])
        handler.start()


if __name__== "__main__":
    Main().start()



