from datetime import datetime
import uuid
import os
from bs4 import BeautifulSoup
import shelve
from scripts.timestripper import TimeStripper
from atlassian import Confluence

from dotenv import load_dotenv

load_dotenv()

class AlterTable:
    def __init__(self, page_id = os.environ["UPDATE_PAGE_ID"]):
        self.confluence = Confluence(url="https://wiki.at.sky/",
                        token=os.environ.get("WIKI_TOKEN"),
        )
        with shelve.open("my_shelf") as db:
            self.current_table_uuid = db.get("current_table_uuid", "")
            if not self.current_table_uuid:
                # Create new UUID and store it
                self.current_table_uuid = str(uuid.uuid4())
                self.current_table_creation_time = datetime.now()

                db["current_table_uuid"] = self.current_table_uuid
                db["current_table_creation_time"] = self.current_table_creation_time
            else:
                self.current_table_creation_time = db.get("current_table_creation_time", "")

        self.page_id = page_id
        self.page = self.confluence.get_page_by_id(page_id, expand="body.storage")
        page_body = self.page["body"]["storage"]["value"]

        self.soup = BeautifulSoup(page_body, "html.parser")
        self.timestripper = TimeStripper()



    def get_updated_table_details(self, data, time=datetime.now()):
        time_difference = time - self.current_table_creation_time
        table = self.soup.find("table")

        if time_difference.days >= 7 or not table:
            print("Creating new table")

            # Create new UUID and time
            self.current_table_uuid = str(uuid.uuid4())
            self.current_table_creation_time = datetime.now()

            # Save to shelf
            with shelve.open("my_shelf") as db:
                db["current_table_uuid"] = self.current_table_uuid
                db["current_table_creation_time"] = self.current_table_creation_time

            # Generate new table HTML
            week_string = self.timestripper.get_week_string(self.current_table_creation_time)
            table_html = f"""
                <h2>515 Update for {week_string}</h2>
                <table>
                    <colgroup>
                        <col/><col/><col/>
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

            parsed = BeautifulSoup(table_html, "html.parser")

            self.soup.append(parsed.find("h2"))
            self.soup.append(parsed.find("table"))

            

        
            table = self.soup.find_all("table")[-1]

            if not table or not table.find("tbody"):
                raise ValueError("Table or its tbody not found after creation")

        new_row = self.soup.new_tag("tr")

        td_user = self.soup.new_tag("td")
        td_user.string = data["username"]
        new_row.append(td_user)

        td_response = self.soup.new_tag("td")
        td_response.string = data["response"]
        new_row.append(td_response)

        td_time = self.soup.new_tag("td")
        td_time.string = str(datetime.now())
        new_row.append(td_time)

        # Re-locate the (possibly new) table
        table = self.soup.find("table")
        if not table or not table.find("tbody"):
            raise ValueError("Table or its tbody not found after creation")

        table.find("tbody").append(new_row)

        # Update the confluence page
        self.confluence.update_page(
            page_id=self.page_id,
            title=self.page["title"],
            body=str(self.soup),
            representation="storage"
        )
    
