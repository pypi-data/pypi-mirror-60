import FlowMePy as fm
import numpy as np
import os
import pandas as pd
import pkg_resources


class FmFcsCache:
    """Caches data and gates from FCS files.
    """

    def __init__(self, filepath: str):
        """FCS cache.
        This class is designed to cache fcs data.
        In contrast to FmFcsLoader, it does not hold
        C++ classes and is therefore perfectly suited for 
        parallel processing.

        Arguments:
            filepath {str} -- absolute filepath to the fcs files.
        """

        self.filepath = filepath
        self.events = None
        self.gates = None

    def load(self):
        """Cache the FCS file.
        """

        with FmFcsLoader(self.filepath) as fcs:
            self.events = fcs.events()
            self.gates = fcs.gate_labels()

        return self


class FmFcsLoader:
    """The FCS loader.
    The lazy loading allows for creating multiple instances
    without loosing resources. A more greedy - but convenient
    class would be FmFcsCache which directly loads samples and
    therefore allows parallel loading.
    """

    def __init__(self, filepath: str, trainpath: str = ""):
        """A convenience class that eases the use of FlowMePy
        The constructor is leight-weight - hence loading is only
        performed if any member is called (i.e. events()).

        Arguments:
            filepath {str} -- the absolute file path
        """

        self._filepath = filepath
        self._train_path = trainpath
        self._fcs = None         # the C++ fcs object
        self._events = None      # dataframe with all events
        self._gate = None        # bool matrix with gate information
        self._autogate = None    # bool matrix with auto gate information

        if not self._train_path:
    
            self._train_path = pkg_resources.resource_filename(
                'FlowMePy', 'cloud/')

    def auto_gate_labels(self):

        if self._autogate is None:

            fcs = self.load()

            if fcs.auto_gate(self._train_path):
                labels = np.array(fcs.auto_gate_labels(), copy=True)
                names = fcs.auto_gate_names()

                # convert to data frame
                self._autogate = pd.DataFrame(
                    labels,
                    columns=names)
            else:
                self._autogate = pd.DataFrame()

        return self._autogate

    def __enter__(self):

        self.load()

        # cache values
        self._events = self.events()
        self._gates = self.gate_labels()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        self.fcs = None


    def gate_labels(self):
        """Returns gate labels

        Returns:
            pandas.DataFrame -- Gate labels is a MxN data frame 
            with M ... # events and N ... # of gates.
        """

        if self._gate is None:

            fcs = self.load()

            labels = np.array(fcs.gate_labels(), copy=True)
            names = fcs.gate_names()

            # convert to data frame
            self._gate = pd.DataFrame(
                labels,
                columns=names)

        return self._gate


    def events(self):
        """Returns the tranformed events.
        This function reads events from an fcs file compensates 

        Returns:
            pandas.DataFrame -- events is a MxN data frame with 
            M ... # events and N ... # of dimensions (antibodies)
        """

        if self._events is None:

            # load an fcs & process events
            fcs = self.load()

            # make a deep copy of the events
            data = np.array(fcs.events(), copy=True)

            # convert to panda data frame
            self._events = pd.DataFrame(data,
                                        columns=fcs.antibodies())

        return self._events

    def load(self):
        """Loads the FCS file.

        NOTE: this function typically does not need to be called explicitly.

        Raises:
            FileNotFoundError: if the provided file path does not exist.

        Returns:
            FlowMePy.fcs_file -- an FCS instance
        """

        if self._fcs is None:
            # file exists?
            if not os.path.exists(self._filepath):
                raise FileNotFoundError()

            # touch the file
            self._fcs = fm.fcs_file(self._filepath)

        return self._fcs

    def label_exclusive(self, gatename: str, others: list):
        """Returns exclusive events of the current gates.

        This method creates disjunct event groups for all gates
        provided in the list.

        Arguments:
            gatename {str} -- the gatename for the group of interest
            others {list} -- events that should be removed from 'gatename'

        Returns:
            [type] -- boolean array with exclusively gated events w.r.t 'gatename'
        """
        labels = self.gate_labels().copy()
        cl = labels[gatename]

        for g in others:

            if g is not gatename:
                cl -= labels[g]

        return cl


def load_fcs_from_list(filepaths: list):
    """Parallel loading of multiple FCS files.
    Since FCS files use a lot of resources (RAM), you
    should not load more than 50 samples at once.

    Arguments:
        filepaths {list} -- absolute FCS file paths

    Returns:
        FmFcsCache {list} -- loaded FCS data
    """
    from multiprocessing import Pool, Queue

    fcs_files = [FmFcsCache(f) for f in filepaths]

    with Pool() as pool:
        fcs_files = pool.map(FmFcsCache.load, fcs_files)

    return fcs_files


if __name__ == "__main__":

    print("you are running version: " + fm.__version__)

    # for debugging
    fd = os.path.join(os.path.dirname(__file__),
                      '../../flowme/src/data/samples/FacsDiva.xml')
    fk = os.path.join(os.path.dirname(__file__),
                      '../../flowme/src/data/samples/Kaluza.analysis')

    fcs = FmFcsLoader(fk)
    ag = fcs.auto_gate_labels()

    print(ag)

    # fcs = FmFcsCache(fd)
    # fcs.load()

    # fcs = FmFcsLoader(fd)

    # events = fcs.events()
    # gates = fcs.gate_labels()

    # f = load_fcs_from_list([fd, fk])

    pass
