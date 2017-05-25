import mdl
import os
import sys
from display import *
from matrix import *
from draw import *

"""======== first_pass( commands, symbols ) ==========
  Checks the commands array for any animation commands
  (frames, basename, vary)
  
  Should set num_frames and basename if the frames 
  or basename commands are present
  If vary is found, but frames is not, the entire
  program should exit.
  If frames is found, but basename is not, set name
  to some default value, and print out a message
  with the name being used.
  jdyrlandweaver
  ==================== """

def first_pass( commands ):
    basename = ""
    frames = -1
    for command in commands:
        if command[0] == 'frames':
            frames = command[1]
        if command[0] == 'basename':
            basename = command[1]
        if command[0] == 'vary':
            if frames == -1:
                print("vary used without setting frames")
                sys.exit(1)
    if basename == "":
        basename = "default"
        print("basename set to default")
    if frames == -1:
        frames = 1
        print("frames set to default")
    return (basename,frames)
    


"""======== second_pass( commands ) ==========
  In order to set the knobs for animation, we need to keep
  a seaprate value for each knob for each frame. We can do
  this by using an array of dictionaries. Each array index
  will correspond to a frame (eg. knobs[0] would be the first
  frame, knobs[2] would be the 3rd frame and so on).
  Each index should contain a dictionary of knob values, each
  key will be a knob name, and each value will be the knob's
  value for that frame.
  Go through the command array, and when you find vary, go 
  from knobs[0] to knobs[frames-1] and add (or modify) the
  dictionary corresponding to the given knob with the
  appropirate value. 
  ===================="""
def second_pass( commands, num_frames ):
    a = []
    for i in range(num_frames):
        a.append({}) 
    for command in commands:
        if command[0] == 'vary':
            if command[2] >= command[3] or command[3] >= num_frames:
                print("vary variable " + command[1] + " has invalid frame range")
                sys.exit(1)
            name = command[1]
            value = command[5] - command[4]
            f_range = command[3] - command[2]
            c = 0.0
            for i in range(command[2],command[3] + 1):
                if name in a[i]:
                    print("Overlapping and conflicting frames for vary variable " + name)
                    sys.exit(1)
                a[i][name] = (c / f_range) * (value) + command[4]
                c += 1.0
    return a


def run(filename):
    """
    This function runs an mdl script
    """
    color = [255, 255, 255]
    screen = new_screen()
    step = 0.1
    tmp = new_matrix()
    ident( tmp )
    
    p = mdl.parseFile(filename)
    if p:
        (commands, symbols) = p
    else:
        print "Parsing failed."
        return

    (basename,frames) = first_pass(commands)
    knobs = second_pass(commands,frames)
    for c_frame in range(frames):
        tmp = new_matrix()
        ident(tmp)
        stack = [ [x[:] for x in tmp] ]
        tmp = []
        for command in commands:
            c = command[0]
            args = command[1:]

            if c == 'box':
                add_box(tmp,
                        args[0], args[1], args[2],
                        args[3], args[4], args[5])
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'sphere':
                add_sphere(tmp,
                           args[0], args[1], args[2], args[3], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'torus':
                add_torus(tmp,
                          args[0], args[1], args[2], args[3], args[4], step)
                matrix_mult( stack[-1], tmp )
                draw_polygons(tmp, screen, color)
                tmp = []
            elif c == 'move':
                x = args[0]
                y = args[1]
                z = args[2]
                try:
                    i = knobs[c_frame-1][args[3]]
                    tmp = make_translate(x*i,y*i,z*i)
                except:
                    tmp = make_translate(x, y, z)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [q[:] for q in tmp]
                tmp = []
            elif c == 'scale':
                x = args[0]
                y = args[1]
                z = args[2]
                try:
                    i = knobs[c_frame-1][args[3]]
                    tmp = make_scale(x*i,y*i,z*i)
                    print(str(i))
                except:
                    tmp = make_scale(x, y, z)
                matrix_mult(stack[-1], tmp)
                stack[-1] = [q[:] for q in tmp]
                tmp = []
            elif c == 'rotate':
                theta = args[1] * (math.pi/180)
                try:
                    theta *= knobs[c_frame-1][args[2]]
                except:
                    "lol"
                if args[0] == 'x':
                    tmp = make_rotX(theta)
                elif args[0] == 'y':
                    tmp = make_rotY(theta)
                else:
                    tmp = make_rotZ(theta)
                matrix_mult( stack[-1], tmp )
                stack[-1] = [ x[:] for x in tmp]
                tmp = []
            elif c == 'push':
                stack.append([x[:] for x in stack[-1]] )
            elif c == 'pop':
                stack.pop()
            elif c == 'display':
                display(screen)
            elif c == 'save':
                save_extension(screen, args[0])
        name = "anim/" + basename + "%03d"%c_frame
        save_ppm(screen,name)
        clear_screen(screen)
    make_animation(basename)
