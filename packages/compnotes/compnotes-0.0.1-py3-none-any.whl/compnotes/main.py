import os
currPath = os.path.dirname(os.path.abspath(__file__))

def menu(target = None, saveAs = None):
    """
    menu() to display all options
    2 parameters - target and saveAs
    target - use it if you already know the option
    saveAs - if u want to save the code somewhere, specify file name
    """
    stuff = dict(enumerate([
        "lSearch", 
        "bSearch", 
        "k2d&d2k",
        "sorting",
        "SLLL",
        "DLLL",
        "CLDLL",
        "queue",
        "stack",
        "BST",
        "HT"
        ], 1))
    if target == None:
        print("what do u want?")
        for k, v in stuff.items():
            print(f"{k}:{v}")
        target = ""
        while target not in stuff.keys():
            target = int(input("enter a valid key: "))
    with open(currPath + f"/h2comp/{stuff[target]}.py") as f:
        if saveAs == None:
            return f.read()
        else:
            with open(saveAs, "w") as f2:
                f2.write(f.read())
    
if __name__ == "__main__":
    print(menu())



