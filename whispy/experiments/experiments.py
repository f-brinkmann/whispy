from whispy.utils import read_config
import numpy as np
import os
import time
from typing import Optional, List, Dict

# Directory containing this file.
# Required for loading the default configs
FILEPATH = os.path.dirname(os.path.abspath(__file__))


def course(
        experiment: Optional[str] = None,
        randomize_blocks: Optional[bool] = True,
        randomize_sections: Optional[bool] = True,
        randomize_conditions: Optional[bool] = True,
        max_conditions_per_gui: Optional[int] = 7,
        random_seed: Optional[int] = None) -> List[Dict]:
    """Generate a randomized experimental course from configuration.

    Parameters
    ----------
    experiment : str or None, optional
        Path to the experiment configuration file. If ``None``, the default
            ``configs/experiment.yml`` from this package is used.
    randomize_blocks : bool, optional
        Whether to randomize the order of blocks of the experiment. The default
        is ``True``.
    randomize_sections : bool, optional
        Whether to randomize the order of sections within blocks of the
        experiment. The default is ``True``.
    randomize_conditions : bool, optional
        Whether to randomize the order of conditions within sections of the
        experiment. The default is ``True``.
    max_conditions_per_gui : int, optional
        Maximum number of conditions to display per GUI screen. The default is
        ``7``.
    random_seed : int, optional
        Seed for random number generator. If ``None``, the current internet
        time in seconds ``time.time()`` is used.

    Returns
    -------
    experimental_course: list of dict
        Experimental course as a list. Each element contains the keys
        blocks, sections, references, test conditions, and flags indicating
        block/section changes.
    """

    # load config
    if experiment is None:
        experiment = os.path.join(
                FILEPATH, '..', '..', 'configs', 'experiment.yml')

    experiment = read_config(experiment)

    # initialize experimental_course
    experimental_course = []

    # initialize random generator
    if random_seed is None:
        random_seed = int(time.time())

    rng = np.random.default_rng(random_seed)

    # randomize blocks
    n_blocks = len(experiment)

    if randomize_blocks and n_blocks > 1:
        blocks = rng.permutation(n_blocks)
    else:
        blocks = np.arange(n_blocks)

    # loop blocks
    for b_idx in blocks:

        block = experiment[b_idx]["block"]

        # randomize sections
        n_sections = len(block)

        if randomize_sections and n_sections > 1:
            sections = rng.permutation(n_sections)
        else:
            sections = np.arange(n_sections)

        # loop sections
        for s_idx in sections:
            section = block[s_idx]["section"]

            # randomize conditions
            n_conditions = len(section["test"])
            conditions = section["test"]

            if randomize_conditions and n_conditions > 1:
                conditions = rng.permutation(conditions)

            # split conditions across multiple rating GUIs
            n_gui = int(np.ceil(n_conditions / max_conditions_per_gui))

            for g_idx in range(n_gui):

                # check if block or section changed
                if experimental_course:
                    block_changed = \
                        experimental_course[-1]["block"] != b_idx
                    section_changed = \
                        experimental_course[-1]["section"] != s_idx
                    # ignore section change at the start of a new block
                    section_changed = section and not block_changed
                else:
                    # beginning of the experiment
                    block_changed, section_changed = (True, True)

                # get current conditions (if split across multiple GUIs)
                t_start = g_idx * max_conditions_per_gui
                t_end = min(n_conditions, t_start + max_conditions_per_gui)

                # append current line of the experiment
                experimental_course.append(
                    {"block": int(b_idx),
                     "section": int(s_idx),
                     "reference": section["reference"],
                     "test": conditions[t_start:t_end],
                     "block_changed": bool(block_changed),
                     "section_changed": bool(section_changed)}
                )

    return experimental_course
