def generate_recommendation(faults):
    """
    faults = list of persistent fault dict
    """
    if not faults:
        return None

    # Ambil fault paling kritis
    fault = max(
        faults,
        key=lambda f: (
            ["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(f["severity"]),
            f.get("confidence", 0)
        )
    )

    severity = fault["severity"]
    fault_type = fault["fault"]

    if fault_type == "BEARING_FAULT":
        if severity == "MEDIUM":
            return {
                "priority": "MEDIUM",
                "maintenance_type": "INSPECTION",
                "recommended_in_days": 14,
                "action": "Periksa kondisi bearing dan pelumasan",
                "notes": "Indikasi awal kerusakan bearing terdeteksi konsisten"
            }

        if severity == "HIGH":
            return {
                "priority": "HIGH",
                "maintenance_type": "PLANNED_REPLACEMENT",
                "recommended_in_days": 7,
                "action": "Rencanakan penggantian bearing",
                "notes": "Degradasi bearing meningkat"
            }

        if severity == "CRITICAL":
            return {
                "priority": "CRITICAL",
                "maintenance_type": "IMMEDIATE_SHUTDOWN",
                "recommended_in_days": 0,
                "action": "Hentikan mesin dan ganti bearing",
                "notes": "Risiko kegagalan bearing tinggi"
            }

    # Default fallback
    return {
        "priority": severity,
        "maintenance_type": "MONITORING",
        "recommended_in_days": 30,
        "action": "Pantau kondisi mesin",
        "notes": "Anomali terdeteksi namun belum spesifik"
    }

