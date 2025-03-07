"""
Message queue processor for handling MQTT messages.
"""
import queue
import time
import traceback
from threading import Thread, Event

import config
from line_messenger import send_message
from logger import setup_logger

class MessageQueueProcessor(Thread):
    """
    Worker thread that processes messages from a queue.
    Ensures only one message is being sent to LINE at a time.
    """
    
    def __init__(self, message_queue=None):
        """
        Initialize the message queue processor.
        
        Args:
            message_queue (Queue): Queue for message processing
        """
        super().__init__(daemon=True)
        self.queue = message_queue or queue.Queue(maxsize=100)
        self.should_stop = Event()
        self.logger = setup_logger("msg_queue")
    
    def run(self):
        """Main processing loop."""
        self.logger.info("Message processor started")
        
        while not self.should_stop.is_set():
            try:
                # Get message from queue with timeout to check stop condition periodically
                try:
                    identifier, action, message = self.queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process background ping checks without logging
                if action == "bg_ping":
                    self.logger.debug(f"ID {identifier} | Background check, still alive.")
                    self.queue.task_done()
                    continue
                
                # Process actual message
                self.logger.info(f"ID {identifier} | Processing message with action: {action}")
                result = send_message(action, message)
                
                if result:
                    self.logger.info(f"ID {identifier} | Message sent successfully to LINE\n")
                else:
                    self.logger.critical(f"ID {identifier} | Failed to send message to LINE\n")
                
                # Mark task as done
                self.queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in message processor: {e}")
                self.logger.error(traceback.format_exc())
                # Ensure we mark the task as done even on error
                try:
                    self.queue.task_done()
                except:
                    pass
    
    def stop(self):
        """Signal the processor to stop."""
        self.should_stop.set()
    
    def enqueue_message(self, identifier, action, message, block=False, timeout=None):
        """
        Add a message to the processing queue.
        
        Args:
            identifier (str): Message identifier for logging
            action (str): Action type (call, cancel, debug)
            message (str): Message content
            block (bool): Whether to block if queue is full
            timeout (float): Timeout for blocking operation
            
        Returns:
            bool: True if message was added to queue, False otherwise
        """
        try:
            self.queue.put((identifier, action, message), block=block, timeout=timeout)
            return True
        except queue.Full:
            self.logger.error(f"ID {identifier} | Message queue is full! Dropping message.")
            return False
            
    def wait_completion(self):
        """
        Wait for all queued messages to be processed.
        """
        self.logger.info("Waiting for message queue to empty...")
        self.queue.join()
        self.logger.info("All messages processed")