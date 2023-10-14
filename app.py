import os
import random
import json
import time

from datetime import timedelta
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_mysqldb import MySQL
import MySQLdb.cursors
from operator import itemgetter

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=['https://mook-popup.netlify.app'])

# MySQL 설정 (앞서와 동일)
mysql = MySQL(app)

@app.route('/score/submit', methods=['POST'])
def score_submit():
    data = request.json
    print(data)
    
    scores = [data.get(str(i), 0) for i in range(1, 10)]
    initialFormData = data.get('initialFormData')
    selectedKeyword = data.get('selectedKeyword')
    card_ans = data.get('card_ans')
    
    cur = mysql.connection.cursor()
    try:
        cur.execute("""
            INSERT INTO Qr_Table
            (name, phone_number, keyword1, card_ans, score1, score2, score3, score4, score5, score6, score7, score8, score9) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            initialFormData['name'], initialFormData['phoneNumber'],
            selectedKeyword, card_ans, *scores
        ))
        mysql.connection.commit()
        return jsonify({"message": "성공적으로 제출되었습니다."}), 200
    except Exception as e:
        print("Error:", e)  # 로그 기록 혹은 출력
        return jsonify({"message": str(e)}), 500
    finally:
        cur.close()

@app.route('/getRecentData', methods=['GET'])
def get_recent_data():
    def custom_sort(item):
        _, score = item
        return float('-inf') if score is None else score
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  # DictCursor 사용
    try:
        cur.execute("SELECT * FROM Qr_Table ORDER BY user_id DESC LIMIT 350") 
        data = cur.fetchall()

        for item in data:
            print(item)
            scores = [(i, item[f'score{i}']) for i in range(1, 10)]
            # scores.sort(key=itemgetter(1), reverse=True)
            scores.sort(key=custom_sort, reverse=True)
            item['sorted_scores'] = scores
        
        return jsonify(data), 200
    except Exception as e:
        print("Error:", e)  
        return jsonify({"message": str(e)}), 500
    finally:
        cur.close()

if __name__ == "__main__":
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host="0.0.0.0", port=port, debug=True)
    app.run(debug=True)
