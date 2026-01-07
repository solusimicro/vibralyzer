class MaintenanceRecommender:

    def recommend(self, status, faults, iso_zone, vel_rms, health_index):

        # DEFAULT
        recommendation = {
            "priority": "LOW",
            "maintenance_type": "CBM",
            "recommended_in": "30 days",
            "action": "Continue monitoring",
            "notes": "Machine operating within acceptable limits"
        }

        # 🔴 ALARM
        if status == "ALARM":
            recommendation.update({
                "priority": "HIGH",
                "maintenance_type": "CM",
                "recommended_in": "NOW",
                "action": self._alarm_action(faults),
                "notes": "Immediate maintenance required to avoid failure"
            })

        # 🟠 WARNING
        elif status == "WARNING":
            recommendation.update({
                "priority": "MEDIUM",
                "maintenance_type": "PM",
                "recommended_in": "7 days",
                "action": self._warning_action(faults),
                "notes": "Early degradation detected"
            })

        # 🟢 NORMAL tapi health drop
        elif health_index < 0.85:
            recommendation.update({
                "priority": "LOW",
                "maintenance_type": "CBM",
                "recommended_in": "14 days",
                "action": "Schedule inspection",
                "notes": "Health index trending down"
            })

        return recommendation

    def _alarm_action(self, faults):
        if not faults:
            return "Inspect machine immediately"

        main_fault = faults[0]["fault"]

        fault_actions = {
            "UNBALANCE": "Check rotor balance and coupling",
            "MISALIGNMENT": "Inspect shaft alignment",
            "BEARING_FAULT": "Inspect bearing condition, prepare replacement",
            "LOOSENESS": "Inspect foundation and mechanical fastening"
        }

        return fault_actions.get(
            main_fault,
            "Perform detailed vibration analysis"
        )

    def _warning_action(self, faults):
        if not faults:
            return "Schedule vibration re-measurement"

        main_fault = faults[0]["fault"]

        fault_actions = {
            "UNBALANCE": "Plan rotor balancing",
            "MISALIGNMENT": "Check alignment during next shutdown",
            "BEARING_FAULT": "Monitor bearing trend closely",
            "LOOSENESS": "Check bolts and mounting"
        }

        return fault_actions.get(
            main_fault,
            "Increase monitoring frequency"
        )
