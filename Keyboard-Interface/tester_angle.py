
from RC_YawAngle import calculate_initial_coordinate_system





def tester(drone_point, target, true_result):
    angle = calculate_initial_coordinate_system(drone_point,target)
    if angle == true_result:
        print( 'true!')
    else:
        print(f" not good need to be {true_result} whas {angle}")

     


p1 = (412, 111)
p2 = (227,237)
p3 = (477, 250)

print("test 1:")
tester(p1,p2,-55.74196317782834)
print("test 2")
tester(p1, p3, 25.06200825579444)
print("test 3")
tester(p2,p3, 87.02330053188825)



