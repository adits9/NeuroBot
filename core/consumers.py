import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer

logger = logging.getLogger(__name__)

class NeuroConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Handle incoming WebSocket connection"""
        logger.info("Attempting WebSocket connection...")
        
        try:
            # Set the group name
            self.group_name = 'neurobot_live'
            
            # Accept the WebSocket connection
            await self.accept()
            logger.info("WebSocket connection accepted")
            
            # Add the channel to the group
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            logger.info(f"Added to group: {self.group_name}")
            
            # Send welcome message
            await self.send(text_data=json.dumps({
                'type': 'welcome',
                'message': 'Connected to NeuroBot live feed'
            }))
            
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}")
            if hasattr(self, 'channel_name'):
                try:
                    await self.channel_layer.group_discard(
                        self.group_name,
                        self.channel_name
                    )
                except:
                    pass
            await self.close(code=1000)
            raise StopConsumer()

    async def disconnect(self, close_code):
        """Handle client disconnection"""
        logger.info(f"WebSocket disconnecting with code: {close_code}")
        try:
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}")
        raise StopConsumer()

    async def receive(self, text_data=None, bytes_data=None):
        """Handle incoming messages"""
        if text_data:
            try:
                await self.send(text_data=json.dumps({
                    'type': 'echo',
                    'message': text_data
                }))
                logger.info(f"Echoed message: {text_data[:100]}...")
            except Exception as e:
                logger.error(f"Error in receive: {str(e)}")

    async def eeg_processed(self, event):
        # Event sent from view when EEG is processed
        payload = {
            'type': 'eeg_processed',
            'record_id': event.get('record_id'),
            'features': event.get('features'),
            'mood': event.get('mood'),
        }
        await self.send(text_data=json.dumps(payload))
