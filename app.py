from flask import Flask, render_template, request, jsonify
from flask.ext.compress import Compress
import psycopg2
import json

app = Flask(__name__)
# Automatically compress this app's responses using gzip
Compress(app)
app.debug = True


@app.route('/')
def get_homepage():
    return render_template('base.html')


@app.route("/dummy")
def get_dummy():
    return json.dumps({"data": [
        {
            "day": 1,
            "hour": 0,
            "files_changed": 4, "insertions": 111, "deletions": 52, "commits": 1
        },
        {
            "day": 1,
            "hour": 2,
            "files_changed": 16, "insertions": 668, "deletions": 29045, "commits": 2
        },
        {
            "day": 1,
            "hour": 3,
            "files_changed": 2, "insertions": 124, "deletions": 99, "commits": 1
        },
        {
            "day": 1,
            "hour": 4,
            "files_changed": 1, "insertions": 1, "deletions": 1, "commits": 3
        },
        {
            "day": 1,
            "hour": 5,
            "files_changed": 6, "insertions": 24, "deletions": 8, "commits": 1
        },
        {
            "day": 2,
            "hour": 0,
            "files_changed": 5, "insertions": 69, "deletions": 101, "commits": 1
        },
        {
            "day": 2,
            "hour": 2,
            "files_changed": 6, "insertions": 12, "deletions": 7, "commits": 2
        },
        {
            "day": 2,
            "hour": 3,
            "files_changed": 11, "insertions": 168, "deletions": 2757, "commits": 1
        },
        {
            "day": 2,
            "hour": 4,
            "files_changed": 19, "insertions": 29331, "deletions": 29316, "commits": 1
        },
        {
            "day": 2,
            "hour": 5,
            "files_changed": 1, "insertions": 2, "deletions": 2, "commits": 1
        },
        {
            "day": 3,
            "hour": 2,
            "files_changed": 18, "insertions": 86, "deletions": 86, "commits": 2
        },
        {
            "day": 3,
            "hour": 4,
            "files_changed": 10, "insertions": 466, "deletions": 352, "commits": 1
        },
        {
            "day": 3,
            "hour": 5,
            "files_changed": 7, "insertions": 376, "deletions": 361, "commits": 1
        },
        {
            "day": 4,
            "hour": 0,
            "files_changed": 9, "insertions": 7052, "deletions": 4732, "commits": 1
        },
        {
            "day": 4,
            "hour": 2,
            "files_changed": 4, "insertions": 53, "deletions": 56, "commits": 1
        },
        {
            "day": 4,
            "hour": 3,
            "files_changed": 11, "insertions": 217, "deletions": 152, "commits": 1
        },
        {
            "day": 4,
            "hour": 4,
            "files_changed": 7, "insertions": 29358, "deletions": 7, "commits": 1
        },
        {
            "day": 4,
            "hour": 5,
            "files_changed": 5, "insertions": 142, "deletions": 73, "commits": 1
        },
        {
            "day": 5,
            "hour": 0,
            "files_changed": 7, "insertions": 520, "deletions": 53, "commits": 1
        },
        {
            "day": 5,
            "hour": 2,
            "files_changed": 2, "insertions": 258, "deletions": 7, "commits": 1
        },
        {
            "day": 5,
            "hour": 3,
            "files_changed": 12, "insertions": 330, "deletions": 182, "commits": 4
        },
        {
            "day": 5,
            "hour": 4,
            "files_changed": 7, "insertions": 2828, "deletions": 35, "commits": 1
        },
        {
            "day": 5,
            "hour": 5,
            "files_changed": 4, "insertions": 37, "deletions": 281, "commits": 1
        },
        {
            "day": 6,
            "hour": 3,
            "files_changed": 12, "insertions": 260, "deletions": 180, "commits": 1
        },
        {
            "day": 7,
            "hour": 5,
            "files_changed": 4, "insertions": 116, "deletions": 74, "commits": 1
        }]})


@app.route("/cached_patient")
def get_cached_patient():
    return json.dumps(
        {"nmeas": -1, "distcylinder": "\\\\N", "pd30": -7, "td39": -14, "pd54": -1, "pd53": -1, "pd52": -6, "pd51": -5,
         "pd50": -1, "s24": 23, "distsphere": "-3.00", "pd25": -1, "pdp54": 1.0, "pdp52": 0.02, "pdp53": 1.0,
         "pdp50": 1.0, "pdp51": 0.02, "mdprob": 0.005, "ismaxmeas": 0, "malfixnum": 1, "s54": 20, "s53": 20, "s52": 15,
         "td19": -8, "td18": -12, "td17": -10, "td16": -11, "td15": -11, "td14": -12, "td13": -11, "td12": -11,
         "td11": -14, "td10": -11, "td8": -11, "pd36": 0, "pdp40": 1.0, "psd": 2.82, "s25": 22, "tdp18": 0.005,
         "tdp19": 0.02, "tdp16": 0.005, "tdp17": 0.005, "tdp14": 0.005, "tdp15": 0.005, "tdp12": 0.005, "tdp13": 0.005,
         "tdp10": 0.005, "tdp11": 0.005, "yearsfollowed": 0.0, "tdp22": 0.005, "pd32": -1, "s44": 20, "s45": 20,
         "td28": -16, "td29": -15, "s40": 22, "s41": 22, "s42": 22, "s43": 20, "td22": -8, "td23": -9, "td20": -8,
         "td21": -9, "s48": 22, "td27": -10, "td24": -9, "td25": -10, "pd38": -11, "pd18": -3, "s19": 19, "s46": 18,
         "tdp29": 0.005, "tdp28": 0.005, "td3": -12, "td2": -12, "td1": -14, "tdp20": 0.005, "tdp27": 0.005, "td6": -11,
         "td5": -13, "tdp24": 0.005, "td34": -9, "td37": -11, "td36": -9, "td31": -5, "td30": -16, "td33": -8,
         "td32": -10, "pd7": -3, "pd6": -2, "pd5": -4, "pd4": -3, "pd3": -3, "td38": -20, "pd1": -6, "s47": 22,
         "tdp8": 0.005, "tdp9": 0.005, "tdp37": 0.005, "tdp4": 0.01, "tdp5": 0.005, "tdp6": 0.005, "tdp7": 0.005,
         "tdp1": 0.005, "tdp2": 0.005, "tdp3": 0.005, "tdp34": 0.005, "tdp36": 0.005, "s18": 17, "tdp30": 0.005,
         "tdp31": 0.005, "tdp32": 0.005, "tdp33": 0.005, "s13": 20, "s12": 19, "s11": 15, "s10": 17, "s17": 20,
         "tdp39": 0.005, "s15": 20, "s14": 19, "td50": -10, "pdp45": 1.0, "righteye": 0, "falsenegrate": 0.08,
         "td40": -10, "td41": -10, "td42": -9, "td43": -10, "td44": -10, "td45": -10, "td46": -13, "td47": -9,
         "td48": -9, "td49": -8, "s49": 22, "pd2": -4, "tdp21": 0.005, "tdp41": 0.005, "tdp40": 0.005, "tdp43": 0.005,
         "tdp42": 0.005, "tdp45": 0.005, "tdp44": 0.005, "tdp47": 0.005, "tdp46": 0.005, "tdp49": 0.005, "tdp48": 0.005,
         "centralval": 18, "distaxis": "\\\\N", "falseposrate": 0.02, "td53": -10, "td52": -15, "pdp18": 1.0,
         "pdp19": 1.0, "blindspoty": -1, "blindspotx": -15, "td54": -9, "pdp12": 1.0, "pdp13": 1.0, "pdp10": 1.0,
         "pdp11": 0.05, "pdp16": 1.0, "pdp17": 1.0, "pdp14": 1.0, "pdp15": 1.0, "s26": 0, "distprev": 0, "tdp52": 0.005,
         "tdp53": 0.005, "tdp50": 0.005, "tdp51": 0.005, "s39": 18, "s38": 11, "tdp54": 0.005, "s35": 0, "s34": 23,
         "s37": 18, "s36": 21, "s31": 27, "s30": 16, "s33": 24, "s32": 23, "pdp27": 1.0, "testdate": 67441,
         "pdp25": 1.0, "pdp24": 1.0, "pdp23": 1.0, "pdp22": 1.0, "pdp21": 1.0, "pdp20": 1.0, "pd31": 3, "s51": 15,
         "pdp29": 0.01, "pdp28": 0.05, "md": -10.85, "pdp43": 1.0, "pdp31": 1.0, "td51": -14, "pd43": -2, "td9": -11,
         "nvisit": 1, "pd13": -3, "pd12": -3, "pd11": -5, "pd10": -2, "pd17": -1, "eyeid": 63511, "pd15": -3,
         "pd14": -3, "s50": 20, "pd19": 1, "psdprob": 0.02, "s27": 19, "s16": 20, "cylinder": "\\\\N", "pdp7": 1.0,
         "site": "bpei", "pdp30": 0.005, "sphere": "+0.00", "pdp32": 1.0, "pdp33": 1.0, "pdp34": 1.0, "pdp36": 1.0,
         "pdp37": 1.0, "pdp38": 0.005, "pdp39": 0.01, "id": 63511, "duration": 455, "axis": "\\\\N", "pd39": -5,
         "s9": 18, "s8": 18, "centralprob": 0.01, "s23": 23, "s3": 15, "td7": -12, "s1": 13, "s20": 21, "s7": 18,
         "s6": 18, "s5": 16, "s4": 14, "s21": 22, "tdp25": 0.005, "pd28": -7, "pd29": -6, "pd27": -2, "pd24": -1,
         "td4": -12, "pd22": 1, "pd23": -1, "pd20": 1, "pd21": 0, "pd48": -1, "pd49": 0, "pd44": -1, "pd45": -1,
         "pd46": -4, "pd47": -1, "pd40": -1, "pd41": -1, "pd42": -1, "malfixrate": 0.0625, "tdp23": 0.005,
         "tdp38": 0.005, "pd16": -2, "pd33": 0, "ght": "3", "pdp44": 1.0, "pdp47": 1.0, "pdp46": 0.05, "pdp41": 1.0,
         "pd9": -2, "vfi": 96.4604766864335, "pdp42": 1.0, "age": 57.4219178082192, "pd8": -3, "pdp49": 1.0,
         "pdp48": 1.0, "s22": 24, "pdp1": 0.05, "pdp2": 1.0, "pdp3": 1.0, "pdp4": 1.0, "pdp5": 0.05, "pdp6": 1.0,
         "s2": 15, "pdp8": 1.0, "pdp9": 1.0, "s28": 11, "s29": 14, "pd34": 0, "pd37": -3, "malfixdenom": 16})


@app.route('/patient')
def get_patient_data():
    cursor, connection = connect()

    cursor.execute("select * from points_r_label where id=%s and righteye=%d" % (str(63511), 0))
    records = cursor.fetchall()

    data = []
    for record in records:
        patient = dict()
        for index, desc in enumerate(cursor.description):
            patient[desc[0]] = record[index]
        data.append(patient)

    cursor.close()
    connection.close()
    return json.dumps({"data": data})


def connect():
    conn_string = "host='104.196.246.100' dbname='glaucoma' user='postgres' password='postgres'"
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    return cursor, conn


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
