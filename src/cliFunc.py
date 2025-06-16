# Functions for interacting with the user

def getIntegerInput(prompt, minVal=0, maxVal=0):
    strVal = input(f"{prompt}: ")
    hasBounds = (minVal != maxVal)
    try:
        val = int(strVal)
        if (not hasBounds) or ((val >= minVal) and (val <= maxVal)):
            return val
        else:
            val = int("test")
    except ValueError:
        if hasBounds:
            print(f"'{strVal}' is not a valid integer between {minVal} and {maxVal}")
        else:
            print(f"'{strVal}' is not a valid integer")
        return getIntegerInput(prompt, minVal, maxVal)


def selectListElem(prompt, vals):
    if(len(vals) == 0):
        raise Exception("Cannot select elements from an empty list")
    if(len(vals) == 1):
        return vals[0]

    for valIndex, val in enumerate(vals):
        print(f"{valIndex + 1}. {val}")
    
    index = getIntegerInput(prompt, 1, len(vals))
    return vals[index-1]


def confirmSelection(func, default=True):
    val = func()

    if default:
        certain = input(f"Do you want to select {val}? [Y/n]\n")
    else:
        certain = input(f"Do you want to select {val}? [y/N]\n")

    if certain.lower() == "n" or (certain == "" and not default):
        return confirmSelection(func, default)
    else:
        return val

if __name__ == "__main__":
    a = lambda : getIntegerInput("Select an integer")
    b = confirmSelection(a)
    print(b)