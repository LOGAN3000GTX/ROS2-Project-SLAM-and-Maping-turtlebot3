import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped
import math
import time

class NavigationGoalSender(Node):
    def __init__(self):
        super().__init__('navigation_goal_sender')
        
        self._action_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )
        
        # List of point (x, y, angle in degrees)
        self.waypoints = [
            (1.0, 0.0, 0),
            (1.0, 1.0, 90),
            (0.0, 1.0, 180),
            (2.0, 0.0, 0),
            (2.0, 2.0, 90),
            (2.0, 3.0, 170),
            (0.0, 0.0, 270),  # going to home
        ]
        self.current_waypoint = 0

        self.stop_seconds = 5

    def send_goal(self, x, y, yaw_deg):
        self.get_logger().info(f'goal: x={x}, y={y}, angle={yaw_deg}°')
        
        goal_msg = NavigateToPose.Goal()
        
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.get_clock().now().to_msg()
        
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0
        
        # Converting to quanternions
        yaw = math.radians(yaw_deg)
        pose.pose.orientation.z = math.sin(yaw / 2)
        pose.pose.orientation.w = math.cos(yaw / 2)
        
        goal_msg.pose = pose
        
        self._action_client.wait_for_server()
        
        future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().warn('Failed goal!')
            return
        
        self.get_logger().info('The goal accepted, driving...')

        result_future = goal_handle.get_result_async()

        result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback

        dist = feedback.distance_remaining
        
        self.get_logger().info(f'Left: {dist:.2f}m')

    def result_callback(self, future):
        self.get_logger().info('The point has been reachead, I am waiting {self.stop_seconds} seconds')
        
        time.sleep(self.stop_seconds)

        self.get_logger().info('Continue navigation path')
        self.current_waypoint += 1

        if self.current_waypoint < len(self.waypoints):
            wp = self.waypoints[self.current_waypoint]
            self.send_goal(wp[0], wp[1], wp[2])
        else:
            self.get_logger().info('Navigation completed!')

def main(args=None):
    rclpy.init(args=args)
    node = NavigationGoalSender()
    
    # Отправляем первую точку
    wp = node.waypoints[0]
    node.send_goal(wp[0], wp[1], wp[2])
    
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()