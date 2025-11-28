from vehicle import Driver

# Controller timestep used for Webots device enable and driver.step()
TIME_STEP = 16

# Initialize the high-level Driver and enable the receiver device
driver = Driver()
receiver = driver.getDevice("path_receiver")
receiver.enable(TIME_STEP)

print("CONTROLLER: Waiting for commands...")

# Print a single debug message the first time a packet is received
first_packet_received = False


# Main control loop: read incoming messages and apply steering/speed
while driver.step() != -1:

    # default commands
    steer_command = 0.0
    speed_command = 0.0

    # receive a packet if available
    if receiver.getQueueLength() > 0:
        if not first_packet_received:
            print("CONTROLLER: First packet received from supervisor.")
            first_packet_received = True
        message = receiver.getString()
        try:
            # message expected in format: "<steer>,<speed>"
            parts = message.split(",")
            steer_command = float(parts[0])
            speed_command = float(parts[1])
        except ValueError:
            # malformed messages are ignored
            pass

        # advance the receiver queue
        receiver.nextPacket()

    # apply commands to the Driver API
    driver.setSteeringAngle(steer_command)
    driver.setCruisingSpeed(speed_command)
