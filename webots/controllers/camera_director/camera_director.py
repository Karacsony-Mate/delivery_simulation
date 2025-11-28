from controller import Supervisor

def main():
    supervisor = Supervisor()
    timestep = int(supervisor.getBasicTimeStep())

    viewpoint_node = supervisor.getFromDef("MAIN_VIEWPOINT")
    
    if viewpoint_node is None:
        print("CAMERA_DIRECTOR: ERROR! 'DEF MAIN_VIEWPOINT Viewpoint' not found.")
        return

    vp_pos = viewpoint_node.getField("position")
    vp_rot = viewpoint_node.getField("orientation")
    vp_follow = viewpoint_node.getField("follow")

    print("CAMERA_DIRECTOR: Started.")

    shots = [
        {
            "time": 0.0,
            "pos": [-370, 312, 102],
            "rot": [0.196, 0.188, -0.962, 1.65],
            "follow": "",
            "triggered": False
        },
        {
            "time": 23.5,
            "pos": [-256, -36, 45],
            "rot": [0.169, -0.0654, -0.983, 3.87],
            "follow": "",
            "triggered": False
        },
        {
            "time": 30.0,
            "pos": [-243, -215, 36.7],
            "rot": [0.139, -0.0843, -0.987, 4.22],
            "follow": "",
            "triggered": False
        }
    ]

    while supervisor.step(timestep) != -1:
        current_time = supervisor.getTime()

        for shot in shots:
            if not shot["triggered"] and current_time >= shot["time"]:
                print(f"CAMERA_DIRECTOR: changing to {shot['time']} second view.")
                
                if shot.get("pos"):
                    vp_pos.setSFVec3f(shot["pos"])
                
                if shot.get("rot"):
                    vp_rot.setSFRotation(shot["rot"])
                
                if "follow" in shot:
                    vp_follow.setSFString(shot["follow"])
                
                shot["triggered"] = True

if __name__ == "__main__":
    main()