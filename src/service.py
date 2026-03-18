from src.models import Notification
from src.extensions import socketio

def send_notification(receiver_id, message, notification_type, ticket_id=None):
    print(f"[send_notification] émission vers room=user_{receiver_id}, message={message}")
    Notification.create(
        user_id=receiver_id,
        message=message,
        type=notification_type,
        ticket_id=ticket_id
    )
    socketio.emit(
        "new_notification",
        {"message": message, "notification_type": notification_type, "ticket_id": ticket_id},
        room=f"user_{receiver_id}",
    )
    print(f"[send_notification] émis ✓")