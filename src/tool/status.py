# Status Bar
statBar = None
def setStatus(msg, bar=None):
    global statBar
    if statBar is None and bar is not None:
        statBar = bar
    statBar.clearMessage()
    statBar.showMessage(msg, timeout=-1)


# Tool Bar