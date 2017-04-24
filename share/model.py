import pandas as pd
from data_recipe import IdentityRecipe, SyntheticDataRecipe
from sklearn.cross_validation import KFold
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.metrics import precision_recall_fscore_support
import numpy as np
from sklearn.preprocessing import StandardScaler
from data_provider import fetch_patient_data
from math import trunc


# Select identity recipe to create models with only 134 eyes (without synthetic data using combination)
recipe = IdentityRecipe()
# recipe = SyntheticDataRecipe()
NUM_ITERATIONS = 1000


def make_predictions():
    for datasets in fetch_patient_data():
        # Printing the features to be used for training
        df = datasets['data']
        features = filter(lambda x: x not in ['id', 'nvisit', 'truth'], list(df.columns.values))
        print datasets['name']

        X_df = pd.DataFrame()
        y_labels = pd.DataFrame()
        patients = df.groupby('id')

        for name, patient in patients:
            combs = recipe.get_recipe(len(patient))

            for index, pt_indices in enumerate(combs):
                data = patient.iloc[pt_indices,:]

                mean_age = data['age'].mean()
                split_point = data['nvisit'][data['age'] > mean_age].iloc[0]
                vf_points_set1 = data[data['nvisit'] < split_point]
                vf_points_set2 = data[data['nvisit'] >= split_point]

                diff_df = (vf_points_set2.mean(axis=0) - vf_points_set1.mean(axis=0)).to_frame()
                prog_feat_space = diff_df.T
                prog_feat_space['id'] = pd.Series(data['id'].iloc[0], index=prog_feat_space.index)

                labels = pd.Series(data['truth'].iloc[0], index=prog_feat_space.index).to_frame("truth")
                ptids = pd.Series(name, index=prog_feat_space.index).to_frame("id")
                combinations = pd.Series(' '.join(map(lambda x:str(x),pt_indices)), index=prog_feat_space.index).to_frame("combinations")
                y_labels = pd.concat([y_labels, pd.concat([labels, ptids, combinations], axis=1)])
                X_df = pd.concat([X_df, prog_feat_space])

        predict(patients, X_df, y_labels)


def run_cv_with_patients(patients, X_df, y_df, clf_class, **kwargs):
    kf = KFold(len(patients), n_folds=5, shuffle=True)
    y_pred = y_df['truth'].as_matrix().copy()

    patients_series = patients.apply(lambda t: t.iloc[0]['id'])

    for train_index, test_index in kf:
        train_ids = patients_series.iloc[train_index]
        test_ids = patients_series.iloc[test_index]

        X_test_df = X_df[X_df['id'].isin(test_ids)]
        X_train_df = X_df[X_df['id'].isin(train_ids)]
        test_actual_index = np.where(X_df['id'].isin(test_ids))

        y_train_df = y_df[y_df['id'].isin(train_ids)]
        y_train_df = y_train_df.drop('id', axis=1)

        for col_name in ['id', 'nvisit']:
            X_test_df = X_test_df.drop(col_name, axis=1)
            X_train_df = X_train_df.drop(col_name, axis=1)

        y_train = np.where(y_train_df['truth'] == 'progressing', 1, np.where(y_train_df['truth'] == 'stable', 0, -1))

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train_df.as_matrix().astype(np.float))
        X_test = scaler.fit_transform(X_test_df.as_matrix().astype(np.float))

        clf = clf_class(**kwargs)
        clf.fit(X_train,y_train)
        prediction = clf.predict(X_test)
        y_pred[test_actual_index] = prediction

    return np.array(y_pred, dtype=np.int64)


def predict(patients, X,y):

    y_true = np.array(np.where(y['truth'] == 'progressing', 1, np.where(y['truth'] == 'stable', 0, -1)), dtype=np.int64)

    def print_report(p_r_f_report, title, digits=2):
        print title
        headers = ["precision", "recall", "f1-score", "support"]
        fmt = '%% %ds' % 11  # first column: class name
        fmt += '  '
        fmt += ' '.join(['% 9s' for _ in headers])
        fmt += '\n'
        headers = [""] + headers
        report = fmt % tuple(headers)
        report += '\n'
        p, r, f1, s = p_r_f_report[0], p_r_f_report[1], p_r_f_report[2], p_r_f_report[3]
        for i, label in enumerate(["Stable", "Progressing"]):
            values = [label]
            for v in (p[i], r[i], f1[i]):
                values += ["{0:0.{1}f}".format(v, digits)]
            values += ["{0}".format(trunc(s[i]))]
            report += fmt % tuple(values)

        report += '\n'
        # compute weighted averages
        values = ['avg / total']
        for v in (np.average(p, weights=s),
                  np.average(r, weights=s),
                  np.average(f1, weights=s)):
            values += ["{0:0.{1}f}".format(v, digits)]
        values += ['{0}'.format(trunc(np.sum(s)))]
        report += fmt % tuple(values)
        print report

    # for algos in [{'name':'Support Vector Machine', 'algo':SVC}, {'name':'Random Forest', 'algo':RF}, {'name':'K Nearest Neighbors', 'algo':KNN}]:
    for algos in [{'name':'Support Vector Machine', 'algo':SVC}]:
        pred = [run_cv_with_patients(patients, X, y, algos['algo']) for i in range(NUM_ITERATIONS)]
        scores = np.array([np.array(precision_recall_fscore_support(y_true, i)) for i in pred])
        mean = np.mean(scores, axis=0)
        variance = np.std(scores, axis=0)
        variance[3] = mean[3]
        print_report(mean, "%s: Mean across %d iterations" % (algos['name'], NUM_ITERATIONS))
        print_report(variance, "%s: Standard Deviation across %d iterations" % (algos['name'], NUM_ITERATIONS), digits=4)


if __name__ == '__main__':
    make_predictions()