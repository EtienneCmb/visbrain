"""Group functions for file managment.

This file contains a bundle of functions that can be used to load several
specific files including *.eeg, *.edf...
"""

import numpy as np

"""
##############################################################################
A LIRE (et à supprimer ensuite !)

Dans visbrain, j'ai adopté une nomenclature assez précise pour la
documentation et le formatage du code. Tu connais certainement, mais au cas où:
- Chaque ligne ne dépasse pas 79 caractères pour des questions de lisibilité.
Pour m'aider, dans sublimetext j'ai mis une ligne verticale.
- Le code suit la nomenclature pep8 (pareil, dans sublime j'ai un paquet pour
gérer ça).
- Dans la mesure du possible, j'essaye d'avoir une consistence dans ma doc
(une première ligne descriptive, suivi d'un paragraphe plus détaillé. Ensuite
viennent les arguments obligatoires (Args), puis les optionels (Kargs), puis
ce que la fonction retourne (ici c'est important de donner les tailles de
matrices). Enfin, parfois je met un exemple d'utilisation. Pas obligatoire.)

Je sais, c'est un peu tyranique, mais j'ai longuement regardé les packages les
plus développés et c'est un format standard (utilisé par numpy et scikit par
exemple).
Je t'ai pré-formatté la fonction eeg2array pour t'aider un peu. Si tu n'as pas
le temps de faire le formatage, pas de soucis, je remettrai en forme. C'est
quasiment automatique avec sublime.

PS: tu crois qu'on a vraiment besoin de retourner le nombre de channel et de
sample? Parce que ça se récupère bien ensuite si je comprends bien?
##############################################################################
"""

__all__ = ['eeg2array']


def eeg2array(arg1, arg2, karg1=0., karg2='ok', karg3=None):
    """One line description of what the function do.

    More explanations if needed. My function do this, do this, do this, do this
    do this, do this, do this, do this, do this, do this, do this.

    Args:
        arg1: float
            First arg description.

        arg2: string
            Second arg description.

    Kargs:
        karg1: float, optional, (def: 0.)
            Optional argument 1 description.

        karg2: string, optional, (def: 'ok')
            Optional argument 2 description.

        karg3: np.ndarray, optional, (def: None)
            Optional argument 3 description.

    Return:
        sf: float
            The sampling frequency.

        data: np.ndarray
            The data organised as well (n_channels, n_points)

        n_points: int
            The number of time points.

        chan: list
            The list of channel's names.

        n_channels: int
            The number of channels.

    Example:
        >>> import os
        >>> # Define path where the file is located
        >>> pathfile = 'mypath/'
        >>> path = os.path.join(pathfile, 'myfile.eeg')
        >>> sf, data, npts, chan, nchan = eeg2array(path)
    """
    # Comment :
    x = np.array([0, 1, 2, 3])
    # Comment :
    x *= 10

    return x
