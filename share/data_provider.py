import psycopg2
import pandas as pd
import json

# Note that 'id' is included here but will be dropped before the training step.
# It is necessary in intermediate step for ensuring that records from the same patient
# is not present in both the training and test sets.
FEATURES = ['id', 'truth', 'nvisit', 'age', 'vfi', 'md', 'psd', 'tdp1', 'tdp2', 'tdp3', 'tdp4', 'tdp5', 'tdp6', 'tdp7', 'tdp8', 'tdp9', 'tdp10', 'tdp11', 'tdp12', 'tdp13', 'tdp14', 'tdp15', 'tdp16', 'tdp17', 'tdp18', 'tdp19', 'tdp20', 'tdp21', 'tdp22', 'tdp23', 'tdp24', 'tdp25', 'tdp27', 'tdp28', 'tdp29', 'tdp30', 'tdp31', 'tdp32', 'tdp33', 'tdp34', 'tdp36', 'tdp37', 'tdp38', 'tdp39', 'tdp40', 'tdp41', 'tdp42', 'tdp43', 'tdp44', 'tdp45', 'tdp46', 'tdp47', 'tdp48', 'tdp49', 'tdp50', 'tdp51', 'tdp52', 'tdp53', 'tdp54', 'pdp1', 'pdp2', 'pdp3', 'pdp4', 'pdp5', 'pdp6', 'pdp7', 'pdp8', 'pdp9', 'pdp10', 'pdp11', 'pdp12', 'pdp13', 'pdp14', 'pdp15', 'pdp16', 'pdp17', 'pdp18', 'pdp19', 'pdp20', 'pdp21', 'pdp22', 'pdp23', 'pdp24', 'pdp25', 'pdp27', 'pdp28', 'pdp29', 'pdp30', 'pdp31', 'pdp32', 'pdp33', 'pdp34', 'pdp36', 'pdp37', 'pdp38', 'pdp39', 'pdp40', 'pdp41', 'pdp42', 'pdp43', 'pdp44', 'pdp45', 'pdp46', 'pdp47', 'pdp48', 'pdp49', 'pdp50', 'pdp51', 'pdp52', 'pdp53', 'pdp54', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10', 's11', 's12', 's13', 's14', 's15', 's16', 's17', 's18', 's19', 's20', 's21', 's22', 's23', 's24', 's25', 's26', 's27', 's28', 's29', 's30', 's31', 's32', 's33', 's34', 's35', 's36', 's37', 's38', 's39', 's40', 's41', 's42', 's43', 's44', 's45', 's46', 's47', 's48', 's49', 's50', 's51', 's52', 's53', 's54', 'td1', 'pd1', 'td2', 'pd2', 'td3', 'pd3', 'td4', 'pd4', 'td5', 'pd5', 'td6', 'pd6', 'td7', 'pd7', 'td8', 'pd8', 'td9', 'pd9', 'td10', 'pd10', 'td11', 'pd11', 'td12', 'pd12', 'td13', 'pd13', 'td14', 'pd14', 'td15', 'pd15', 'td16', 'pd16', 'td17', 'pd17', 'td18', 'pd18', 'td19', 'pd19', 'td20', 'pd20', 'td21', 'pd21', 'td22', 'pd22', 'td23', 'pd23', 'td24', 'pd24', 'td25', 'pd25', 'td26', 'pd26', 'td27', 'pd27', 'td28', 'pd28', 'td29', 'pd29', 'td30', 'pd30', 'td31', 'pd31', 'td32', 'pd32', 'td33', 'pd33', 'td34', 'pd34', 'td35', 'pd35', 'td36', 'pd36', 'td37', 'pd37', 'td38', 'pd38', 'td39', 'pd39', 'td40', 'pd40', 'td41', 'pd41', 'td42', 'pd42', 'td43', 'pd43', 'td44', 'pd44', 'td45', 'pd45', 'td46', 'pd46', 'td47', 'pd47', 'td48', 'pd48', 'td49', 'pd49', 'td50', 'pd50', 'td51', 'pd51', 'td52', 'pd52', 'td53', 'pd53', 'td54', 'pd54']


def connect():
    conn_string = "host='104.196.246.100' dbname='glaucoma' user='postgres' password='postgres'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor, conn


def execute_query(query, close=True):
    cursor, connection = connect()
    cursor.execute(query)
    result = cursor.fetchall()

    if close:
        cursor.close()
        connection.close()
    return (result, cursor, connection)


def fetch_patient_data():
    records_label = execute_query(
        "select cast(patient_id as text), \"Truth\" from detailed_results where \"Truth\" = 'progressing' or \"Truth\"='stable'"
    )[0]

    patient_map = dict()
    for label in records_label:
        patient_map[label[0]] = label[1]

    ids = ", ".join(patient_map.keys())
    query = "select * from points_r_label where id IN (%s)" % ids
    records, cursor, _ = execute_query(query)

    data = []
    for record in records:
        patient = dict()
        for index, desc in enumerate(cursor.description):
            patient[desc[0]] = record[index]
        patient['truth'] = patient_map[str(patient['id'])]
        data.append(patient)
    df = pd.read_json(json.dumps(data))

    for col_name in list(df.columns.values):
        if col_name not in FEATURES:
            df.drop(col_name, axis=1, inplace=True)
    return df

# if __name__ == '__main__':
#     fetch_patient_data()