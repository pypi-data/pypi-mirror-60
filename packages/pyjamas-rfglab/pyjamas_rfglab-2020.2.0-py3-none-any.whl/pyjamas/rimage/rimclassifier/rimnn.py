"""
    PyJAMAS is Just A More Awesome Siesta
    Copyright (C) 2018  Rodrigo Fernandez-Gonzalez (rodrigo.fernandez.gonzalez@utoronto.ca)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from pyjamas.rimage.rimclassifier.rimclassifier import rimclassifier
from sklearn.neural_network import MLPClassifier

class nnmlp(rimclassifier):

    N_HIDDEN: int = (30,)
    L2: float = 0.
    EPOCHS: int = 100
    ETA: float = 0.001  # learning rate, # only used by 'adam' or 'sgd' solvers.
    SHUFFLE: bool = True  # learning rate, # only used by 'adam' or 'sgd' solvers.
    MINIBATCH_SIZE: int = 50  # only used by 'adam' or 'sgd' solvers.

    def __init__(self, parameters: dict = None):
        super().__init__(parameters)

        n_hidden = parameters.get('n_hidden', nnmlp.N_HIDDEN)
        l2: float = parameters.get('l2', nnmlp.L2)
        epochs: int = parameters.get('epochs', nnmlp.EPOCHS)
        eta: float = parameters.get('eta', nnmlp.ETA)
        shuffle: bool = parameters.get('shuffle', nnmlp.SHUFFLE)
        minibatch_size: int = parameters.get('minibatch_size', nnmlp.MINIBATCH_SIZE)

        # Neural network/multilayer perceptron-specific parameters.
        # Note: The default solver ‘adam’ works pretty well on relatively large datasets
        # (with thousands of training samples or more) in terms of both training time and validation score.
        # For small datasets, however, ‘lbfgs’ can converge faster and perform better.
        self.classifier = parameters.get('classifier', MLPClassifier(solver='lbfgs', alpha=l2,
                                                                     batch_size=minibatch_size,
                                                                     hidden_layer_sizes=n_hidden,
                                                                     learning_rate_init=eta,
                                                                     max_iter=epochs,
                                                                     random_state=nnmlp.DEFAULT_SEED,
                                                                     shuffle=shuffle,
                                                                     verbose=True))
