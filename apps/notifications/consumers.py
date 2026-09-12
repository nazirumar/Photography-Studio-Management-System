import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications."""

    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.group_name = f"notifications_{self.user.pk}"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

        # Send unread count on connect
        count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            "type": "unread_count",
            "count": count
        }))

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get("type") == "mark_read":
            notification_id = data.get("id")
            if notification_id:
                await self.mark_read(notification_id)
                count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    "type": "unread_count",
                    "count": count
                }))

    async def notification(self, event):
        """Send notification to WebSocket."""
        await self.send(text_data=json.dumps({
            "type": "notification",
            "data": event["data"]
        }))

    async def unread_count_update(self, event):
        """Send unread count update."""
        await self.send(text_data=json.dumps({
            "type": "unread_count",
            "count": event["count"]
        }))

    @database_sync_to_async
    def get_unread_count(self):
        from apps.notifications.models import Notification
        return Notification.objects.filter(user=self.user, is_read=False).count()

    @database_sync_to_async
    def mark_read(self, notification_id):
        from apps.notifications.models import Notification
        Notification.objects.filter(pk=notification_id, user=self.user).update(is_read=True)


class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time dashboard updates."""

    async def connect(self):
        self.user = self.scope["user"]
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.group_name = "dashboard_updates"

        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def dashboard_update(self, event):
        """Send dashboard update."""
        await self.send(text_data=json.dumps({
            "type": "dashboard_update",
            "data": event["data"]
        }))
