from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from datetime import datetime

from dotenv import load_dotenv

from atlassian import Confluence

import lmstudio as lms
from bs4 import BeautifulSoup

load_dotenv()

confluence = Confluence(url="https://wiki.at.sky/",
                        token=os.environ.get("WIKI_TOKEN"),
)
page_id = "1073002353"
space = "OE"

page = confluence.get_page_by_id(page_id, expand="body.storage")
page_body = page["body"]["storage"]["value"]

soup = BeautifulSoup(page_body, "html.parser")


app = App(token=os.environ.get("SLACK_TOKEN"))




@app.event("app_mention")
def event_handle(event,say,client):
    inp = event.get("text")
    user_id = event.get("user").lstrip('@')
    print(user_id)
    user_info = client.users_info(user=user_id)
    username = user_info["user"]["profile"].get("display_name") or user_info["user"]["profile"].get("real_name")

    prompt = f""""
    You are a smart AI assistant tool,

    given this input {inp}, generate a small 515 50 word summary of the input and return only that summary
    """

    with lms.Client() as client:
        model = client.llm.model("mistralai/devstral-small-2505")
        chat = lms.Chat()
        chat.add_user_message(prompt)
        response = model.respond(chat)
        
        print(f"Sending {response.content} as 515 to confluence")

        table_markup = f"""

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
            <tr>
            <td>{username}</td>
            <td>{response.content}</td>
            <td>{datetime.now()}</td>
            </tr>
        </tbody>
        </table>

        """
        table = soup.find("table")
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
            soup.append(new_soup)
            table = new_soup.find("table")

        # user_id = event.get("user").lstrip('@')
        # user_info = client.users_info(user=user_id)
        # username = user_info["user"]["profile"].get("display_name") or user_info["user"]["profile"].get("real_name")

        new_row = soup.new_tag("tr")
        new_row.append(soup.new_tag("td"))
        new_row.td.string = username
        new_row.append(soup.new_tag("td"))
        new_row.contents[1].string = response.content
        new_row.append(soup.new_tag("td"))
        new_row.contents[2].string = str(datetime.now())

        table.tbody.append(new_row)


        # confluence.append_page(
        #     page_id,
        #     "Temporary 515",
        #     table_markup,
        #     parent_id=None,
        #     representation='storage',
        #     minor_edit=False)

        confluence.update_page(
        page_id=page_id,
        title=page["title"],
        body=str(soup),
        representation="storage"
    )


        say(f"Sending {response.content} as 515 to confluence",thread_ts=event["ts"])



if __name__== "__main__":
    SocketModeHandler(app,os.environ["SLACK_APP_TOKEN"]).start()



