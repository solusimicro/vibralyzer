def evaluate_alarm(
    iso_zone_code,
    faults,
    health_index
):
    """
    Returns:
        alarm_code (int): 0..3
        alarm_label (str)
    """

    # Default
    alarm_code = 0
    alarm_label = "NORMAL"

    max_conf = max(
        [f.get("confidence", 0) for f in faults],
        default=0
    )

    # =========================
    # HEALTH OVERRIDE
    # =========================
    if health_index < 0.4:
        return 3, "TRIP"
    elif health_index < 0.6:
        alarm_code = max(alarm_code, 2)

    # =========================
    # ISO ZONE BASED
    # =========================
    if iso_zone_code == 1:  # A
        if faults and max_conf >= 0.7:
            alarm_code = max(alarm_code, 1)

    elif iso_zone_code == 2:  # B
        if faults and max_conf >= 0.7:
            alarm_code = max(alarm_code, 2)
        else:
            alarm_code = max(alarm_code, 1)

    elif iso_zone_code == 3:  # C
        if faults and max_conf >= 0.5:
            alarm_code = max(alarm_code, 2)

    elif iso_zone_code == 4:  # D
        return 3, "TRIP"

    # =========================
    # LABEL MAP
    # =========================
    label_map = {
        0: "NORMAL",
        1: "WARNING",
        2: "ALARM",
        3: "TRIP"
    }

    return alarm_code, label_map[alarm_code]
