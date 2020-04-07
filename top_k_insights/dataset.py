import csv
class Dataset:
    def __init__(self, filename):
        """
        Datasets should be csvs formatted with dimension columns to the left
        and measure as the final column. The first row should be a header.
        """
        with open(filename, encoding='mac_roman', newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            first_row = next(reader)
            self.dimension_names = first_row[:-1]
            self.measure_name = first_row[-1]
            self.data = []
            for row in reader:
                self.data.append(tuple(row))
