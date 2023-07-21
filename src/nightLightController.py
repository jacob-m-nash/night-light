import os
import sys

PIPE_PATH = os.path.join(os.getcwd(),"pipes","pipe") # TODO when setting up write path of pipe to "global" config file 

def Run(args):
    if not os.path.isfile(PIPE_PATH):
        print("No pipe exists, night light not running")
        return
    with open(PIPE_PATH, 'w') as pipeInput:    
        pipeInput.write(" ".join(args))
    with open(PIPE_PATH, 'r') as pipeInput:
        print(pipeInput.readline())
    return

if __name__ == '__main__':
    args = sys.argv[1:]
    Run(args)
    