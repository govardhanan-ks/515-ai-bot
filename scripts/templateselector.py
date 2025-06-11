from datetime import datetime
import uuid

class AlterTable:
    def __init__(self):
        self.new_table_template = """
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
        self.current_table_uuid = uuid.int


    def add_record_or_table(self, time = datetime.now()):
        pass
