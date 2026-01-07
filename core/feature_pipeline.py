from models.fault_diagnostic import detect_fault_with_confidence
from models.alarm_matrix import evaluate_alarm
from core.scada_publisher import publish_scada_features
from features.feature_extractor import process_signal
from models.iso_zone import calculate_iso_zone
from models.alarm_persistence import AlarmPersistence
from models.fault_fsm import FaultFSM
from models.alarm_timer import AlarmTimer
from models.maintenance_recommendation import MaintenanceRecommender


class FeaturePipeline:

    def __init__(self):
        self.alarm_persistence = AlarmPersistence(warn_count=3, alarm_count=2)
        self.fsm = FaultFSM()
        self.alarm_timer = AlarmTimer(warn_delay=60, alarm_delay=30)
        self.recommender = MaintenanceRecommender()   # 👈 STEP 6

    def process(self, signal, fs, asset, point, rpm=None):

        # 1️⃣ Feature extraction
        features = process_signal(
            {"asset": asset, "point": point},
            {"signal": signal, "fs": fs, "rpm": rpm}
        )

        # 2️⃣ Fault diagnostic
        faults = detect_fault_with_confidence(features)

        # 3️⃣ ISO Zone
        vel_rms = features.get("velocity", {}).get("rms_mm_s", 0.0)
        iso_code, iso_label = calculate_iso_zone(vel_rms)

        # 4️⃣ Alarm matrix
        alarm_code, raw_status = evaluate_alarm(
            iso_zone_code=iso_code,
            faults=faults,
            health_index=features.get("health_index", 1.0)
        )

        # 5️⃣ Alarm persistence
        _ = self.alarm_persistence.update(
            f"{asset}_{point}",
            raw_status
        )

        # 6️⃣ Fault FSM (progression)
        fsm_status = self.fsm.update(
            f"{asset}_{point}",
            alarm_code,
            faults
        )

        # 7️⃣ Alarm timer (delay)
        final_status = self.alarm_timer.update(
            f"{asset}_{point}",
            fsm_status
        )

        # 8️⃣ Maintenance Recommendation (STEP 6 🔥)
        recommendation = self.recommender.recommend(
            status=final_status,
            faults=faults,
            iso_zone=iso_label,
            vel_rms=vel_rms,
            health_index=features.get("health_index", 1.0)
        )

        # 9️⃣ Publish ke SCADA
        publish_scada_features(
            asset=asset,
            point=point,
            rpm=rpm or 0,
            health=features.get("health_index", 1.0),
            vel_rms=vel_rms,
            iso_zone=iso_label,
            iso_zone_code=iso_code,
            faults=faults,
            status=final_status,
            alarm_code=alarm_code,
            recommendation=recommendation   # 👈 OPTIONAL (kalau SCADA siap)
        )

        # 🔟 Return lengkap (API / Historian / ML)
        return {
            **features,
            "iso_zone": iso_label,
            "iso_zone_code": iso_code,
            "faults": faults,
            "status": final_status,
            "alarm_code": alarm_code,
            "maintenance_recommendation": recommendation
        }

