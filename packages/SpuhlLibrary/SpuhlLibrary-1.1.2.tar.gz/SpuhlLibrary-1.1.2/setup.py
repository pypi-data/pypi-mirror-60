from setuptools import setup

setup(
    name='SpuhlLibrary',
    version='1.1.2',
    packages=['tests', 'tests.IoTEdgeMessagePublisher', 'package', 'package.IoTEdgeMessagePublisher', 'package.Util'],
    url='https://github.com/sagerpascal/Spuhl_IoT_Solution',
    license='',
    author='Luca Staehli, Pascal Sager',
    author_email='pascal.sager@spuhl.com',
    description='Azure IoT Library from Spuhl GmbH',
    test_suite="tests",
    install_requires=['azure-iothub-device-client~=1.4.3']
)
