# Copyright (C) 2019 Alteryx, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Random forest classification algorithm."""

from sklearn.ensemble import ExtraTreesClassifier


class RandomForestClassifier(ExtraTreesClassifier):
    """Random forest classifier wrapper class."""

    def __init__(
        self,
        n_estimators=100,
        criterion="gini",
        max_depth=10,
        min_samples_split=2,
        min_weight_fraction_leaf=0.0,
        max_features="auto",
        min_impurity_decrease=0.0,
        min_impurity_split=None,
        bootstrap=True,
        oob_score=False,
        n_jobs=None,
        random_state=10,
        class_weight=None,
    ):
        """Construct a random forest classifier."""
        super().__init__(
            n_estimators=n_estimators,
            criterion=criterion,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_weight_fraction_leaf=min_weight_fraction_leaf,
            max_features=max_features,
            min_impurity_decrease=min_impurity_decrease,
            min_impurity_split=min_impurity_split,
            bootstrap=bootstrap,
            oob_score=oob_score,
            n_jobs=n_jobs,
            random_state=random_state,
            class_weight=class_weight,
        )
