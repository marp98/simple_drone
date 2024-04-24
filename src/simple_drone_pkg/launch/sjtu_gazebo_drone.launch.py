import os
import random
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command
from launch_ros.actions import Node

def generate_launch_description():
    ####### DATA INPUT ##########
    urdf_file = 'sjtu_drone.urdf'
    package_description = "simple_drone_pkg"
    ####### DATA INPUT END ##########

    print("Fetching URDF ==>")
    robot_desc_path = os.path.join(get_package_share_directory(package_description), "urdf", urdf_file)

    # Robot State Publisher
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher_node',
        emulate_tty=True,
        parameters=[{'use_sim_time': True, 'robot_description': Command(['xacro ', robot_desc_path])}],
        output="screen"
    )

    # RVIZ Configuration
    rviz_config_dir = os.path.join(get_package_share_directory(package_description), 'rviz', 'rviz.rviz')
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        output='screen',
        name='rviz_node',
        parameters=[{'use_sim_time': True}],
        arguments=['-d', rviz_config_dir]
    )

    # Gazebo Configuration
    pkg_gazebo_ros = get_package_share_directory('gazebo_ros')
    simple_drone_pkg = get_package_share_directory('simple_drone_pkg')
    gazebo_models_path = os.path.join(simple_drone_pkg, 'models')
    os.environ['GAZEBO_MODEL_PATH'] = gazebo_models_path

    # Gazebo launch
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_gazebo_ros, 'launch', 'gazebo.launch.py')
        )
    )

    # Position and orientation
    position = [0.0, 0.0, 0.2]
    orientation = [0.0, 0.0, 0.0]

    # Base Name or robot
    robot_base_name = "sjtu_drone"
    entity_name = robot_base_name + "-" + str(int(random.random() * 100000))

    # Spawn ROBOT Set Gazebo
    spawn_robot = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        name='spawn_entity',
        output='screen',
        arguments=['-entity', entity_name,
                   '-x', str(position[0]), '-y', str(position[1]), '-z', str(position[2]),
                   '-R', str(orientation[0]), '-P', str(orientation[1]), '-Y', str(orientation[2]),
                   '-topic', '/robot_description']
    )

    # Create and return launch description object
    return LaunchDescription([
        robot_state_publisher_node,
        rviz_node,
        gazebo,
        spawn_robot
    ])