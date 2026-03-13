import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Twist
import subprocess

class SLAMMonitor(Node):
    def __init__(self):
        super().__init__('slam_monitor')
        
        self.map_sub = self.create_subscription(
            OccupancyGrid, '/map', self.map_callback, 10)
        
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.timer = self.create_timer(0.5, self.explore)
        
        self.map_saved = False
        
        self.get_logger().info('SLAM Monitor is ready!')

    def map_callback(self, msg):

        known = sum(1 for cell in msg.data if cell != -1)
        total = len(msg.data)
        percent = 100 * known // total

        self.get_logger().info(
            f'map: {msg.info.width}x{msg.info.height} | '
            f'researched: {percent}%'
        )

        # Autosaving wheh map will reasrch on 70%
        if percent >= 60 and not self.map_saved:
            self.map_saved = True
            self.stop_robot()
            self.save_map()

    def explore(self):
        
        if not self.map_saved:
            msg = Twist()
            msg.angular.z = 0.3
            msg.linear.x = 0.1
            self.cmd_pub.publish(msg)

    def stop_robot(self):
        
        stop = Twist()
        self.cmd_pub.publish(stop)
        self.get_logger().info('Robot stoped')

    def save_map(self):
        
        self.get_logger().info('Saving map')
        try:
            subprocess.run([
                'ros2', 'run', 'nav2_map_server', 'map_saver_cli',
                '-f', '/home/amksegun/my_finished_map'
            ], timeout=15)
            self.get_logger().info('Map saved: ~/my_finished_map.yaml')
        except Exception as e:
            self.get_logger().error(f'Error save {e}')

def main(args=None):
    rclpy.init(args=args)
    node = SLAMMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.stop_robot()
        node.get_logger().info('Process has stoped')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()