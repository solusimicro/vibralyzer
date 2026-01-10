# models/fault_diagnostic.py

def detect_fault_with_confidence(features: dict):
    """
    Rule-based fault confidence (Bearing focused – early detection friendly)
    """

    score = 0.0
    evidence = []

    # =========================
    # 1️⃣ HF RMS (Early damage)
    # =========================
    hf = features.get("acc_hf_rms_g", 0)
    if hf >= 0.6:
        score += 0.30
        evidence.append("HF_RMS_ALARM")
    elif hf >= 0.3:
        score += 0.15
        evidence.append("HF_RMS_WARNING")

    # =========================
    # 2️⃣ Envelope Kurtosis
    # =========================
    kurt = features.get("envelope_kurtosis", 0)
    if kurt >= 5.0:
        score += 0.30
        evidence.append("ENV_KURT_HIGH")
    elif kurt >= 3.5:
        score += 0.15
        evidence.append("ENV_KURT_WARN")

    # =========================
    # 3️⃣ Bearing Energy Ratio
    # =========================
    ber = features.get("bearing_energy_ratio", 0)
    if ber >= 0.35:
        score += 0.20
        evidence.append("BEARING_ENERGY_HIGH")
    elif ber >= 0.2:
        score += 0.10
        evidence.append("BEARING_ENERGY_WARN")

    # =========================
    # 4️⃣ Crest Factor
    # =========================
    cf = features.get("crest_factor", 0)
    if cf >= 6.0:
        score += 0.10
        evidence.append("CREST_HIGH")
    elif cf >= 4.0:
        score += 0.05
        evidence.append("CREST_WARN")

    # =========================
    # 5️⃣ Spectral Entropy
    # =========================
    se = features.get("spectral_entropy", 0)
    if se >= 6.0:
        score += 0.10
        evidence.append("ENTROPY_HIGH")

    # =========================
    # NORMALIZE
    # =========================
    confidence = min(score, 1.0)

    if confidence >= 0.7:
        severity = "HIGH"
    elif confidence >= 0.4:
        severity = "MEDIUM"
    elif confidence >= 0.2:
        severity = "LOW"
    else:
        return []

    return [{
        "fault": "BEARING_FAULT",
        "confidence": round(confidence, 2),
        "severity": severity,
        "evidence": evidence
    }]


