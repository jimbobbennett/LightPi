import os, asyncio, threading, random, time, json, base64
from dotenv import load_dotenv
from azure.iot.device.aio import IoTHubDeviceClient, ProvisioningDeviceClient
from azure.iot.device import MethodResponse
from lightcontrollerws281x import LightController_WS281x
#from lightcontrollerunicornhat import LightController_UnicornHat
from hexcolor import HexColor

load_dotenv()

id_scope = os.getenv('ID_SCOPE')
device_id = os.getenv('DEVICE_ID')
primary_key = os.getenv('PRIMARY_KEY')
light_type = os.getenv('LIGHT_TYPE')
pixel_count = int(os.getenv('PIXEL_COUNT'))

def ws281x():
    return LightController_WS281x(pixel_count)

controllers = {
    'ws281x' : ws281x#,
#    'Unicorn pHAT' : unicorn_phat
}


# def unicorn_phat():
#     return LightController_UnicornHat(pixel_count)

light_controller = controllers[light_type]()

frame_index = 0
frames = []
run_frames = False
loop_frames = True
frame_sleep_max_resolution = 0.1

def convert_string_to_color_dict(color):
    if isinstance(color, dict):
        return color
    else:
        return {'color': color}

def convert_to_timed_frames(colors):
    mapped_color_values = map(lambda x: convert_string_to_color_dict(x), colors['colors'])
    color_values = list(mapped_color_values)
    for color_value in color_values:
        color_value['frame_time'] = colors['frame_rate']
    return color_values

def handle_color_frames(colors, loop):
    global frames
    global run_frames
    global loop_frames
    global frame_index

    frames = colors
    frame_index = 0
    run_frames = True
    loop_frames = loop

def set_color_from_frame(frame):
    try:
        # A frame can be a single hex color value, a JSON doc with a single field called color,
        # # or an array of hex color values in a field called colors
        frame = convert_string_to_color_dict(frame)

        # check for single color
        if 'color' in frame:
            light_controller.set_single_color(HexColor(frame['color']))
        else:
            mapped_colors = map(lambda x: HexColor(x), frame['colors']) 
            light_controller.set_multiple_colors(list(mapped_colors))

        print('Color set from frame')
    except Exception as e:
        print('Error setting colors:', e)

def handle_multiple_colors(colors):
    if 'frame_rate' in colors:
        # Handle colors with timed frames
        color_values = convert_to_timed_frames(colors)
        loop = True
        if 'loop' in colors:
            loop = colors['loop']   
        handle_color_frames(color_values, loop)
    else:
        # check for frame times agains each item
        color_values = colors['colors']
        if 'frame_time' in color_values[0]:
            loop = True
            if 'loop' in colors:
                loop = colors['loop']   
            handle_color_frames(color_values, loop)
        else:
            set_color_from_frame(colors)

async def set_color(request):
    run_frames = False

    # Hacky thread safety - sleep long enough for the light loop to stop processing frames
    await asyncio.sleep(frame_sleep_max_resolution * 5)

    try:
        # If the request is JSON then it'll come as a dictionary
        # Otherwise it's a single color value
        if isinstance(request, dict):
            # check for single color
            if 'color' in request:
                set_color_from_frame(request)
            else:
                handle_multiple_colors(request)
        else:
            set_color_from_frame(request)
    except Exception as e:
        print('Error setting colors:', e)

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
        encoded_desired_color = twin['reported']['encoded_color']
        print('Encoded desired color:', encoded_desired_color)
        decoded_bytes = base64.b64decode(encoded_desired_color)
        payload = str(decoded_bytes, "utf-8")

        try:
            parsed = json.loads(payload)
            payload = parsed
        except:
            pass

        await set_color(payload)
    except Exception as e:
        print("Couldn't load twin:", e)

    async def frame_loop():
        global frame_index
        global frames
        global run_frames
        global loop_frames

        while True:
            if run_frames:
                current_frame = frames[frame_index]
                frame_time = current_frame['frame_time']
                # Do the current frame
                set_color_from_frame(current_frame)

                # prep the next frame
                frame_index = frame_index + 1
                if frame_index >= len(frames):
                    if loop_frames:
                        frame_index = 0
                    else:
                        run_frames = False

                if run_frames:
                    # wait for the next frame, checking if we need to stop
                    current_wait = 0.0
                    to_wait = min(frame_sleep_max_resolution, frame_time)
                    while (current_wait < frame_time) and run_frames:
                        await asyncio.sleep(to_wait)
                        to_wait = min(frame_sleep_max_resolution, frame_time - current_wait)
                        current_wait = current_wait + to_wait
            else:
                await asyncio.sleep(frame_sleep_max_resolution)

    # listen for commands
    async def command_listener(device_client):
        while True:
            method_request = await device_client.receive_method_request()

            print('Call made to', method_request.name)

            payload = method_request.payload
            
            print('payload', payload)

            try:
                parsed = json.loads(payload)
                payload = parsed
            except:
                pass

            print('parsed payload', payload)

            await set_color(payload)

            response_payload = {'result': True, 'data': payload}
            method_response = MethodResponse.create_from_method_request(
                method_request, 200, response_payload
            )
            await device_client.send_method_response(method_response)

            # Write the color back as a property
            # encode the data as base64 as arrays are not supported in device twins
            json_string = json.dumps(payload)
            encoded = base64.b64encode(json_string.encode("utf-8")).decode('ascii')
            patch = {'encoded_color' : encoded}

            print('Patch:', patch)
            await device_client.patch_twin_reported_properties(patch)

    # async loop that controls the lights
    async def main_loop():
        while True:
            await asyncio.sleep(1)

    listeners = asyncio.gather(command_listener(device_client), frame_loop())

    await main_loop()

    # Cancel listening
    listeners.cancel()

    # Finally, disconnect
    await device_client.disconnect()

if __name__ == '__main__':
    asyncio.run(main())