import operator
import streamlit as st

OPS = {
    "==": operator.eq,
    ">=": operator.ge,
    "<=": operator.le,
    "<": operator.lt
}

RULES = [
    {
        "name": "Windows open → turn AC off",
        "priority": 100,
        "conditions": [["windows_open", "==", True]],
        "action": {
            "ac_mode": "OFF",
            "fan_speed": "LOW",
            "setpoint": None,
            "reason": "Windows are open"
        }
    },
    {
        "name": "No one home → eco mode",
        "priority": 90,
        "conditions": [
            ["occupancy", "==", "EMPTY"],
            ["temperature", ">=", 24]
        ],
        "action": {
            "ac_mode": "ECO",
            "fan_speed": "LOW",
            "setpoint": 27,
            "reason": "Home empty; save energy"
        }
    },
    {
        "name": "Hot & humid (occupied) → cool strong",
        "priority": 80,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 30],
            ["humidity", ">=", 70]
        ],
        "action": {
            "ac_mode": "COOL",
            "fan_speed": "HIGH",
            "setpoint": 23,
            "reason": "Hot and humid"
        }
    },
    {
        "name": "Hot (occupied) → cool",
        "priority": 70,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 28]
        ],
        "action": {
            "ac_mode": "COOL",
            "fan_speed": "MEDIUM",
            "setpoint": 24,
            "reason": "Temperature high"
        }
    },
    {
        "name": "Slightly warm (occupied) → gentle cool",
        "priority": 60,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["temperature", ">=", 26],
            ["temperature", "<", 28]
        ],
        "action": {
            "ac_mode": "COOL",
            "fan_speed": "LOW",
            "setpoint": 25,
            "reason": "Slightly warm"
        }
    },
    {
        "name": "Night (occupied) → sleep mode",
        "priority": 75,
        "conditions": [
            ["occupancy", "==", "OCCUPIED"],
            ["time_of_day", "==", "NIGHT"],
            ["temperature", ">=", 26]
        ],
        "action": {
            "ac_mode": "SLEEP",
            "fan_speed": "LOW",
            "setpoint": 26,
            "reason": "Night comfort"
        }
    },
    {
        "name": "Too cold → turn off",
        "priority": 85,
        "conditions": [["temperature", "<=", 22]],
        "action": {
            "ac_mode": "OFF",
            "fan_speed": "LOW",
            "setpoint": None,
            "reason": "Already cold"
        }
    }
]

def rule_matches(facts, rule):
    return all(
        OPS[c[1]](facts[c[0]], c[2])
        for c in rule["conditions"]
    )

def run_rules(facts, rules):
    matched = [r for r in rules if rule_matches(facts, r)]
    if not matched:
        return None, []
    matched.sort(key=lambda r: r["priority"], reverse=True)
    return matched[0]["action"], matched

st.title("Rule-Based Smart Home AC Controller")

temperature = st.number_input("Temperature (°C)", value=22)
humidity = st.number_input("Humidity (%)", value=46)
occupancy = st.selectbox("Occupancy", ["OCCUPIED", "EMPTY"])
time_of_day = st.selectbox("Time of Day", ["MORNING", "AFTERNOON", "EVENING", "NIGHT"])
windows_open = st.checkbox("Windows Open", value=False)

facts = {
    "temperature": temperature,
    "humidity": humidity,
    "occupancy": occupancy,
    "time_of_day": time_of_day,
    "windows_open": windows_open
}

if st.button("Evaluate"):
    action, matched_rules = run_rules(facts, RULES)

    st.subheader("Decision")
    st.write("AC Mode:", action["ac_mode"])
    st.write("Fan Speed:", action["fan_speed"])
    st.write("Setpoint:", action["setpoint"])
    st.write("Reason:", action["reason"])
