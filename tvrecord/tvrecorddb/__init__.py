def searchZap(zap, search):
    try:
        poss = []
        found = False
        sch = search.lower()
        for sect in zap.sections():
            if search.lower()[:4] in sect.lower():
                poss.append(sect)
            elif search == sect:
                found = True
                break
        return (poss, found)
    except Exception as e:
        print(e)
        errorNotify(sys.exc_info()[2], e)


def chooseName(poss, chan):
    try:
        for n in poss:
            print(n)
        print(f"Type the correct DVB name for channel {chan}")
        choice = input("? ")
        return choice
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)


def chooseGetData(chan):
    try:
        print(f"0, 1 or 2 - get data for channel {chan}")
        sin = input("? ")
        iin = int(sin)
        if iin < 0 or iin > 2:
            iin = 0
        return iin
    except Exception as e:
        errorNotify(sys.exc_info()[2], e)
