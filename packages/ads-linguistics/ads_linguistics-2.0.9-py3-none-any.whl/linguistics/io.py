import pandas as pd


class io:

    @staticmethod
    def read_file(filename, file="csv"):
        if file == "csv":
            return pd.read_csv(filename)

    @staticmethod
    def save_file(data, filename, file="csv", index=False):
        if file == "csv":
            data.to_csv(filename, index=index)

    @staticmethod
    def check_args(sys, no_of_args=2, message="I need a) filename"):
        if len(sys.argv) < no_of_args:
            print(message)
            sys.exit()

        filename = sys.argv[1]
        modelname = filename.split('/')[-1]
        modelname = modelname[:-4]

        return filename, modelname
