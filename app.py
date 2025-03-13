from flask import Flask, jsonify
import requests
import xml.etree.ElementTree as ET
import threading
import time

app = Flask(__name__)

# متغیر برای ذخیره آخرین رویداد بررسی‌شده
last_checked_id = None

def fetch_events_from_xml():
    """دریافت رویدادها از فایل XML"""
    url = "http://irsc.ut.ac.ir/events_list_fa.xml"
    response = requests.get(url)
    root = ET.fromstring(response.content)

    events = []
    for item in root.findall('item'):
        event = {
            'id': item.find('id').text,
            'reg1': item.find('reg1').text,
            'dis1': item.find('dis1').text,
            'reg2': item.find('reg2').text,
            'dis2': item.find('dis2').text,
            'reg3': item.find('reg3').text,
            'dis3': item.find('dis3').text,
            'mag': item.find('mag').text,
            'dep': item.find('dep').text,
            'long': item.find('long').text,
            'lat': item.find('lat').text,
            'date': item.find('date').text,
        }
        events.append(event)
    return events

def get_latest_event(events):
    """دریافت رویداد با بالاترین ID"""
    if not events:
        return None
    return max(events, key=lambda x: int(x['id']))

def check_for_new_events():
    """بررسی وجود رویداد جدید"""
    global last_checked_id
    events = fetch_events_from_xml()
    latest_event = get_latest_event(events)
    
    if latest_event and latest_event['id'] != last_checked_id:
        last_checked_id = latest_event['id']
        return latest_event
    return None

def poll_events():
    """بررسی دوره‌ای رویدادها"""
    while True:
        new_event = check_for_new_events()
        if new_event:
            print("رویداد جدید:", new_event)
        time.sleep(60)  # هر ۶۰ ثانیه بررسی کند

@app.route('/latest-event', methods=['GET'])
def get_latest_event_api():
    """API برای دریافت آخرین رویداد"""
    latest_event = check_for_new_events()
    if latest_event:
        return jsonify(latest_event)
    return jsonify({"message": "هیچ رویداد جدیدی وجود ندارد"}), 404

if __name__ == '__main__':
    # شروع بررسی دوره‌ای در یک thread جداگانه
    threading.Thread(target=poll_events, daemon=True).start()
    app.run(debug=True)
