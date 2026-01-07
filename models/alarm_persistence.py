class AlarmPersistence:
    def __init__(self, warn_count=3, alarm_count=2):
        self.warn_count = warn_count
        self.alarm_count = alarm_count
        self.counter = {}

    def update(self, key, status):
        if key not in self.counter:
            self.counter[key] = {"WARNING": 0, "ALARM": 0}

        if status == "WARNING":
            self.counter[key]["WARNING"] += 1
            self.counter[key]["ALARM"] = 0
            if self.counter[key]["WARNING"] >= self.warn_count:
                return "WARNING"

        elif status == "ALARM":
            self.counter[key]["ALARM"] += 1
            if self.counter[key]["ALARM"] >= self.alarm_count:
                return "ALARM"

        else:
            self.counter[key] = {"WARNING": 0, "ALARM": 0}
            return "NORMAL"

        return "NORMAL"
