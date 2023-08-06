import abc


class Operation(abc.ABC):
    """
    Operation base.
    """

    @abc.abstractmethod
    def apply(self, data_frame):
        """
        Apply this operation on the given `data_frame`.
        :param data_frame: a `pandas.DataFrame` to process.
        """
        pass


class RemoveDuplicateRows(Operation):
    """
    Remove all duplicates from the dataset based on a `unique_on` column.
    """

    def __init__(self, *unique_on):
        self._unique_on = [header.value for header in unique_on]

    def apply(self, data_frame):
        data_frame.drop_duplicates(
            subset=self._unique_on,
            keep='first',
            inplace=True,  # Modify the input data_frame directly.
        )
        return data_frame


class RemoveEmptyRows(Operation):
    """
    Remove all empty rows from the databaset based on a `empty_on` column.
    """

    def __init__(self, *empty_on):
        self._empty_on = [header.value for header in empty_on]

    def apply(self, data_frame):
        data_frame.dropna(
            axis=0,  # Drop rows which contain missing values.
            how='any',
            subset=self._empty_on,
            inplace=True,  # Modify the input data_frame directly.
        )
        return data_frame
