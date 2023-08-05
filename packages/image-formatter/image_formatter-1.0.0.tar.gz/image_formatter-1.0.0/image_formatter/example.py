import argparse

############ARGPARSE########
parser = argparse.ArgumentParser(description='Transform Raw to JPEG')
parser.add_argument('--to_print', type=str, help='print to screen this word')
args = parser.parse_args()
#############################


print(args.to_print)
