# --- Importok ---
from vehicle import Driver
from controller import Keyboard

# --- Konstansok ---
TIME_STEP = 16

THROTTLE_STEP = 0.05 # 0 es 1 kozotti ertek
BRAKE_STEP = 0.1 # 0 es 1 kozotti ertek
STEERING_STEP = 0.03 # Radian
MAX_STEERING_ANGLE = 0.5 # Radian

# --- Inicializalas ---
driver = Driver()
keyboard = Keyboard()
keyboard.enable(TIME_STEP)

# --- HUD beallitasa ---
try:
    display = driver.getDevice("display")
except:
    display = None
    print("ERROR: 'display' nem talalhato")

font = "Arial"

# --- Alap ertekek beallitasa ---
throttle = 0.0
brake = 0.0
steering = 0.0
gear = 1 # Alapertelmezett fokozat: elore menet
is_gear_key_down = False
driver.setGear(gear)

print("↑↓ - gaz/fek, ←→ - kanyarodas, G - sebessegvalto, Space - kezifek")

# --- Esemenyek kezelese ---
while driver.step() != -1:
    key = keyboard.getKey()
    
    current_key_is_G = (key in (ord('G'), ord('g')))
    is_throttle_active = (key == Keyboard.UP)
    is_brake_active = (key == Keyboard.DOWN or key == ord(' '))
    is_steering_active = (key == Keyboard.LEFT or key == Keyboard.RIGHT)
    
    # --- Gazadas ---
    if is_throttle_active:
        throttle = min(1.0, throttle + THROTTLE_STEP)
        brake = 0.0
    
    # --- Fekezes ---
    elif is_brake_active:
        if key == Keyboard.DOWN:
            brake = min(1.0, brake + BRAKE_STEP)
        elif key == ord(' '):
            brake = 1.0
        
        throttle = 0.0

    # --- Kanyarodas ---
    if key == Keyboard.LEFT:
        steering = max(-MAX_STEERING_ANGLE, steering - STEERING_STEP)
    elif key == Keyboard.RIGHT:
        steering = min(MAX_STEERING_ANGLE, steering + STEERING_STEP)
        
    # --- Valto ---
    if current_key_is_G and not is_gear_key_down:
        
        if throttle == 0.0: # Csak akkor, ha allo helyzetben van
            gear = -gear
            driver.setGear(gear)
            brake = 0.0
            print("Fokozat:", "Eloremenet" if gear == 1 else "Hatramenet")
            
        is_gear_key_down = True
    
    elif not current_key_is_G:
        is_gear_key_down = False

    # --- Kormany visszaallitasa ---    
    if not is_steering_active:
        steering *= 0.90 

    # --- "Motorfek" szimulacioja ---
    if not is_throttle_active and not is_brake_active:
        throttle *= 0.98
        brake *= 0.9
        
    # --- Ertekek beallitasa ---
    driver.setSteeringAngle(steering)
    driver.setThrottle(throttle)
    driver.setBrakeIntensity(brake)

    # --- HUD ---
    if display:
        display.setColor(0x000000)
        display.fillRectangle(0, 0, display.getWidth(), 60)
        display.setColor(0xFFFFFF)
        display.setFont(font, 20, True)
        speed = driver.getCurrentSpeed()
        display.drawText(f"Sebesseg: {speed:.1f} km/h", 10, 10)
        display.drawText(f"Kormanyzas: {steering:.2f} rad", 10, 35)