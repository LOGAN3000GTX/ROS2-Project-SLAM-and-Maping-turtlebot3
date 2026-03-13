from setuptools import setup

package_name = 'my_tb3_project'

setup(
    name=package_name,
    version='0.0.1',
    packages=[package_name],
    install_requires=['setuptools'],
    entry_points={
        'console_scripts': [
            'slam_monitor = my_tb3_project.slam_launcher:main',
            'nav_goals = my_tb3_project.nav_goal_sender:main',
            'map_saver = my_tb3_project.map_saver:main',
        ],
    },
)