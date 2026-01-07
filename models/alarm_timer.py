import time

class AlarmTimer:
    def __init__(self, warn_delay=60, alarm_delay=30):
        """
        warn_delay  : detik sebelum WARNING valid
        alarm_delay : detik sebelum ALARM valid
        """
        self.warn_delay = warn_delay
        self.alarm_delay = alarm_delay
        self.timer = {}

    def update(self, key, status):
        now = time.time()

        if status not in ("WARNING", "ALARM"):
            self.timer.pop(key, None)
            return status

        if key not in self.timer:
            self.timer[key] = {
                "status": status,
                "start": now
            }
            return "NORMAL"

        prev = self.timer[key]

        # status berubah → reset timer
        if prev["status"] != status:
            self.timer[key] = {"status": status, "start": now}
            return "NORMAL"

        elapsed = now - prev["start"]

        if status == "WARNING" and elapsed >= self.warn_delay:
            return "WARNING"

        if status == "ALARM" and elapsed >= self.alarm_delay:
            return "ALARM"

        return "NORMAL"
