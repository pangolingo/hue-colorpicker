#!/usr/bin/python

from phue import Bridge
import time
import random
import getch

b = Bridge('10.0.0.12')


# If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
b.connect()

# Get the bridge state (This returns the full dictionary that you can explore)
# print( b.get_api() )

print("\n\n")

# Prints if light 1 is on or not
# print( b.get_light(1, 'on') )

# artery light group
GROUP = 3

artery_lights = b.get_group(GROUP, 'lights')
artery_lights = list(map(lambda l: int(l), artery_lights))

print(artery_lights)

b.set_group(GROUP, 'on', True)

red = [0.648427, 0.330856] # red: 255, 0, 0
green = [0.330853, 0.586362] # green: 65, 210, 27

while True:
    key = getch.getch()
    print(key)
    if key == ' ':
        color = (random.random(), random.random())
        print('changing to')
        print(color)
        b.set_light(artery_lights[0], {
            'transitiontime': 0,
            'xy': color,
            'bri': 254
        })
    # print('click')
    # b.set_light(artery_lights[0], {
    #     'transitiontime': 4,
    #     'xy': red,
    #     'bri': 254
    # })
    # b.set_light(artery_lights[1], {
    #     'transitiontime': 4,
    #     'xy': green,
    #     'bri': 254
    # })
    # time.sleep(4)
    # print('click')
    # b.set_light(artery_lights[0], {
    #     'transitiontime': 4,
    #     'xy': green,
    #     'bri': 254
    # })
    # b.set_light(artery_lights[1], {
    #     'transitiontime': 4,
    #     'xy': red,
    #     'bri': 254
    # })
    # time.sleep(4)

# for light in artery_lights:
#     b.set_light(light, {
#         # 'transitiontime': 700,
#         # 'hue': 0,
#         # 'sat': 100,
#         'xy': [0.648427, 0.330856], # red: 255, 0, 0
#         'bri': 254
#     })
#     time.sleep(1)
#     b.set_light(light, {
#         # 'transitiontime': 700,
#         # 'hue': 112,
#         # 'sat': 100,
#         'xy': [0.330853, 0.586362], # green: 65, 210, 27
#         'bri': 254
#     })

# for light in artery_lights:
#     b.set_light(light, 'on', False)
#     time.sleep(1)
#     b.set_light(light, 'on', True)
#     time.sleep(1)