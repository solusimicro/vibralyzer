def smooth_confidence(current, state, alpha=0.3):
    prev = state.get("confidence", current)
    smooth = alpha * current + (1 - alpha) * prev
    state["confidence"] = smooth
    return round(smooth, 2)


def update_stage(conf_smooth, features, state):
    rms = features.get("rms", 0)

    if state["stage"] == "NORMAL":
        if conf_smooth > 0.5:
            state["counter"] += 1
            if state["counter"] >= 3:
                state["stage"] = "EARLY"
                state["counter"] = 0
        else:
            state["counter"] = 0

    elif state["stage"] == "EARLY":
        if conf_smooth > 0.7 and rms > 0.03:
            state["counter"] += 1
            if state["counter"] >= 3:
                state["stage"] = "LATE"
                state["counter"] = 0
        else:
            state["counter"] = 0

    return state
