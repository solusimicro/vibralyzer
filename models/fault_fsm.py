class FaultFSM:
    def __init__(self):
        self.state = {}

    def update(self, key, alarm_code, faults):

        # ✅ INIT STATE
        prev = self.state.get(key, "NORMAL")

        if prev == "NORMAL":
            if alarm_code >= 2:
                self.state[key] = "WARNING"
            else:
                self.state[key] = "NORMAL"

        elif prev == "WARNING":
            if alarm_code >= 3 or faults:
                self.state[key] = "ALARM"
            elif alarm_code == 0:
                self.state[key] = "NORMAL"
            else:
                self.state[key] = "WARNING"

        elif prev == "ALARM":
            if alarm_code >= 4:
                self.state[key] = "TRIP"
            else:
                self.state[key] = "ALARM"

        elif prev == "TRIP":
            self.state[key] = "TRIP"  # reset manual only

        return self.state[key]

