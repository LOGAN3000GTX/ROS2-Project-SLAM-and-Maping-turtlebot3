import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
import subprocess
import os
from datetime import datetime

class MapSaver(Node):
    def __init__(self):
        super().__init__('map_saver')
        
        self.map_sub = self.create_subscription(
            OccupancyGrid,
            '/map',
            self.map_callback,
            10
        )
        
        self.last_save = 0
         
        
        self.get_logger().info('Map Saver is ready!')

    def map_callback(self, msg):
        now = self.get_clock().now().nanoseconds / 1e9
        
        if now - self.last_save > self.save_interval:
            self.save_map()
            self.last_save = now

    def save_map(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        map_name = f'/tmp/map_{timestamp}'
        
        try:
            subprocess.run([
                'ros2', 'run', 'nav2_map_server', 'map_saver_cli',
                '-f', map_name
            ], timeout=10)
            
            self.get_logger().info(f'map save{map_name}.yaml')
        except Exception as e:
            self.get_logger().error(f'Error saved: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = MapSaver()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()