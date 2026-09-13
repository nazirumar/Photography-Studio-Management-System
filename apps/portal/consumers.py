import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class ClientPortalConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for client portal real-time notifications.

    Sends booking updates, payment confirmations, and gallery notifications.
    Scoped to a single client via portal ClientUser.
    """

    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        client_id = await self.get_client_id()
        if not client_id:
            await self.close()
            return

        self.group_name = f"portal_{client_id}"
        self.client_id = client_id

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            "type": "unread_count",
            "count": count,
        }))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "mark_read":
            notification_id = data.get("id")
            if notification_id:
                await self.mark_read(notification_id)
                count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    "type": "unread_count",
                    "count": count,
                }))
        elif data.get("type") == "ping":
            await self.send(text_data=json.dumps({"type": "pong"}))

    async def notification(self, event):
        await self.send(text_data=json.dumps({
            "type": "notification",
            "data": event["data"],
        }))

    async def booking_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "booking_update",
            "data": event["data"],
        }))

    async def payment_confirmed(self, event):
        await self.send(text_data=json.dumps({
            "type": "payment_confirmed",
            "data": event["data"],
        }))

    async def gallery_ready(self, event):
        await self.send(text_data=json.dumps({
            "type": "gallery_ready",
            "data": event["data"],
        }))

    async def unread_count_update(self, event):
        await self.send(text_data=json.dumps({
            "type": "unread_count",
            "count": event["count"],
        }))

    @database_sync_to_async
    def get_client_id(self):
        from apps.portal.models import ClientUser
        try:
            cu = ClientUser.objects.get(pk=self.user.pk)
            if cu.client:
                return str(cu.client.pk)
        except ClientUser.DoesNotExist:
            pass
        return None

    @database_sync_to_async
    def get_unread_count(self):
        from apps.notifications.models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            staff_user = User.objects.get(email=self.user.email)
            return Notification.objects.filter(user=staff_user, is_read=False).count()
        except User.DoesNotExist:
            return 0

    @database_sync_to_async
    def mark_read(self, notification_id):
        from apps.notifications.models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            staff_user = User.objects.get(email=self.user.email)
            Notification.objects.filter(pk=notification_id, user=staff_user).update(is_read=True)
        except User.DoesNotExist:
            pass
