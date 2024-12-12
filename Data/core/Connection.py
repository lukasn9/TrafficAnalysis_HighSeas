import json
import requests
from PySide6.QtWidgets import QMessageBox
from urllib3 import PoolManager


def check_internet_conn(freq_inp):
    try:
        http = PoolManager(timeout=3.0)
        r = http.request('GET', 'aidetection.great-site.net', preload_content=False)
        code = r.status
        r.release_conn()
        if code == 200:
            return False
    except:
        internet_warning = QMessageBox()
        internet_warning.setWindowTitle("Can't Connect to the Internet")
        internet_warning.setText("There has been an issue with sending data to the server.")
        retry_button = internet_warning.addButton("Retry", QMessageBox.AcceptRole)
        internet_warning.addButton("Analyze Locally", QMessageBox.RejectRole)
        internet_warning.exec()

        if internet_warning.clickedButton() == retry_button:
            return check_internet_conn(freq_inp)
        else:
            freq_inp.setValue(0)
            freq_inp.setEnabled(False)
            freq_inp.setObjectName("freq_inp_disabled")
            freq_inp.setStyleSheet("color: #373737;")
        return True


async def send_data(data_get, krizovatka, toggle_pause):
    url = 'https://aidetection.great-site.net/send_data.php'
    data = []

    if len(data_get) == 0:
        return 0
    for index in range(len(data_get)):
        data_get[index]['place'] = krizovatka
        data.append(data_get[index])

    data = json.dumps(data)
    try:
        response = requests.post(url, data={'data': data}, params={"krizovatka": krizovatka})
        if response.status_code == 200:
            print('Data sent successfully:', response.text)
            toggle_pause(True)

            return 0
        else:
            print('Failed to send data:', response.text)
            raise Exception()
    except:
        toggle_pause(False)
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Sending error")
        msg_box.setText("There has been aan error with sending data to our database. Check your internet connection.")
        msg_box.setIcon(QMessageBox.Information)
        button1 = msg_box.addButton("Retry", QMessageBox.AcceptRole)
        button2 = msg_box.addButton("Analyze locally", QMessageBox.DestructiveRole)
        button3 = msg_box.addButton("Stop", QMessageBox.RejectRole)

        # Execute the message box and wait for the user's choice
        msg_box.exec_()

        # Determine which button was clicked
        if msg_box.clickedButton() == button1:
            await send_data(data_get, krizovatka, toggle_pause)
            # Code for Option 1 action
        elif msg_box.clickedButton() == button2:
            toggle_pause(True)

            return 1
            # Code for Option 2 action
        elif msg_box.clickedButton() == button3:
            toggle_pause(True)

            return 2
        return 2


def get_places():
    url = 'https://aidetection.great-site.net/fetch_places.php'

    response = requests.get(url)
    if response.status_code == 200:
        print('Data got successfully:', response.text)
        return response.json()
    else:
        print('Failed to get data:', response.text)
        return False

def set_live(intersection, live):
    url = 'https://aidetection.great-site.net/set_live.php'

    response = requests.post(url, data={"intersection": intersection, "live": live})
    if response.status_code == 200:
        print('Set live', response.text)
        return True
    else:
        print('Failed to get data:', response.text)
        return False
def check_live(intersection):
    url = 'https://aidetection.great-site.net/check_live.php'

    response = requests.get(url, params={"intersection": intersection})
    if response.status_code == 200:
        return response.json()
    else:
        print('Failed to get data:', response.text)
        return False

def check_availability(intersection, start_time, end_time):
    url = 'https://aidetection.great-site.net/check_availability.php'

    response = requests.get(url, params={'intersection': intersection,
                                         'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                                         'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S')})

    if response.status_code == 200:
        return response.json()
    else:
        print('Failed to get data:', response.text)
        return False


def delete_logs(intersection, start_time, end_time):
    url = 'https://aidetection.great-site.net/delete_data.php'

    response = requests.post(url, data={'intersection': intersection,
                                         'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
                                         'end_time': end_time.strftime('%Y-%m-%d %H:%M:%S')})
    if response.status_code == 200:
        return response.json()
    else:
        print('Failed to connect:', response.text)
        return False


def create_place(krizovatka, lat, long):
    url = 'https://aidetection.great-site.net/create_place.php'

    response = requests.post(url, data={'krizovatka': krizovatka, 'lat': lat, 'long': long})
    if response.status_code == 200:
        print('Data sent successfully:', response.text)
        return True
    else:
        print('Failed to send data:', response.text)
        return False
