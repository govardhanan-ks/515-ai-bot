from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from uuid import uuid4
from datetime import datetime

class Auditor:
    def __init__(self):
        self.cluster = Cluster(['127.0.0.1'])
        self.session = self.cluster.connect('audit_ks')
    def audit(self, data):
        insert_query = """
            INSERT INTO audit_logs (id, username, action, timestamp, details)
            VALUES (%s, %s, %s, %s, %s)
            """
        self.session.execute(insert_query, (uuid4(), data['username'], data['action'], datetime.now(), data['details']))
        print(f"Audit log created for user {data['username']} with action {data['action']}")
