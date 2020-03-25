import os, asyncio, threading, random, time
from dotenv import load_dotenv
from azure.iot.device.aio import IoTHubDeviceClient, ProvisioningDeviceClient
from azure.iot.device import MethodResponse
from lightcontroller-unicornhat import ColorController

load_dotenv()

id_scope = os.getenv('ID_SCOPE')
device_id = os.getenv('DEVICE_ID')
primary_key = os.getenv('PRIMARY_KEY')


def set_color(color):
    r = '0x' + color[0:2]
    g = '0x' + color[2:4]
    b = '0x' + color[4:6]

    r_value = int(r, 0)
    g_value = int(g, 0)
    b_value = int(b, 0)

    print('Updating color: r =', r_value, ', g =', g_value, ', b =', b_value)

    uh.set_all(r_value, g_value, b_value)
    uh.show()

async def main():
    # provision the device
    async def register_device():
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host='global.azure-devices-provisioning.net',
            registration_id=device_id,
            id_scope=id_scope,
            symmetric_key=primary_key,
        )

        return await provisioning_device_client.register()

    results = await asyncio.gather(register_device())
    registration_result = results[0]

    # build the connection string
    conn_str='HostName=' + registration_result.registration_state.assigned_hub + \
                ';DeviceId=' + device_id + \
                ';SharedAccessKey=' + primary_key

    # The client object is used to interact with your Azure IoT Central.
    device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

    # connect the client.
    print('Connecting')
    await device_client.connect()
    print('Connected')

    # Get the current color
    twin = await device_client.get_twin()
    print('Got twin: ', twin)

    try:
        desired_color = twin['reported']['color']
        set_color(desired_color)
    except Error:
        print("Couldn't load twin,")

    # listen for commands
    async def command_listener(device_client):
        while True:
            method_request = await device_client.receive_method_request()

            print('Call made to', method_request.name)

            color = method_request.payload
            
            print('payload', color)

            if isinstance(color, dict):
                color = color['color']

            print('payload', color)

            set_color(color)

            payload = {'result': True, 'data': color}
            method_response = MethodResponse.create_from_method_request(
                method_request, 200, payload
            )
            await device_client.send_method_response(method_response)

            # Write the color back as a property
            await device_client.patch_twin_reported_properties({'color':color})

    # async loop that controls the lights
    async def main_loop():
        global mode
        while True:
            await asyncio.sleep(1)

    listeners = asyncio.gather(command_listener(device_client))

    await main_loop()

    # Cancel listening
    listeners.cancel()

    # Finally, disconnect
    await device_client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())