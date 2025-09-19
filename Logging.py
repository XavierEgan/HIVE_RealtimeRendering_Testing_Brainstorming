class Logging:
    @staticmethod
    def printInfo(s):
        print(f"\033[0m[INFO] {s}")

    @staticmethod
    def printWarn(s):
        print(f"\033[0;33m[WARNING] {s}\033[0m")

    @staticmethod
    def printErr(s):
        print(f"\033[0;1;31m[ERROR] {s}\033[0m")