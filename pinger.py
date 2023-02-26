import asyncio

from viam.robot.client import RobotClient
from viam.rpc.dial import Credentials, DialOptions
from viam.components.board import Board
from viam.components.motor import Motor
from viam.components.base import Base
from viam.components.camera import Camera
from viam.services.vision import VisionServiceClient
from time import perf_counter

#from viam.components.servo import Servo




async def connect():
    creds = Credentials(
        type='robot-location-secret',
        payload='cw3q5avw80zw62kgvsmauzc4r8v3srfyosqnvcv0dg1e2zjg')
    opts = RobotClient.Options(
        refresh_interval=0,
        dial_options=DialOptions(credentials=creds)
    )
    return await RobotClient.at_address('wendys545-main.zi6pw6tlq8.viam.cloud', opts)

async def main():
    width=640
    height=480
    robot = await connect()

    print('Resources:')
    print(robot.resource_names)
    
    # Note that the pin supplied is a placeholder. Please change this to a valid pin you are using.
    # local

    

    local = Board.from_robot(robot, "local")
    pin17 = await local.gpio_pin_by_name("17")
    pin18 = await local.gpio_pin_by_name("21")
    pin19 = await local.gpio_pin_by_name("19")


 


    
    # print(f"local gpio_pin_by_name return value: {local_return_value}")
    
    #gpio=local.GPIOPin()

   # pin18 = local.GPIOPin("18")
    # pin18 = await local.gpio_pin(18)
    # pin19 = await local.gpio_pin(19)
    #pin19 = local.GPIOPin("19")
    # pin18 = gpio.pin(18)
    # pin19 = gpio.pin(19)

    ####srvo = Servo.from_robot(robot, "servo")

    nominal=.5

    # right
    right = Motor.from_robot(robot, "right")
    right_return_value = await right.is_moving()
    print(f"right is_moving return value: {right_return_value}")
    
    # left
    left = Motor.from_robot(robot, "left")
    left_return_value = await left.is_moving()
    print(f"left is_moving return value: {left_return_value}")
    

    vac=False


    # viam_base
    viam_base = Base.from_robot(robot, "viam_base")
    viam_base_return_value = await viam_base.is_moving()
    print(f"viam_base is_moving return value: {viam_base_return_value}")
    
    # camera1
    #camera_1 = Camera.from_robot(robot, "camera1")
    #camera_1_return_value = await camera_1.get_image()
    #print(f"camera1 get_image return value: {camera_1_return_value}")
    
    # classCam
    #class_cam = Camera.from_robot(robot, "classCam")
    # class_cam_return_value = await class_cam.get_image()
    # print(f"classCam get_image return value: {class_cam_return_value}")
    
    # pingpong
    #pingpong = VisionServiceClient.from_robot(robot, "pingpong")
    #pingpong_return_value = await pingpong.get_detections_from_camera("camera1","find_objects")
    #print(f"pingpong get_detector_names return value: {pingpong_return_value}")
    #detections=await
    pingpong = VisionServiceClient.from_robot(robot, "pingpong")
    on_left_side = False
    #pingpong_return_value = await pingpong.get_detections_from_camera("camera1","find_objects", timeout = 45)
    vactime = 0
    for _ in iter(int,1):
    
        if perf_counter()-vactime > 10:
            vac = False
        if vac:
            await pin18.set(True)
            if perf_counter()-vactime>2:
                right_motor_speed = .4
                left_motor_speed = .4
            print("vacuum is on")
        else:
            await pin18.set(False)
            print("vacuum is off")

        print("checking for balllllsssss")
        pingpong_return_value = await pingpong.get_detections_from_camera("camera1","find_objects", timeout = 4500)
        asyncio.sleep(.3)

        print("balls!?!?!?")
        #print(f"pingpong get_detector_names return value: {pingpong_return_value}")
        if await pin19.get() is False:
            print("appraoching ball")
            refrigerators = []
            for detect_obj in pingpong_return_value:
                if detect_obj.class_name == "Sportsball" and detect_obj.confidence > .4:
                    refrigerators.append(detect_obj)
            
            refrigerators.sort(key = lambda x: x.confidence, reverse=True)
            print(refrigerators)


            if refrigerators:
                print('refrigerator located')
                xmin = refrigerators[0].x_min
                xmax = refrigerators[0].x_max
                ymin = refrigerators[0].y_min
                ymax = refrigerators[0].y_max
            
                xcenter=(xmin + xmax)/2
                ycenter=(ymin + ymax)/2
                xwidth=xmax-xmin
                yheight=ymax-ymin

                print("ball is",xwidth, "by", yheight)

                if xwidth >200 and yheight >200:
                    atball = True
                    print('at the ball!')
                else:
                    print('not at the ball yet')
                    atball = False
                
                x_offset = xcenter - width/2
                y_offset = ycenter - height/2
                print(ycenter)

                if abs(x_offset) < 50:
                    right_motor_speed = nominal*1.5 - 0.0001 * (x_offset)
                    left_motor_speed = nominal*1.5 + 0.0001 * (x_offset)
                else:
                    right_motor_speed = nominal - 0.0001 * (x_offset)
                    left_motor_speed = nominal + 0.0001 * (x_offset)


                if atball is True:
                    print("stopping")
                    right_motor_speed = 0
                    left_motor_speed = 0
                    await pin18.set(True)


                print("setting right motor to", right_motor_speed)
                await right.set_power(right_motor_speed)
                print("setting left motor to", left_motor_speed)
                await left.set_power(left_motor_speed)    

                if x_offset < 0:
                    on_left_side = True
                    on_right_side = False
                else:
                    on_left_side = False
                    on_right_side = True
                if ycenter > 200:
                    vac=True
                    vactime = perf_counter()
            else:
                if on_left_side:
                    await right.set_power(.4);
                    await left.set_power(-0.2);
                    
                else: 
                    await right.set_power(-0.2);
                    await left.set_power(0.4);
                if vac:
                    print("caught")


                # await right.set_power(.4);
                # await left.set_power(0);

            await asyncio.sleep(0.1)
        




        # if await pin19.get() is True:
        #     print("approaching person")
        #     pin18.set(True)
        #     people = [] 
        #     for detect_obj in pingpong_return_value:
        #         if detect_obj.class_name == "Person" and detect_obj.confidence > .4:
        #             people.append(detect_obj)
            
        #     people.sort(key = lambda x: x.confidence, reverse=True)
        #     if bool(people):
        #         xmin = people[0].x_min
        #         xmax = people[0].x_max
        #         ymin = people[0].y_min
        #         ymax = people[0].y_max
            
        #         xcenter=(xmin + xmax)/2
        #         ycenter=(ymin + ymax)/2
        #         xwidth=xmax-xmin
        #         yheight=ymax-ymin

        #         if yheight >200:
        #             atperson = True
        #         else:
        #             atperson = False

        #         x_offset = (xcenter - width)/2
        #         y_offset = (ycenter - height)/2
        #         right_motor_speed = 0.5 * (y_offset - x_offset)
        #         left_motor_speed = 0.5 * (y_offset + x_offset)

        #         if atperson is True and pin19.get() is True:
        #             await right.go_for(1.83,10)
        #             await left.go_for(-1.83,10)
        #             await asyncio.sleep(5)
        #             #await srvo.move(90)
        #             await asyncio.sleep(1)
        #             await pin18.set(False)
                    
                    
        #         await right.set_power(right_motor_speed)
        #         await left.set_power(left_motor_speed)        
        #     await asyncio.sleep(0.1)


    print(xmin)
    
    
    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())

