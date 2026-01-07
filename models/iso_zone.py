def calculate_iso_zone(vel_rms):
    """
    ISO 10816 / 20816 velocity RMS classification (mm/s)
    Returns: (zone_code, zone_label)
    """

    try:
        vel = float(vel_rms)
    except (TypeError, ValueError):
        return 0, "UNKNOWN"

    if vel <= 2.8:
        return 1, "A"
    elif vel <= 4.5:
        return 2, "B"
    elif vel <= 7.1:
        return 3, "C"
    else:
        return 4, "D"
