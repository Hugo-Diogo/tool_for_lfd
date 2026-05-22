import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, TransformStamped
from sensor_msgs.msg import Joy


"""
The structure is:

-Imports
-give a name to the node
-create a publisher and subscribers and at the third position we write self.(name subscriber)
-Write functions with the name of each subscriber
-For the publisher we can create simply by writing new_msg = PoseStamped() and then filling the data of the message and then publishing it with self.pub.publish(new_msg)

- In order to use signals between readings we can attached a new bool variable to the class self by writting self.(name variable) = FALSE.

"""
x_init = 0.0
y_init = 0.0
z_init = 0.0

cx_init = 0.0
cy_init = 0.0
cz_init = 0.0
cw_init = 1.0

class MyNode(Node):

    def __init__(self):

        super().__init__('relay_node')

        #Special signal to turn on the relay from the OptiTrack data to the Robot
        self.special_button = False

        """
        First Subscriber - OptiTrack
        type of message -> PoseStamped
        topic name -> /optitrack/pose
        """
        self.sub_optitrack = self.create_subscription(
            PoseStamped,
            '/optitrack/pose',
            self.optitrack_pose_callback,
            10
        )

        """"
        Second Subscriber - ESP32 Buttons
        type of message -> Joy
        topic name -> /esp32/buttons
        """
        self.sub_esp32 = self.create_subscription(
            Joy,
            '/esp32/buttons',
            self.esp32_buttons_callback,
            10
        )

        """
        Publisher - Relay
        Type of message -> TransformStamped
        Topic name -> /relay/pose
        """
        self.pub = self.create_publisher(
            TransformStamped,   
            '/relay/pose',
            10
        )
        


        self.get_logger().info("Relay Node Initialized")


    def optitrack_pose_callback(self, msg):

        x = msg.pose.position.x
        y = msg.pose.position.y
        z = msg.pose.position.z

        cx = msg.pose.orientation.x
        cy = msg.pose.orientation.y
        cz = msg.pose.orientation.z
        cw = msg.pose.orientation.w


        self.get_logger().info(f"OptiTrack Pose: x={x}, y={y}, z={z} | orientation: x={cx}, y={cy}, z={cz}, w={cw}")

        #Create the difference between them

        dx = x - x_init
        dy = y - y_init
        dz = z - z_init 

        qcx = cx - cx_init
        qcy = cy - cy_init
        qcz = cz - cz_init
        qcw = cw - cw_init

        if self.special_button:
            #Create the new message to publish

            new_msg = TransformStamped()
            new_msg.header.stamp = self.get_clock().now().to_msg()
            new_msg.header.frame_id = 'world'
            new_msg.child_frame_id = 'robot'

            new_msg.transform.translation.x = dx
            new_msg.transform.translation.y = dy
            new_msg.transform.translation.z = dz

            new_msg.transform.rotation.x = qcx
            new_msg.transform.rotation.y = qcy
            new_msg.transform.rotation.z = qcz
            new_msg.transform.rotation.w = qcw

            self.pub.publish(new_msg)

        else:
            new_msg = TransformStamped()
            new_msg.header.stamp = self.get_clock().now().to_msg()
            new_msg.header.frame_id = 'world'
            new_msg.child_frame_id = 'robot'

            new_msg.transform.translation.x = 0
            new_msg.transform.translation.y = 0
            new_msg.transform.translation.z = 0

            new_msg.transform.rotation.x = 0
            new_msg.transform.rotation.y = 0
            new_msg.transform.rotation.z = 0
            new_msg.transform.rotation.w = 0

            self.pub.publish(new_msg)


    def esp32_buttons_callback(self, msg):

        button_1 = msg.buttons[0]


        if button_1 == 1:  # If button 1 is pressed
            self.special_button = True
            button_2 = msg.buttons[1]
            button_3 = msg.buttons[2]
            button_4 = msg.buttons[3]
            self.get_logger().info(f"B1: {button_1}, B2: {button_2}, B3: {button_3}, B4: {button_4} - Special button activated!")
        else:
            self.special_button = False
            button_2 = 0
            button_3 = 0
            button_4 = 0
            self.get_logger().info(f"B1: {button_1}, B2: {button_2}, B3: {button_3}, B4: {button_4} - Special button deactivated.")

        


def main(args=None):

    rclpy.init(args=args)

    node = MyNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()




    
