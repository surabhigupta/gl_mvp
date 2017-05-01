from flask import Flask, render_template, request, jsonify
from flask.ext.compress import Compress
import psycopg2
import json

app = Flask(__name__)
# Automatically compress this app's responses using gzip
Compress(app)
app.debug = True

coords = [(3, 0), (4, 0), (5, 0), (6, 0), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (1, 2), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2), (8, 2), (0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4), (1, 5), (2, 5), (3, 5), (4, 5), (5, 5), (6, 5), (7, 5), (8, 5), (2, 6), (3, 6), (4, 6), (5, 6), (6, 6), (7, 6), (3, 7), (4, 7), (5, 7), (6, 7)]


def get_data_map():
    map = dict()
    for i in xrange(54):
        map[str(i+1)] = coords[i]
    return map

@app.route('/')
def get_homepage():
    return render_template('base.html')


def vf_indices():
    return filter(lambda x:x!=25 and x!=34, xrange(54))

@app.route("/vf/<eye_id>", methods=['GET'])
def get_VF_view_model(eye_id):
    data = get_patient_data(eye_id)
    coord_map = get_data_map()
    view_model = []
    metadata = []
    global_metrics = {}
    for index, eye in enumerate(data):
        result = []
        for i in vf_indices():
            coods = coord_map[str(i+1)]
            result.append({
                "x": coods[0],
                "y": coods[1],
                "sensitivity": eye['s' + str(i+1)],
                "td": eye['td' + str(i+1)],
                "tdp": eye['tdp' + str(i+1)],
                "pd": eye['pd' + str(i+1)],
                "pdp": eye['pdp' + str(i+1)]
            })
        view_model.append(result)
        # TODO: Add min and max of TD and PD to the list
        # This will be used to generate one legend for the all the VFs of an eye
        yrs_string = 'yrs' if eye['yearsfollowed'] > 1.0 else 'yr'
        metadata.append({
            'nmeas': "Visit #%d" % abs(eye['nmeas']),
            'yearsfollowed': "(%.1f %s)" % (eye['yearsfollowed'], yrs_string) if index > 0 else '',
            'md': "MD: %.2f (p < %.3f)" % (eye['md'], eye['mdprob']),
            'psd': "PSD: %.2f (p < %.3f)" % (eye['psd'], eye['psdprob']),
            'vfi': "VFI: %.2f" % eye['vfi']
        })
    global_metrics['min_td'] = min(map(lambda x:aggregate_value('td', 'min', x), data))
    global_metrics['max_td'] = max(map(lambda x:aggregate_value('td', 'max', x), data))
    global_metrics['min_pd'] = min(map(lambda x:aggregate_value('pd', 'min', x), data))
    global_metrics['max_pd'] = max(map(lambda x:aggregate_value('pd', 'max', x), data))

    return json.dumps({"data": view_model, "metadata": metadata, "global": global_metrics})


def aggregate_value(metric_type, min_or_max, eye):
    return min([eye[metric_type + str(i+1)] for i in vf_indices()]) if min_or_max == 'min' else max([eye[metric_type + str(i+1)] for i in vf_indices()])

@app.route("/patients")
def get_patients():
    cursor, connection = connect()
    cursor.execute("select distinct on (id, righteye) id, righteye from points_r_label")
    records = cursor.fetchall()

    data = []
    for record in records:
        patient = dict()
        patient['id'] = record[0]
        patient['eye'] = 'Right' if record[1] == 1 else "Left"
        data.append(patient)

    cursor.close()
    connection.close()
    return json.dumps({"data":data})


@app.route("/labels/<eye_id>", methods=['GET'])
def get_labels(eye_id):
    cursor, connection = connect()

    id, eye_display = eye_id.split('_')
    eye = "OS" if eye_display == 'Left' else "OD"

    query = "select * from detailed_results where patient_id=%s and eye='%s'" % (id, eye)
    cursor.execute(query)
    record = cursor.fetchone()
    result = dict()
    for index, desc in enumerate(cursor.description):
        value = record[index] if (record and record[index] != '-') else 'unclear'
        result[desc[0]] = value

    def add_rank_to_result(table_name, column_name):
        query = "select round(r.d_rnk) from (select ptid, eye, %s, dense_rank() over (order by %s) as d_rnk from %s) r where ptid=%s and eye='%s';" % (column_name, column_name, table_name, id, eye)
        cursor.execute(query)
        record = cursor.fetchone()
        result[column_name] = "%.1f" % (record[0]*100.0/13156)

    # add_rank_to_result("md_slope", "md_slope")
    # add_rank_to_result("vfi_slope", "vfi_slope")

    return json.dumps(result)

def get_patient_data(eye_id):
    cursor, connection = connect()
    # 63511
    id, eye_display = eye_id.split('_')
    eye = 0 if eye_display == 'Left' else 1

    query = "select * from points_r_label where id=%s and righteye=%d" % (id, eye)
    cursor.execute(query)
    records = cursor.fetchall()

    data = []
    for record in records:
        patient = dict()
        for index, desc in enumerate(cursor.description):
            patient[desc[0]] = record[index]
        data.append(patient)

    cursor.close()
    connection.close()
    return data


def connect():
    conn_string = "host='104.196.246.100' dbname='glaucoma' user='postgres' password='postgres'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor, conn


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
