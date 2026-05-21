#!/usr/bin/env python3

"""
For the ESP32 Buttons Node I will use a type of node called Joy that has specific data for buttons, time stamp, frame_id and axes (that it is not needed)
You shall find more information about this frame here -> https://docs.ros2.org/foxy/api/sensor_msgs/msg/Joy.html

"""




import serial
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy


PORT = '/dev/cu.usbserial-AI055XSA'
BAUD = 921600


class ESP32ButtonsNode(Node):

    def __init__(self):
        # Name of the ROS2 Node -> /esp32/buttons
        super().__init__('esp32_buttons_node')

        # Publisher ROS2
        self.pub = self.create_publisher(
            Joy,
            '/esp32/buttons',
            10
        )

        # Porta serial
        self.ser = serial.Serial(
            PORT,
            BAUD,
            timeout=0.01
        )

        # Timer a 200 Hz
        self.timer = self.create_timer(
            0.005,
            self.read_serial
        )

# if needed, inside self.last_long_time there is an object rclpy.time.Time to convert to ROS2 message we need to add .to_msg()
        self.last_log_time = self.get_clock().now()

        # Same as print but in ROS2
        self.get_logger().info("ESP32 Buttons Node iniciado")

    def read_serial(self):
#-------------------------------------------------------------------------------------data reading
        # Read data from Serial
        data = self.ser.read(3)
#-------------------------------------------------------------------------------------data validation
        if len(data) != 3:
            return

        # This is the defined structure where data = [START][TYPE][BUTTONS]
        start = data[0]
        msg_type = data[1]
        buttons = data[2]

        # If the first byte is not correct we can conclude that the frame is invalid. This is called a flag in communication protocols.
        if start != 0xAA:
            return

        # To distinguish buttons from images we create a data type byte, in the case of the buttons this byte is equal to 0x01
        if msg_type == 0x01:

            now = self.get_clock().now()

            # Now we need to separete the value of each button from the frame -> [BUTTONS] = [0 0 0 0 b4 b3 b2 b1]
            # [0 0 0 0 b4 b3 b2 b1] >> 1 = [0 0 0 0 0 b4 b3 b2] & 00000001 = b2
            b1 = (buttons >> 0) & 1 # This button will be responsible to turn on or off the data collection
            b2 = (buttons >> 1) & 1
            b3 = (buttons >> 2) & 1
            b4 = (buttons >> 3) & 1
#-------------------------------------------------------------------------------------creating the ROS2 topic
            msg = Joy()

            msg.header.frame_id = "TOOL"
            

            
            #time of my computer clock
            msg.header.stamp = self.get_clock().now().to_msg()


            # Buttons
            msg.buttons = [b1, b2, b3, b4]

#-------------------------------------------------------------------------------------publishing
            self.pub.publish(msg)

            # Log 1x por segundo

#-------------------------------------------------------------------------------------Debugging

            self.get_logger().info(
                f"B1:{b1} B2:{b2} B3:{b3} B4:{b4}"
            )
            self.last_log_time = now


def main(args=None):

    rclpy.init(args=args)

    node = ESP32ButtonsNode()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    node.ser.close()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
    