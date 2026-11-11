def analyze_log(log_text):
    """Describe known error patterns found in log text without external requests."""
    issues = []

    if "Fatal error" in log_text:
        issues.append("Fatal error detected. Server likely crashed immediately.")

    if "Out of memory" in log_text:
        issues.append("Server ran out of memory. Consider reducing entity load or increasing RAM.")

    if "assert" in log_text.lower():
        issues.append("Assertion failed. This usually indicates a bug in the game server code.")

    if "Unhandled Exception" in log_text:
        issues.append("Unhandled exception occurred. Check mods or corrupt save data.")

    if not issues:
        issues.append("No critical issues detected. May be normal shutdown or log.")

    return "Possible issues:\n" + "\n".join(f"- {issue}" for issue in issues)
