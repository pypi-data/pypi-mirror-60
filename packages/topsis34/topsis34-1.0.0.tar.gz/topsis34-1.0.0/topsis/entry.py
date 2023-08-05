from . import topsis
import sys

def main():
    t = topsis.Topsis(sys.argv[1],sys.argv[2],sys.argv[3])
    t.calculate_print_rank()

if __name__ == "__main__":
    main()
