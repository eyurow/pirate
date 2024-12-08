import numpy as np
from testclass import Test

glob = 10

def set_pa():
    global glob
    glob += 10



def run():
    global glob
    glob = 10

    t = Test(glob)
    t.t()
    
def none():
    x = 5 + glob
    print(str(glob)[1])

    #set_pa()

if __name__ == '__main__':
    #run()
    none()
