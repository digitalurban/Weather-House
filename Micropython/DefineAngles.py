from machine import Pin, PWM
import time

# --- Configuration ---
SERVO_PIN = 16  # The GPIO pin your servo is connected to.

# --- Initialization ---
try:
    # Initialize the PWM (Pulse Width Modulation) on the servo pin
    # 50Hz is the standard frequency for most hobby servos.
    servo_pwm = PWM(Pin(SERVO_PIN))
    servo_pwm.freq(50)
except Exception as e:
    print("Error initializing the servo. Is it on Pin 16?")
    print(e)
    # Use a dummy object if PWM fails, so the script doesn't crash.
    class DummyPWM:
        def duty_u16(self, val):
            pass
    servo_pwm = DummyPWM()

def servo(degrees):
    """
    Moves the servo to a specific angle in degrees.
    Converts the angle (0-180) into the required PWM duty cycle.
    """
    if not 0 <= degrees <= 180:
        print("Angle must be between 0 and 180.")
        return

    # Standard pulse widths for servos are ~500us (0 deg) to ~2500us (180 deg)
    # The total cycle for 50Hz is 20,000us.
    # duty_u16 wants a value from 0 to 65535.
    min_pulse_us = 500
    max_pulse_us = 2500

    # Calculate the pulse width in microseconds for the given angle
    pulse_us = min_pulse_us + (max_pulse_us - min_pulse_us) * (degrees / 180)

    # Convert the pulse width to a 16-bit duty cycle value
    duty = int((pulse_us / 20000) * 65535)

    # Send the signal to the servo
    servo_pwm.duty_u16(duty)
    print(f"Servo moved to {degrees}°")

# --- Main Loop ---
print("--- Servo Calibration Tool ---")
print("Enter an angle between 0 and 180 to move the servo.")
print("Type 'exit' to quit.")
print("-" * 30)

# Move to a neutral starting position
servo(90)

while True:
    try:
        # Get user input from the terminal
        command = input("Enter angle (0-180) or 'exit': ").strip().lower()

        if command == 'exit':
            # Stop the script and release the servo
            servo(90) # Return to neutral
            time.sleep(0.5)
            servo_pwm.deinit() # Turn off the PWM signal
            print("Exiting calibration tool.")
            break

        # Convert the input string to an integer
        angle = int(command)

        # Move the servo to the requested angle
        servo(angle)

    except ValueError:
        # This happens if the user types something that isn't a number
        print("Invalid input. Please enter a number between 0 and 180.")
    except Exception as e:
        print(f"An error occurred: {e}")
        break
