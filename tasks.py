from celery import Celery
from scripts.auditor import Auditor

app = Celery("tasks", broker="redis://localhost:6379/0")


@app.task
def send_audit_log_to_db(data):
    try:    
        print("🔍 Task started with:", data)
        auditor = Auditor()
        auditor.audit(data)
        print("✅ Insert successful")
    except Exception as e:
        print("❌ Exception during DB insert:", e)


