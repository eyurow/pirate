import numpy as np

# 30, 120, 110 good sea blue/green
# cloudy dark blue: 25, 109, 158
# tuquoise: 64, 204, 190

# blue slider: 190 for light, 90 for dark
# b:g ratio (min/max): .752, 1.29; g:b - 1.33, .776
# red slider: min of 20 for clear, up to 90 for near grey


three = np.array([[130,130,130,130,130,130,130,130,130,130],
                 [130,130,130,130,130,130,  0,  0,130,130],
                 [130,130,130,  0,  0,  0,  0,  0,130,130],
                 [130,  0,  0,  0,  0,  0,  0,  0,130,130],
                 [130,130,130,  0,  0,  0,  0,  0,130,130],
                 [130,130,130,130,130,  0,  0,  0,130,130],
                 [130,130,130,130,130,130,130,  0,  0,130],
                 [130,130,130,130,130,130,130,130,130,130],
                 [130,130,130,130,130,130,130,130,130,130],
                 [130,130,130,130,130,130,130,130,130,130]])

six = np.array(  [[130,130,130,130,130,130,130,130,130,130],
                 [130,130,130,130,  0,  0,130,130,130,130],
                 [130,130,130,  0,  0,  0,  0,130,130,130],
                 [130,130,  0,  0,  0,  0,  0,  0,130,130],
                 [130,  0,  0,  0,  0,  0,  0,  0,  0,130],
                 [130,130,130,130,130,130,130,130,130,130],
                 [130,130,130,130,130,130,130,130,130,130],
                 [130,130,130,130,130,130,130,130,130,130],
                 [130,130,130,130,130,130,130,130,130,130],
                 [130,130,130,130,130,130,130,130,130,130]])







def six_six(): # 6/6
    one = np.array([np.array([1,2,3,4,5,6,7,8]), np.array([4,4,4,4,4,4,4,4])])
    two = np.array([np.array([2,3,4,5,6,7]), np.array([3,3,3,3,3,3])])
    three = np.array([np.array([3,4,5,6]), np.array([2,2,2,2])])
    four = np.array([np.array([4,5]), np.array([1,1])])
    
    return np.concatenate([one,two,three,four], axis = 1), ( len(one), len(two), len(three), len(four) )

def five_six():
    one = np.array([[1,2,3,4,5,6,7,8],[4,4,4,4,5,5,5,5]])
    two = np.array([[3,4,5,5,6,7],[3,3,3,4,4,4]])
    three = np.array([[4,5,6,6],[2,2,2,3]])
    four = np.array([[5],[1]])
    
    return np.concatenate([one, two, three, four], axis = 1), None

def four_six():
    one = np.array([[1,2,3,4,5,6,7,8],[3,4,4,4,5,5,5,6]])
    two = np.array([[3,4,5,6,7,8],[3,3,3,4,4,4]])
    three = np.array([[2,3,4,5,5,6,7],[2,2,2,2,3,3,3]])
    four = np.array([[5,6,6],[1,1,2]])
    
    return np.concatenate([one, two, three, four], axis = 1), None

def three_six():
    one = np.array([[1,2,3,4,5,6,7,8],[3,3,4,4,5,5,6,6]])
    two = np.array([[3,4,5,5,6],[3,3,3,4,4]])
    three = np.array([[2,3,4,5,6,6,7,7],[2,2,2,2,2,3,3,4]])
    four = np.array([[4,5,6],[1,1,1]])
    
    return np.concatenate([one, two, three, four], axis = 1), None

def two_six():
    one = np.array([[1,2,3,4,5,6,7],[2,3,3,4,5,6,6]])
    two = np.array([[3,4,5,6,6,7],[2,2,3,3,4,5]])
    three = np.array([[4,5,6,6,6,7,7],[2,2,2,3,4,4,5]])
    four = np.array([[4,5,6,6,6],[1,1,1,2,3]])
    
    return np.concatenate([one, two, three, four], axis = 1), None

def one_six():
    one = np.array([[2,3,4,5,6,7],[2,3,4,5,6,7]])
    two = np.array([[3,4,5,6,7],[2,3,4,5,6]])
    three = np.array([[4,5,6,7],[2,3,4,5]])
    four = np.array([[5,6,7,5,6,6],[2,3,4,2,2,3]])
    
    return np.concatenate([one, two, three, four], axis = 1), None
        
    


angle_triangle_map = {6: six_six(),
                      5: five_six(),
                      4: four_six(),
                      3: three_six(),
                      2: two_six(),
                      1: one_six()
                     }
    
    

