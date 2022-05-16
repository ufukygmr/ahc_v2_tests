from adhoccomputing.Networking.PhysicalLayer.BladeRFUtils import *


def main():
    print("Testing bladerf")
    bu = BladeRFUtils(2)
    bu.configureSdr("x115")

if __name__ == "__main__":
    main()
