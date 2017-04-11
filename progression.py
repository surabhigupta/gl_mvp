import psycopg2
import csv
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import itertools
from sklearn.cross_validation import KFold
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier as RF
from sklearn.neighbors import KNeighborsClassifier as KNN

MIN_COMB_SIZE = 3

def export_data_to_csv(data):
    ordered_h = ["id", "truth", "nvisit", "age", "vfi", "md", "psd", "tdp1", "tdp2", "tdp3", "tdp4", "tdp5", "tdp6", "tdp7", "tdp8", "tdp9", "tdp10", "tdp11", "tdp12", "tdp13", "tdp14", "tdp15", "tdp16", "tdp17", "tdp18", "tdp19", "tdp20", "tdp21", "tdp22", "tdp23", "tdp24", "tdp25", "tdp27", "tdp28", "tdp29", "tdp30", "tdp31", "tdp32", "tdp33", "tdp34", "tdp36", "tdp37", "tdp38", "tdp39", "tdp40", "tdp41", "tdp42", "tdp43", "tdp44", "tdp45", "tdp46", "tdp47", "tdp48", "tdp49", "tdp50", "tdp51", "tdp52", "tdp53", "tdp54", "pdp1", "pdp2", "pdp3", "pdp4", "pdp5", "pdp6", "pdp7", "pdp8", "pdp9", "pdp10", "pdp11", "pdp12", "pdp13", "pdp14", "pdp15", "pdp16", "pdp17", "pdp18", "pdp19", "pdp20", "pdp21", "pdp22", "pdp23", "pdp24", "pdp25", "pdp27", "pdp28", "pdp29", "pdp30", "pdp31", "pdp32", "pdp33", "pdp34", "pdp36", "pdp37", "pdp38", "pdp39", "pdp40", "pdp41", "pdp42", "pdp43", "pdp44", "pdp45", "pdp46", "pdp47", "pdp48", "pdp49", "pdp50", "pdp51", "pdp52", "pdp53", "pdp54"]

    with open('patients.csv', 'w') as fp:
        writer = csv.writer(fp, delimiter=',')
        writer.writerow(ordered_h)
        for vf in data:
            values = [vf[v] for v in ordered_h]
            writer.writerow(values)

def connect():
    conn_string = "host='104.196.246.100' dbname='glaucoma' user='postgres' password='postgres'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor, conn


def create_patient_diff():
    df = pd.read_csv('patients.csv')

    result = pd.DataFrame()
    y_labels = pd.DataFrame()
    patients = df.groupby('id')
    for name, patient in patients:
        combs = get_combinations(len(patient), patient.iloc[0]['truth'])
        # print "Combos: ", len(patient), len(combs),
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
            result = pd.concat([result, prog_feat_space])

    # result.to_csv("patients_diff_combs.csv", index=False)
    predict(patients,result,y_labels)


def run_cv_with_patients(patients, X_df, y_df, clf_class, **kwargs):
    kf = KFold(len(patients),n_folds=5,shuffle=True)
    y_pred = y_df['truth'].as_matrix().copy()

    patients_series = patients.apply(lambda t: t.iloc[0]['id'])

    for train_index, test_index in kf:
        # print train_index, test_index
        train_ids = patients_series.iloc[train_index]
        test_ids = patients_series.iloc[test_index]

        X_test_df = X_df[X_df['id'].isin(test_ids)]
        X_train_df = X_df[X_df['id'].isin(train_ids)]
        test_actual_index = np.where(X_df['id'].isin(test_ids))

        y_train_df = y_df[y_df['id'].isin(train_ids)]
        y_train = np.where(y_train_df['truth'] == 'progressing', 1, np.where(y_train_df['truth'] == 'stable', 0, -1))

        # print len(test_ids), len(train_ids), X_test_df.shape, X_train_df.shape, y_train.shape

        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train_df.as_matrix().astype(np.float))
        X_test = scaler.fit_transform(X_test_df.as_matrix().astype(np.float))

        clf = clf_class(**kwargs)
        clf.fit(X_train,y_train)
        prediction = clf.predict(X_test)
        y_pred[test_actual_index] = prediction
        # np.set_printoptions(threshold=np.nan)

    return y_pred


def predict(patients, X,y):
    def accuracy(y_true,y_pred):

        patient_map = dict()
        by_label_accuracy = dict()
        # TODO: Find the accuracy for each patient for each of the chronological combinations (eg: (1,2), (1,2,3), (1,2,3,4) etc.

        combinations = y_true['combinations'].as_matrix()
        ids = y_true['id'].as_matrix()
        y = np.where(y_true['truth'] == 'progressing', 1, np.where(y_true['truth'] == 'stable', 0, -1))

        results_by_patient = np.vstack([ids, combinations,y,y_pred]).T
        for result in results_by_patient:
            (ptid, combs, true, pred) = result
            combs = combs.split()
            if not ptid in patient_map:
                patient_map[ptid] = {'preds':[], 'true_label':true, 'combs':dict()}
            patient_map[ptid]['preds'].append(int(true==pred))
            if len(combs) not in patient_map[ptid]['combs']:
                patient_map[ptid]['combs'][len(combs)] = []
            if str(true) not in by_label_accuracy:
                by_label_accuracy[str(true)] = []
            patient_map[ptid]['combs'][len(combs)].append(int(true==pred))
            by_label_accuracy[str(true)].append(int(true==pred))

        print "Accuracy for progressing and stable rows"
        print "%.2f (%2d) %.2f (%2d)" % (np.mean(by_label_accuracy['1']), len(by_label_accuracy['1']), np.mean(by_label_accuracy['0']), len(by_label_accuracy['0']))
        print "*********"
        results = [(ptid, patient_map[ptid]['true_label'], len(patient_map[ptid]['preds']), np.mean(patient_map[ptid]['preds'])) for ptid in patient_map]
        print "%20s %20s %20s %20s" % ("ID", "True Label", "# Data points", "Accuracy")
        for r in results:
            print "%20s" * len(r) % tuple(r)

        print "\n%20s %20s %20s" % ("Number of elements", "# Data points", "Accuracy")
        for ptid in patient_map:
            by_combs = [(ptid, t, len(patient_map[ptid]['combs'][t]), round(np.mean(patient_map[ptid]['combs'][t]),2)) for t in patient_map[ptid]['combs']]
            print "%10s" % by_combs[0][0],
            print [tuple(i[1:]) for i in by_combs]
        return np.mean(y == y_pred)

    print type(X), type(y), X.shape, y.shape
    print "Support vector machines:"
    print "%.3f" % accuracy(y, run_cv_with_patients(patients,X,y,SVC))
    print "Random forest:"
    print "%.3f" % accuracy(y, run_cv_with_patients(patients,X,y,RF))
    # print "K-nearest-neighbors:"
    # print "%.3f" % accuracy(y, run_cv_with_patients(patients,X,y,KNN))


def run_cv(X,y,clf_class,**kwargs):
    # Construct a kfolds object
    kf = KFold(len(y),n_folds=5,shuffle=True)
    y_pred = y.copy()
    print "KFolds: ", kf
    # Iterate through folds
    for train_index, test_index in kf:
        X_train, X_test = X[train_index], X[test_index]
        y_train = y[train_index]
        # Initialize a classifier with key word arguments
        clf = clf_class(**kwargs)
        clf.fit(X_train,y_train)
        y_pred[test_index] = clf.predict(X_test)
    return y_pred


def get_split_combinations(n):
    # Each combination should have approx. half elements from the first half the half from the second half
    # This will ensure that we don't generate combinations of eyes from the stable section.
    data = range(n)
    # Note # elements in set1 will be >= # elements in set(2)
    set1 = data[:len(data)/2]
    set2 = data[len(data)/2:]
    combs = []
    min_comb_length = max(MIN_COMB_SIZE-1, n-7)

    for i_index in xrange(min_comb_length,len(set1)+1):
        for i in itertools.combinations(set1, i_index):
            indices = filter(lambda x: x>0, [i_index-1,i_index,i_index+1])
            for j_index in indices:
                for j in itertools.combinations(set2, j_index):
                    item = list(i)
                    item.extend(j)
                    combs.append(item)
    if len(combs) == 0:
        combs.append(data)
    return combs


def get_combinations(n, label='stable'):
    return get_split_combinations(n)

    # result = []
    # data = xrange(n)
    # min_comb_length = min(n, max(MIN_COMB_SIZE, n-7))
    # for i in xrange(min_comb_length, n+1):
    #     result.extend([i for i in itertools.combinations(data, i)])
    # return result
    # return [range(n)]


def calculate_num_records():
    # All 200 patients
    vf_counts = [(8, 15), (16, 1), (15, 1), (13, 3), (5, 76), (11, 8), (17, 1), (12, 8), (10, 8), (9, 13), (6, 34), (7, 32)]
    # Only those patients with stable or progressing labels
    # vf_counts = [(16,1) ,(15,1) ,(13,1) ,(12,5), (11,6) ,(10,6) ,(9,9) ,(8,12) ,(7,22) ,(6,24) ,(5,47)]

    sum = 0
    for i in vf_counts:
        print "%s, %s, %s" %(i[1], i[0], i[1] * len(get_combinations(i[0])))
        sum += i[1] * len(get_combinations(i[0]))
    return sum


def fetch_patient_data():
    cursor_2, connection_2 = connect()
    # query_label = "select cast(patient_id as text), \"Truth\" from detailed_results"
    query_label = "select cast(patient_id as text), \"Truth\" from detailed_results where \"Truth\" = 'progressing' or \"Truth\"='stable' limit 70"
    cursor_2.execute(query_label)

    records_label = cursor_2.fetchall()

    patient_map = dict()
    for label in records_label:
        patient_map[label[0]] = label[1]

    cursor, connection = connect()
    ids = ", ".join(patient_map.keys())
    # query = "select * from points_r_label where (id=833 and righteye=1) or (id=34504 and righteye=0)"
    query = "select * from points_r_label where id IN (%s)" % ids
    cursor.execute(query)
    records = cursor.fetchall()

    data = []
    for record in records:
        patient = dict()
        for index, desc in enumerate(cursor.description):
            patient[desc[0]] = record[index]
        patient['truth'] = patient_map[str(patient['id'])]
        data.append(patient)

    export_data_to_csv(data)
    cursor.close()
    connection.close()
    cursor_2.close()
    connection_2.close()
    return data

if __name__ == '__main__':
    fetch_patient_data()
    create_patient_diff()
    # print calculate_num_records()