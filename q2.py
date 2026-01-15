import json
from typing import List, Dict, Any, Tuple
import operator
import streamlit as st

# ----------------------------
# 1) Minimal rule engine
# ----------------------------
OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}

# AC Control Rules (from Table 1)
DEFAULT_RULES: List[Dict[str, Any]] = [
    {
        "name": "Windows open → turn AC off",
        "priority": 100,
        "conditions": [["windows_open", "==", True]],
        "action": {"mode": "OFF", "fan": "LOW", "setpoint": "-", "reason": "Windows are open"},
    },
    {
        "name": "No one home → eco mode",
        "priority": 90,
        "conditions": [["occupancy", "==", "EMPTY"], ["temperature", ">=", 24]],
        "action": {"mode": "ECO", "fan": "LOW", "setpoint": "27°C", "reason": "Home empty; save energy"},
    },
    {
        "name": "Too cold → turn off",
        "priority": 85,
        "conditions": [["temperature", "<=", 22]],
        "action": {"mode": "OFF", "fan": "LOW", "setpoint": "-", "reason": "Already cold"},
    },
    {
        "name": "Hot & humid → cool strong",
        "priority": 80,
        "conditions": [["occupancy", "==", "OCCUPIED"], ["temperature", ">=", 30], ["humidity", ">=", 70]],
        "action": {"mode": "COOL", "fan": "HIGH", "setpoint": "23°C", "reason": "Hot and humid"},
    },
    {
        "name": "Night → sleep mode",
        "priority": 75,
        "conditions": [["occupancy", "==", "OCCUPIED"], ["time_of_day", "==", "NIGHT"], ["temperature", ">=", 26]],
        "action": {"mode": "SLEEP", "fan": "LOW", "setpoint": "26°C", "reason": "Night comfort"},
    },
    {
        "name": "Hot → cool",
        "priority": 70,
        "conditions": [["occupancy", "==", "OCCUPIED"], ["temperature", ">=", 28]],
        "action": {"mode": "COOL", "fan": "MEDIUM", "setpoint": "24°C", "reason": "Temperature high"},
    },
    {
        "name": "Slightly warm → gentle cool",
        "priority": 60,
        "conditions": [["occupancy", "==", "OCCUPIED"], ["temperature", ">=", 26], ["temperature", "<", 28]],
        "action": {"mode": "COOL", "fan": "LOW", "setpoint": "25°C", "reason": "Slightly warm"},
    },
]

def evaluate_condition(facts: Dict[str, Any], cond: List[Any]) -> bool:
    if len(cond) != 3:
        return False
    field, op, value = cond
    if field not in facts or op not in OPS:
        return False
    try:
        return OPS[op](facts[field], value)
    except Exception:
        return False

def rule_matches(facts: Dict[str, Any], rule: Dict[str, Any]) -> bool:
    return all(evaluate_condition(facts, c) for c in rule.get("conditions", []))

def run_rules(facts: Dict[str, Any], rules: List[Dict[str, Any]]):
    fired = [r for r in rules if rule_matches(facts, r)]
    if not fired:
        return None, []
    fired_sorted = sorted(fired, key=lambda r: r.get("priority", 0), reverse=True)
    best = fired_sorted[0]
    return best, fired_sorted

# ----------------------------
# 2) Streamlit UI
# ----------------------------
st.set_page_config(page_title="AC Rule-Based Controller", layout="wide")
st.title("Smart Home Rule-Based AC Controller")

with st.sidebar:
    st.header("Input Home Conditions")
    temperature = st.number_input("Temperature (°C)", min_value=0, max_value=50, value=22)
    humidity = st.number_input("Humidity (%)", min_value=0, max_value=100, value=46)
    occupancy = st.selectbox("Occupancy", ["OCCUPIED", "EMPTY"])
    time_of_day = st.selectbox("Time of Day", ["MORNING", "AFTERNOON", "EVENING", "NIGHT"])
    windows_open = st.selectbox("Windows Open?", [True, False])

    st.divider()
    st.header("Rules (JSON)")
    default_json = json.dumps(DEFAULT_RULES, indent=2)
    rules_text = st.text_area("Edit rules here if needed", value=default_json, height=300)
    run = st.button("Evaluate", type="primary")

facts = {
    "temperature": float(temperature),
    "humidity": float(humidity),
    "occupancy": occupancy,
    "time_of_day": time_of_day,
    "windows_open": windows_open,
}

st.subheader("Facts")
st.json(facts)

# parse rules
try:
    rules = json.loads(rules_text)
except:
    st.error("Invalid JSON. Using default rules.")
    rules = DEFAULT_RULES

st.subheader("Active Rules")
with st.expander("Show rules", expanded=False):
    st.code(json.dumps(rules, indent=2), language="json")

st.divider()

if run:
    best, fired = run_rules(facts, rules)
    if not best:
        st.warning("No rules matched.")
    else:
        action = best["action"]
        st.subheader("AC Decision (Highest Priority Rule)")
        st.success(f"Mode: {action['mode']}, Fan: {action['fan']}, Setpoint: {action['setpoint']}")
        st.write("Reason:", action['reason'])

        st.subheader("Matched Rules (sorted by priority)")
        for i, r in enumerate(fired, start=1):
            st.write(f"**{i}. {r['name']}** | priority = {r['priority']}")
else:
    st.info("Enter inputs and click Evaluate.")
