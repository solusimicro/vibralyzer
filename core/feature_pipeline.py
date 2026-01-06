# core/feature_pipeline.py
import yaml
import numpy as np

from features.time_features import time_features
from features.frequency_features import frequency_features
from features.order_features import order_features
from models.health_index import health_index
from core.band_manager import get_frequency_band
from models.machine_status import machine_status


class FeaturePipeline:
    def __init__(self, config_path="config/signal.yaml"):
        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.static_band = self.config["band"]

    def process(self, signal, fs, asset=None, point=None, rpm=None):
        features = {}

        # === 1️⃣ Windowing (ONCE, centrally) ===
        signal = np.asarray(signal)
        window = np.hanning(len(signal))
        signal = signal * window

        # === 2️⃣ Frequency band selection ===
        band = get_frequency_band(
            fs=fs,
            rpm=rpm,
            static_band=self.static_band
        )

        # === 3️⃣ Time-domain features ===
        features.update(time_features(signal))

        # === 4️⃣ Frequency-domain features ===
        features.update(
            frequency_features(
                signal=signal,
                fs=fs,
                band=band
            )
        )

        # === 5️⃣ Order analysis (conditional) ===
        if rpm is not None:
            features.update(
                order_features(
                    signal=signal,
                    fs=fs,
                    rpm=rpm
                )
            )

        # === 6️⃣ Health index (LAST) ===
        features["health_index"] = health_index(features)
        features["status"] = machine_status(features)
        return features