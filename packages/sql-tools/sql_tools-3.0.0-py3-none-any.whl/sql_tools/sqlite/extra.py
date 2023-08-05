    # &FOR INLINE DATA
    inlineData = False
    __temp = []
    if inlineData:
        if __execMethod:
            __tools.setStatus("Inlining data", logConsole=logConsole)
        for values in data:
            for value in values:
                __temp.append(value)
        data = __temp.copy()
    del __temp

    # &FOR SPLITBYCOLUMNS
    __temp = []
    if splitByColumns:
        if __execMethod:
            __tools.setStatus("Spliting by columns", logConsole=logConsole)
        __temp = []
        for database in data:
            __temp.append(list(zip(*database)))
        data = __temp.copy()
    del __temp
