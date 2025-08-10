import json
import logging
from typing import Optional, Dict, Any
import asyncio

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

from app.core.config import settings
from app.core.logging_config import get_logger
from app.api.v1.controller import MailerController
from app.models.email import EmailRequest

logger = get_logger(__name__)


class MQTTService:
    def __init__(self):
        self.client: Optional[mqtt.Client] = None
        self.connected = False
        self._loop = None
        self._setup_client()
        logger.info("MQTTService initialized")

    def _setup_client(self):
        logger.debug("Setting up MQTT client...")
        
        self.client = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2,
            client_id=settings.mqtt_client_id,
            clean_session=True
        )
        
        logger.debug(f"MQTT client created with ID: {settings.mqtt_client_id}")
        
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_publish = self._on_publish
        self.client.on_log = self._on_log
        self.client.on_subscribe = self._on_subscribe
        self.client.on_unsubscribe = self._on_unsubscribe
        
        logger.debug("MQTT callbacks configured")

        if settings.mqtt_username and settings.mqtt_password:
            self.client.username_pw_set(settings.mqtt_username, settings.mqtt_password)
            logger.debug(f"MQTT authentication configured for user: {settings.mqtt_username}")
        else:
            logger.debug("MQTT authentication not configured")

    def _on_log(self, client, userdata, level, buf):
        log_level = logging.DEBUG
        if level == mqtt.MQTT_LOG_ERR:
            log_level = logging.ERROR
        elif level == mqtt.MQTT_LOG_WARNING:
            log_level = logging.WARNING
        elif level == mqtt.MQTT_LOG_NOTICE:
            log_level = logging.INFO
        elif level == mqtt.MQTT_LOG_INFO:
            log_level = logging.INFO
        elif level == mqtt.MQTT_LOG_DEBUG:
            log_level = logging.DEBUG
            
        logger.log(log_level, f"MQTT System: {buf}")

    def _on_connect(self, client, userdata, flags, reason_code, *args):
        if reason_code == 0:
            self.connected = True
            logger.info(f"Connected to MQTT broker at {settings.mqtt_broker}:{settings.mqtt_port}")
            logger.debug(f"Connection flags: {flags}")
            logger.debug(f"Additional args: {args}")
            
            client.subscribe(settings.mqtt_topic)
            logger.info(f"Subscribed to topic: {settings.mqtt_topic}")
        else:
            logger.error(f"Failed to connect to MQTT broker. Reason code: {reason_code}")
            self.connected = False

    def _on_disconnect(self, client, userdata, reason_code, *args):
        self.connected = False
        logger.warning(f"Disconnected from MQTT broker. Reason code: {reason_code}")
        logger.debug(f"Disconnect args: {args}")

    def _on_subscribe(self, client, userdata, mid, granted_qos, *args):
        logger.info(f"Subscribed to topic with mid: {mid}, QoS: {granted_qos}")
        logger.debug(f"Subscribe args: {args}")

    def _on_unsubscribe(self, client, userdata, mid, *args):
        logger.info(f"Unsubscribed from topic with mid: {mid}")
        logger.debug(f"Unsubscribe args: {args}")

    def _on_message(self, client, userdata, msg):
        try:
            logger.info(f"Received message on topic: {msg.topic}")
            logger.debug(f"Message details - QoS: {msg.qos}, Retain: {msg.retain}, Mid: {msg.mid}")
            
            payload = json.loads(msg.payload.decode('utf-8'))
            logger.debug(f"Message payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            if self._loop and self._loop.is_running():
                logger.debug("Scheduling async message processing...")
                asyncio.run_coroutine_threadsafe(
                    self._process_message(msg.topic, payload, msg.mid), 
                    self._loop
                )
            else:
                logger.warning("Event loop not available, using sync processing")
                self._process_message_sync(msg.topic, payload, msg.mid)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON message: {e}")
            logger.debug(f"Raw message payload: {msg.payload}")
            self._send_nack(msg.topic, msg.mid, "Invalid JSON format")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self._send_nack(msg.topic, msg.mid, str(e))

    def _on_publish(self, client, userdata, mid, *args):
        logger.debug(f"Message published with mid: {mid}")
        logger.debug(f"Publish args: {args}")

    def _process_message_sync(self, topic: str, payload: Dict[str, Any], message_id: int):
        logger.info(f"Processing message {message_id} synchronously")
        try:
            email_request = EmailRequest(
                to=payload.get("to"),
                subject=payload.get("subject", ""),
                template=payload.get("template", "test"),
                context=payload.get("context", {})
            )
            
            logger.info(f"Message {message_id} would be processed for: {email_request.to}")
            logger.debug(f"Email request details: {email_request}")
            
            self._send_ack(topic, message_id, {"status": "queued"})
            
        except Exception as e:
            logger.error(f"Failed to process email request: {e}")
            self._send_nack(topic, message_id, str(e))

    async def _process_message(self, topic: str, payload: Dict[str, Any], message_id: int):
        logger.info(f"Processing message {message_id} asynchronously")
        try:
            email_request = EmailRequest(
                to=payload.get("to"),
                subject=payload.get("subject", ""),
                template=payload.get("template", "test"),
                context=payload.get("context", {})
            )
            
            logger.debug(f"Email request created: {email_request}")
            logger.info(f"Sending email for message {message_id} to: {email_request.to}")
            
            response = await MailerController.send_email(email_request)
            
            logger.info(f"Email sent successfully for message {message_id}")
            logger.debug(f"Email response: {response}")
            
            self._send_ack(topic, message_id, response)
            
        except Exception as e:
            logger.error(f"Failed to process email request: {e}")
            self._send_nack(topic, message_id, str(e))

    def _send_ack(self, topic: str, message_id: int, response: Any):
        try:
            ack_topic = f"{topic}/ack/{message_id}"
            ack_payload = {
                "status": "ack",
                "message_id": message_id,
                "response": response.dict() if hasattr(response, 'dict') else response
            }
            
            logger.debug(f"Sending ACK to topic: {ack_topic}")
            logger.debug(f"ACK payload: {json.dumps(ack_payload, indent=2, ensure_ascii=False)}")
            
            result = self.client.publish(ack_topic, json.dumps(ack_payload))
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"ACK sent for message {message_id}")
            else:
                logger.error(f"Failed to send ACK: MQTT error {result.rc}")
                
        except Exception as e:
            logger.error(f"Failed to send ACK: {e}")

    def _send_nack(self, topic: str, message_id: int, error: str):
        try:
            nack_topic = f"{topic}/nack/{message_id}"
            nack_payload = {
                "status": "nack",
                "message_id": message_id,
                "error": error
            }
            
            logger.debug(f"Sending NACK to topic: {nack_topic}")
            logger.debug(f"NACK payload: {json.dumps(nack_payload, indent=2, ensure_ascii=False)}")
            
            result = self.client.publish(nack_topic, json.dumps(nack_payload))
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.info(f"NACK sent for message {message_id}: {error}")
            else:
                logger.error(f"Failed to send NACK: MQTT error {result.rc}")
                
        except Exception as e:
            logger.error(f"Failed to send NACK: {e}")

    async def connect(self):
        logger.info(f"Connecting to MQTT broker: {settings.mqtt_broker}:{settings.mqtt_port}")
        try:
            self._loop = asyncio.get_running_loop()
            logger.debug("Event loop reference saved")
            
            logger.debug("Establishing MQTT connection...")
            self.client.connect(
                settings.mqtt_broker,
                settings.mqtt_port,
                keepalive=settings.mqtt_keepalive
            )
            
            logger.debug("Starting MQTT client loop...")
            self.client.loop_start()
            
            logger.debug("Waiting for connection...")
            timeout = 10
            while not self.connected and timeout > 0:
                await asyncio.sleep(0.1)
                timeout -= 0.1
            
            if not self.connected:
                raise Exception("Failed to connect to MQTT broker within timeout")
                
            logger.info("MQTT connection established successfully")
                
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

    async def disconnect(self):
        if self.client:
            logger.info("Disconnecting from MQTT broker...")
            try:
                logger.debug("Stopping MQTT client loop...")
                self.client.loop_stop()
                
                logger.debug("Disconnecting MQTT client...")
                self.client.disconnect()
                
                self.connected = False
                self._loop = None
                logger.info("MQTT disconnected successfully")
                
            except Exception as e:
                logger.error(f"Error during MQTT disconnect: {e}")

    async def publish(self, topic: str, payload: Dict[str, Any]):
        if not self.connected:
            raise Exception("Not connected to MQTT broker")
        
        logger.info(f"Publishing message to topic: {topic}")
        logger.debug(f"Message payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")
        
        message = json.dumps(payload)
        result = self.client.publish(topic, message)
        
        if result.rc != mqtt.MQTT_ERR_SUCCESS:
            error_msg = f"Failed to publish message: MQTT error {result.rc}"
            logger.error(f"{error_msg}")
            raise Exception(error_msg)
        
        logger.info(f"Message published successfully to topic {topic}")
        logger.debug(f"Message ID: {result.mid}")
        return result.mid
