import re
import logging

import numpy as np
import pandas as pd

from dtcontrol.dataset.dataset_loader import DatasetLoader
from tqdm import tqdm


class UppaalDatasetLoader(DatasetLoader):
    def _load_dataset(self, filename):
        """
            Some assumptions regarding the Uppaal dataset
            1. All controllable states are named *.Choose
            2. Uppaal only works on integer domains (specifically np.int16)
            3. Actions are single-dimensional. However, if multiple components
               may have the .Choose state, they are added as categorical variables
               in X_train
            4. Step sizes for all state variables is 1
        """

        f = open(filename)
        print("Reading from %s" % filename)

        action_set = set()
        controllable_state_set = set()

        num_lines = sum(1 for line in f)

        f.seek(0)

        logging.info("Extracting actions and controllable components from UPPPAL dump")
        for i, line in enumerate(tqdm(f, total=num_lines)):
            if i == 1:
                # Extract numeric features
                numeric_features = re.findall(r'(\w+)=-?[0-9]+', line)

            # Extract actions and controllable components
            if line.startswith('State: '):
                ctrl = [word for word in line.split() if "Choose" in word]
                if ctrl:
                    controllable_state_set.update(ctrl)
            if line.startswith('When'):
                action_set.add(line[line.index(' take transition ') + 17:].rstrip())

        action_set = {action for action in action_set if "Choose" in action}
        actions = dict(zip(list(action_set), range(1, len(action_set) + 1)))
        controllable_states = list(controllable_state_set)

        # Figure out the assignments in each action and extract
        # the assigned value. The assigned variable is extracted
        # too, but not used anywhere as of now.
        index_to_value = dict()
        action_var = None
        for (action, index) in actions.items():
            _, action_var, val = re.findall(r"((\w+) := (-?[0-9]+))", action)[0]
            index_to_value[index] = int(val)

        row_num_vals = []
        row_actions = []

        ignore_current = False
        current_actions = []
        total_rows = 0
        total_state_actions = 0

        f.seek(0)

        for i in range(7):
            f.readline()

        logging.info("Extracting state-action pairs from UPPAAL dump")
        for i, line in enumerate(tqdm(f, total=num_lines)):
            if line.startswith("State:"):
                # find if the state is controllable, and if so, then make that position 1 in categorical vals
                controllable = False
                cat_vals = [0 for i in range(len(controllable_states))]
                for i in range(len(controllable_states)):
                    if controllable_states[i] in line:
                        cat_vals[i] = 1
                        controllable = True
                if not controllable:
                    ignore_current = True
                    continue
                else:
                    ignore_current = False
                    numeric_vals = [word.split("=")[1] for word in line.split() if "=" in word]
            elif ignore_current:
                continue
            elif line.startswith("When"):
                action_str = line[line.index(' take transition ') + 17:].rstrip()
                current_actions.append(actions[action_str])
            elif line.startswith("While"):
                # We implicityly assume that transitions starting with 'While' are mapped to wait.
                ignore_current = True
            elif line.strip() == "":
                if not ignore_current:
                    row_num_vals.append(cat_vals + numeric_vals)
                    row_actions.append(current_actions)
                    total_rows += 1
                    total_state_actions += len(current_actions)
                ignore_current = False
                current_actions = []
            else:
                raise Exception("ERROR: Unhandled line in input")

        logging.info(f"Done reading {total_rows} states with \na total of {total_state_actions} state-action pairs.")

        # Project onto measurable variables, the strategy should not depend on the gua variables coming from euler
        projection_variables = controllable_states + list(filter(lambda x: 'gua' not in x, numeric_features))
        num_df = pd.DataFrame(row_num_vals, columns=controllable_states + numeric_features, dtype=np.int16)
        num_df = num_df[projection_variables]

        grouped = num_df.groupby(projection_variables)
        X = np.empty((len(grouped), len(projection_variables)), dtype=np.int16)
        Y = np.full((len(grouped), max([len(y) for y in row_actions])), -1, dtype=np.int16)

        i = 0
        for (group, indices) in grouped.indices.items():
            if len(indices) > 1:
                X[i] = group
                conservative_actions = set(actions.values()).copy()
                for idx in indices:
                    conservative_actions &= set(row_actions[idx])
                assert len(
                    conservative_actions) > 0, "Stategy for picking safe action doesn't work. Deeper analysis needed."
                Y[i][0:len(conservative_actions)] = list(sorted(conservative_actions))
            else:
                X[i] = group
                Y[i][0:len(row_actions[indices[0]])] = sorted(row_actions[indices[0]])
            i = i + 1

        print("Constructed training set with %s datapoints" % X.shape[0])

        # construct metadata
        # assumption is that UPPAAL only works with integers
        X_metadata = dict()
        X_metadata["variables"] = projection_variables
        X_metadata["min"] = [int(i) for i in np.amin(X, axis=0)]
        X_metadata["max"] = [int(i) for i in np.amax(X, axis=0)]
        X_metadata["step_size"] = [1 for _ in range(len(projection_variables))]

        Y_metadata = dict()
        Y_metadata["variables"] = [action_var]
        Y_metadata["min"] = [min(index_to_value.values())]
        Y_metadata["max"] = [max(index_to_value.values())]
        Y_metadata["step_size"] = [int((Y_metadata["max"][0] - Y_metadata["min"][0])/(len(index_to_value) - 1))]

        logging.debug(X_metadata)
        logging.debug(Y_metadata)

        return (X, X_metadata, Y, Y_metadata, index_to_value)
