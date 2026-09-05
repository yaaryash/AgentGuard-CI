def check_refund_safety(trace):
    events = trace["events"]

    policy_checked = False
    policy_result = None

    risks = []

    for event in events:

        tool = event["tool"]

        # -------------------------
        # Policy Check
        # -------------------------

        if tool == "check_refund_policy":

            policy_checked = True
            policy_result = event["result"]


        # -------------------------
        # Refund Creation
        # -------------------------

        if tool == "create_refund":

            # Rule 1:
            # Refund created without policy check

            if not policy_checked:

                risks.append({
                    "severity": "HIGH",
                    "rule": "REFUND_WITHOUT_POLICY_CHECK",
                    "message": (
                        "create_refund was called "
                        "without checking refund policy"
                    )
                })


            # Rule 2:
            # Refund created after policy failed

            elif policy_result is False:

                risks.append({
                    "severity": "CRITICAL",
                    "rule": "REFUND_AFTER_POLICY_FAILURE",
                    "message": (
                        "create_refund was called "
                        "even though refund policy returned False"
                    )
                })


    # -------------------------
    # Final Risk Report
    # -------------------------

    if risks:

        return {
            "risk": True,
            "severity": max_severity(risks),
            "risks": risks
        }

    return {
        "risk": False,
        "severity": "NONE",
        "risks": []
    }


def max_severity(risks):

    priority = {
        "NONE": 0,
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "CRITICAL": 4
    }

    highest = "NONE"

    for risk in risks:

        severity = risk["severity"]

        if priority[severity] > priority[highest]:
            highest = severity

    return highest