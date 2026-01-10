def evaluate_alarm(alarm_status, health_score, faults):
    alarm_code = alarm_status

    # Rule 1: Health-based escalation
    if health_score < 0.6:
        alarm_code = max(alarm_code, 1)

    if health_score < 0.4:
        alarm_code = max(alarm_code, 2)

    # Rule 2: Fault-based override
    if any(
        f["fault"] == "BEARING_DEFECT" and f["confidence"] > 0.8
        for f in faults
    ):
        alarm_code = max(alarm_code, 2)

    if any(
        f["fault"] == "BEARING_DEFECT" and f["confidence"] > 0.95
        for f in faults
    ):
        alarm_code = max(alarm_code, 3)

    return alarm_code

