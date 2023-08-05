"""Implements Sequence wrapper for use Numpy Arrays as Keras Sequences."""
from tensorflow.keras.utils import Sequence
import numpy as np
from .sequence_length import sequence_length
from .batch_slice import batch_slice


class NumpySequence(Sequence):
    """NumpySequence is a Sequence wrapper to uniform Numpy Arrays as Keras Sequences.

    Usage Examples
    ----------------------------
    The main usage of this class is as a package private wrapper for Sequences.
    It is required to uniformely return a batch of the array,
    without introducing special cases.
    However, a basic usage example could be the following:

    Wrapping a numpy array as a Sequence
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    .. code:: python

        from keras_mixed_sequence import NumpySequence
        import numpy as np

        examples_number = 1000
        features_number = 10
        batch_size = 32

        my_array = np.random.randint(
            2, shape=(
                examples_number,
                features_number
            )
        )

        my_sequence = NumpySequence(my_array, batch_size)

        # Keras will require the i-th batch as follows:
        ith_batch = my_sequence[i]

    """

    def __init__(self, array: np.ndarray, batch_size: int):
        """Return new NumpySequence object.

        Parameters
        --------------
        array: np.ndarray,
            Numpy array to be split into batches.
        batch_size: int,
            Batch size for the current Sequence.

        Returns
        --------------
        Return new NumpySequence object.
        """
        self._array, self._batch_size = array, batch_size

    def on_epoch_end(self):
        """Shuffle private numpy array object on every epoch end."""
        np.random.shuffle(self._array)

    def __len__(self) -> int:
        """Return length of Sequence."""
        return sequence_length(
            self._array,
            self._batch_size
        )

    def __getitem__(self, idx: int) -> np.ndarray:
        """Return batch corresponding to given index.

        Parameters
        ---------------
        idx: int,
            Index corresponding to batch to be rendered.

        Returns
        ---------------
        Return numpy array corresponding to given batch index.
        """
        return self._array[batch_slice(idx, self._batch_size)]
