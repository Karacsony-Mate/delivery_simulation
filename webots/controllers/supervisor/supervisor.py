# --- Importok ---
from controller import Supervisor
import math

# --- Konstansok ---
TIME_STEP = 16

PICKUP_DISTANCE = 4.5 # Meter
DROPOFF_DISTANCE = 4.5 # Meter

TESLA_DEF = "TESLA"
PACKAGE_DEF = "PACKAGE"
MARKER_DEF = "MARKER"

# --- Inicializalas ---
supervisor = Supervisor()

tesla = supervisor.getFromDef(TESLA_DEF)
package = supervisor.getFromDef(PACKAGE_DEF)
marker = supervisor.getFromDef(MARKER_DEF)

if tesla is None or package is None or marker is None:
    print("ERROR: Hianyzo NODE vagy DEF nev")
    exit(1)
    
has_package = False
delivered = False

# --- Jelolo szin reset --- 
marker_color_field = marker.getField("color")
marker_color_field.setSFColor([1, 0, 0]) # Piros

# --- Tavolsag meghatarozasa ---
def distance(a, b):
    return math.sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

# --- Esemenyek kezelese ---
while supervisor.step(TIME_STEP) != -1:
    # --- Poziciok lekerese ---
    tesla_pos = tesla.getPosition()
    package_pos = package.getPosition()
    marker_pos = marker.getPosition()
    
    if delivered: # Kiszallitas utan
        continue
        
    if not has_package and distance(tesla_pos, package_pos) < PICKUP_DISTANCE: # Csomag felvetele
        print("Csomag felveve!")
        has_package = True
        package.getField("translation").setSFVec3f([0, 0, -10]) # Kikuldjuk a vilagbol

    elif has_package and distance(tesla_pos, marker_pos) < DROPOFF_DISTANCE: # Csomag leszallitasa
        print("Csomag kiszallitva!")
        has_package = False
        delivered = True
        marker_color_field.setSFColor([0, 1, 0]) # Zold
