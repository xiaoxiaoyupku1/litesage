# Status Bar
statBar = None
def setStatus(msg, timeout=5000, bar=None):
    global statBar
    if statBar is None and bar is not None:
        statBar = bar
    statBar.clearMessage()
    statBar.showMessage(msg, timeout=timeout)


# Tool Bar