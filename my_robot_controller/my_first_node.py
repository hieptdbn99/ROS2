#!/usr/bin/env python3

import asyncio
import websockets
import json
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from threading import Thread

class WebSocketTurtle(Node):
    def __init__(self):
        super().__init__('websocket_turtle')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.get_logger().info('WebSocket Turtle Controller Started')

    async def handler(self, websocket, path):
        async for message in websocket:
            self.get_logger().info(f"Received: {message}")
            try:
                data = json.loads(message)  # Use json.loads instead of eval
                msg = Twist()
                msg.linear.x = float(data.get('linear', 0.0))
                msg.angular.z = float(data.get('angular', 0.0))
                self.publisher.publish(msg)
            except (json.JSONDecodeError, ValueError) as e:
                self.get_logger().error(f"Error parsing message: {e}")

async def start_websocket_server(node):
    """Start the WebSocket server"""
    server = await websockets.serve(node.handler, 'localhost', 8765)
    node.get_logger().info('WebSocket server started on ws://localhost:8765')
    # Keep the server running forever
    await asyncio.Future()  # Run forever

def main():
    rclpy.init()
    node = WebSocketTurtle()
    
    # Create a new event loop for the WebSocket server
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Start WebSocket server in a separate thread
    def run_websocket():
        loop.run_until_complete(start_websocket_server(node))
        loop.run_forever()
    
    websocket_thread = Thread(target=run_websocket, daemon=True)
    websocket_thread.start()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        loop.call_soon_threadsafe(loop.stop)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
