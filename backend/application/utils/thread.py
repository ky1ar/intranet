from threading import Thread


def send_push_async(push_service, user_id, title, body, data=None):
    Thread(
        target=push_service.send_to_user,
        kwargs={
            "user_id": user_id,
            "title": title,
            "body": body,
            "data": data,
        },
        daemon=True,
    ).start()
