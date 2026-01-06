import math

def iso_zone(acc_rms_g, dominant_freq):
    """
    ISO 10816 / 20816 (simplified)
    Return zone A/B/C/D
    """

    if dominant_freq <= 0:
        return "UNKNOWN"

    # g → m/s²
    acc_ms2 = acc_rms_g * 9.81

    # velocity RMS (m/s)
    vel_ms = acc_ms2 / (2 * math.pi * dominant_freq)

    # mm/s
    vel_mm_s = vel_ms * 1000

    if vel_mm_s < 1.8:
        return "A"
    elif vel_mm_s < 4.5:
        return "B"
    elif vel_mm_s < 7.1:
        return "C"
    else:
        return "D"
#Nilai threshold = mesin rotating umum (Class II–III)