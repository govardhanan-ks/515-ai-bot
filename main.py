from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from datetime import datetime

from scripts.utils import Utils

from dotenv import load_dotenv

from atlassian import Confluence

import lmstudio as lms
from bs4 import BeautifulSoup

load_dotenv()

class Main:
    def __init__(self, page_id = os.environ["UPDATE_PAGE_ID"]):
        self.confluence = Confluence(url="https://wiki.at.sky/",
                        token=os.environ.get("WIKI_TOKEN"),
        )
        self.page_id = page_id
        self.page = self.confluence.get_page_by_id(page_id, expand="body.storage")
        page_body = self.page["body"]["storage"]["value"]

        self.soup = BeautifulSoup(page_body, "html.parser")

        self.app = App(token=os.environ.get("SLACK_TOKEN"))

        self.utils_app = Utils()
        self.register_listeners()

    def register_listeners(self):

        @self.app.event("app_mention")
        def handle_mention(event,say,client):
            inp = event.get("text")
            user_id = event.get("user").lstrip('@')
            #print(user_id)
            user_info = client.users_info(user=user_id)
            username = user_info["user"]["profile"].get("display_name") or user_info["user"]["profile"].get("real_name")


            response = self.utils_app.generate_content(inp)
            print(f"Sending {response} as 515 to confluence")

            table = self.soup.find("table")
            if not table:
                table_html = """
                <h2>515 Update</h2>
                <table>
                <colgroup>
                    <col/>
                    <col/>
                    <col/>
                </colgroup>
                <tbody>
                    <tr>
                    <th>Author</th>
                    <th>Update Summary</th>
                    <th>Timestamp</th>
                    </tr>
                </tbody>
                </table>
                """
            
                new_soup = BeautifulSoup(table_html, "html.parser")
                self.soup.append(new_soup)
                table = new_soup.find("table")

                # user_id = event.get("user").lstrip('@')
                # user_info = client.users_info(user=user_id)
                # username = user_info["user"]["profile"].get("display_name") or user_info["user"]["profile"].get("real_name")

            new_row = self.soup.new_tag("tr")
            new_row.append(self.soup.new_tag("td"))
            new_row.td.string = username
            new_row.append(self.soup.new_tag("td"))
            new_row.contents[1].string = response
            new_row.append(self.soup.new_tag("td"))
            new_row.contents[2].string = str(datetime.now())

            table.tbody.append(new_row)

            self.confluence.update_page(
            page_id=self.page_id,
            title=self.page["title"],
            body=str(self.soup),
            representation="storage"
            )


            say(f"Sending {response} as 515 to confluence",thread_ts=event["ts"])

    def start(self):
        handler = SocketModeHandler(self.app, os.environ["SLACK_APP_TOKEN"])
        handler.start()


if __name__== "__main__":
    Main().start()



