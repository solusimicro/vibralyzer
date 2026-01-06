def get_frequency_band(fs, rpm=None, static_band=None):
    """
    Hybrid band selector:
    - Jika rpm tersedia → RPM-based band
    - Jika tidak → static band (fallback)
    """

    if rpm and rpm > 0:
        fr = rpm / 60.0  # running frequency (Hz)

        return {
            "lf": (0.5 * fr, 3 * fr),
            "mf": (3 * fr, 10 * fr),
            "hf": (10 * fr, fs / 2),
        }

    # fallback
    if static_band:
        return static_band

    raise ValueError("No RPM and no static band provided")
