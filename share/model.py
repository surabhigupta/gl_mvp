import pandas as pd
from data_recipe import IdentityRecipe, SyntheticDataRecipe
from sklearn.cross_validation import KFold
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.neighbors import KNeighborsClassifier as KNN
from sklearn.metrics import classification_report
import numpy as np
from sklearn.preprocessing import StandardScaler
import math
from data_provider import fetch_patient_data

# Select identity recipe to create models with only 134 eyes (without synthetic data using combination)
# recipe = IdentityRecipe()
recipe = SyntheticDataRecipe()


def make_predictions():
    df = fetch_patient_data()
    X_df = pd.DataFrame()
    y_labels = pd.DataFrame()
    patients = df.groupby('id')
    for name, patient in patients:
        combs = recipe.get_recipe(len(patient))

        for index, pt_indices in enumerate(combs):
            data = patient.iloc[pt_indices,:]

            mean_age = data['age'].mean()
            split_point = data['nvisit'][data['age'] > mean_age].iloc[0]
            set1 = data[data['nvisit'] < split_point]
            set2 = data[data['nvisit'] >= split_point]

            vf_points_set1 = set1.ix[:,4:]
            vf_points_set2 = set2.ix[:,4:]

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
        y_train = np.where(y_train_df['truth'] == 'progressing', 1, np.where(y_train_df['truth'] == 'stable', 0, -1))

        X_test_df = X_test_df.drop('id', axis=1)
        X_train_df = X_train_df.drop('id', axis=1)

        # print (list(X_train_df.columns.values))
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train_df.as_matrix().astype(np.float))
        X_test = scaler.fit_transform(X_test_df.as_matrix().astype(np.float))

        clf = clf_class(**kwargs)
        clf.fit(X_train,y_train)
        prediction = clf.predict(X_test)
        y_pred[test_actual_index] = prediction

    return y_pred


def predict(patients, X,y):
    def accuracy(y_true,y_pred):
        patient_map = dict()
        accuracy_by_VF_count = dict()

        combinations = y_true['combinations'].as_matrix()
        ids = y_true['id'].as_matrix()
        y_true = np.where(y_true['truth'] == 'progressing', 1, np.where(y_true['truth'] == 'stable', 0, -1))

        results_by_patient = np.vstack([ids, combinations,y_true,y_pred]).T
        for result in results_by_patient:
            (ptid, combs, true, pred) = result
            combs = combs.split()
            if not ptid in patient_map:
                patient_map[ptid] = {'preds':[], 'true_label':true, 'combs':dict()}
            patient_map[ptid]['preds'].append(int(true==pred))
            if len(combs) not in patient_map[ptid]['combs']:
                patient_map[ptid]['combs'][len(combs)] = []
            patient_map[ptid]['combs'][len(combs)].append((int(true==pred),true,pred))

        max_combs = [max(patient_map[ptid]['combs']) for ptid in patient_map]
        for index, ptid in enumerate(patient_map):
            for comb in patient_map[ptid]['combs']:
                vf_p = (float(comb) / float(max_combs[index])) * 100
                vf_p = float(math.ceil(vf_p / 10.0)) * 10
                if vf_p not in accuracy_by_VF_count:
                    accuracy_by_VF_count[vf_p] = []
                accuracy_by_VF_count[vf_p].append((patient_map[ptid]['combs'][comb][0][1], patient_map[ptid]['combs'][comb][0][2]))

        # Uncomment for more detailed results

        # print "Accuracy by VF count"
        # for vf_count in sorted(accuracy_by_VF_count):
        #     # np.mean([np.mean(i[0]==i[1]) for i in accuracy_by_VF_count[vf_count]]),
        #     print "VF Count: %d percent: (%d records)" % (vf_count, len(accuracy_by_VF_count[vf_count]))
        #     true = [i[0] for i in accuracy_by_VF_count[vf_count]]
        #     pred = [i[1] for i in accuracy_by_VF_count[vf_count]]
        #     print(classification_report(true, pred, target_names=["stable", "progressing"]))
        #
        # print "Accuracy per patient by number of combinations"
        # print "\n%20s %20s %20s" % ("Number of VFs", "# Data points", "Accuracy")
        # for ptid in patient_map:
        #     by_combs = [(ptid, t, len(patient_map[ptid]['combs'][t]), round(np.mean(patient_map[ptid]['combs'][t]),2)) for t in patient_map[ptid]['combs']]
        #     print "%10s" % by_combs[0][0],
        #     print [tuple(i[1:]) for i in by_combs]

        y_true = np.array(y_true, dtype=np.int64)
        y_pred = np.array(y_pred, dtype=np.int64)
        print(classification_report(y_true, y_pred, target_names=["stable", "progressing"]))
        return np.mean(y_true == y_pred)

    print X.shape, y.shape
    print "Support vector machines:"
    print "Overall Accuracy: %.2f" % accuracy(y, run_cv_with_patients(patients,X,y,SVC))
    print "Random forest:"
    print "Overall Accuracy: %.3f" % accuracy(y, run_cv_with_patients(patients,X,y,RF))
    print "K-nearest-neighbors:"
    print "%.3f" % accuracy(y, run_cv_with_patients(patients,X,y,KNN))


if __name__ == '__main__':
    make_predictions()