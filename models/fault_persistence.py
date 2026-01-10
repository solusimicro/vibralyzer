from collections import defaultdict, deque

class FaultPersistence:
    def __init__(self, window=5):
        self.history = defaultdict(lambda: deque(maxlen=window))

    def update(self, asset, point, faults):
        key = f"{asset}:{point}"
        active = {f["fault"]: f for f in faults}
        self.history[key].append(active)

        persistent = []

        for fault, data in active.items():
            count = sum(
                1 for h in self.history[key]
                if fault in h
            )

            severity = data.get("severity", "LOW")
            if self._is_persistent(severity, count):
                persistent.append(data)

        return persistent

    def _is_persistent(self, severity, count):
        rules = {
            "LOW": 5,
            "MEDIUM": 3,
            "HIGH": 2,
            "CRITICAL": 1
        }
        return count >= rules.get(severity, 99)
