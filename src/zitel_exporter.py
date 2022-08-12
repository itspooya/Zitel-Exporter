import requests
import uuid
import hashlib
from prometheus_client import Gauge, start_http_server
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
session_id = str(uuid.uuid4().hex) + str(uuid.uuid4().hex)


def login(hostname, username, password):
    global session_id
    salt_response = requests.post(f"http://{hostname}/cgi-bin/http.cgi", json={
        "cmd": 997,
        "method": "POST",
        "sessionId": str(uuid.uuid4().hex) + str(uuid.uuid4().hex)
    })
    salt = salt_response.json()["message"]
    salted_password = salt + hashlib.md5(password.encode("utf-8")).hexdigest()
    salted_password_hash = hashlib.sha256(salted_password.encode("utf-8")).hexdigest()
    json_data = {
        "username": username,
        "passwd": salted_password_hash,
        "sessionId": str(uuid.uuid4().hex) + str(uuid.uuid4().hex),
        "cmd": 100,
        "method": "POST"
    }
    response = requests.post(f"http://{hostname}/cgi-bin/http.cgi", json=json_data, verify=False)

    if response.status_code == 200:
        try:
            session_id = response.json()["sessionId"]
        except ValueError:
            logging.critical("Failed to get session id")
            logging.critical("Password Incorrect")
            exit(1)

        login_data = {
            "cmd": 80,
            "method": "GET",
            "Language": "EN",
            "sessionId": session_id

        }
        loginresponse = requests.post(f"http://{hostname}/cgi-bin/http.cgi", json=login_data, verify=False)
        if loginresponse.status_code == 200:
            if loginresponse.text:
                if loginresponse.json()["success"]:
                    return session_id


class Exporter:
    def __init__(self, hostname, username, password, port):
        """
        Enter Hostname, Username and Password of zitel modem

        :param hostname: hostname of zitel modem
        :param username: username of zitel modem
        :param password: password of zitel modem
        :param port:     exporter's port
        """
        self.username = username
        self.password = password
        self.session_id = login(hostname, username, password)
        self.hostname = hostname
        self.registered_metrics = 0
        self.keys = {}
        self.port = port
        self.sched = BlockingScheduler()

    def get_session_id(self):
        self.session_id = login(self.hostname,self.username,self.password)

    def schedule_jobs(self):
        start_http_server(int(self.port))
        self.sched.add_job(self.covert_to_prometheus_metric,"interval",seconds=10)
        self.sched.add_job(self.get_session_id,"interval",minutes=45)
        self.sched.start()

    def get_celltower_stats(self):
        json_data = {

            "sessionId": session_id,
            "cmd": 82,
            "method": "POST",
            "lang": "EN"
        }
        response = requests.post(f"http://{self.hostname}/cgi-bin/http.cgi", json=json_data)
        if response.status_code == 200:
            return response.json()

    def get_traffic_stats(self):
        json_data = {
            "cmd": 18,
            "method": "GET",
            "lang": "EN",
            "sessionId": session_id
        }
        response = requests.post(f"http://{self.hostname}/cgi-bin/http.cgi", json=json_data)
        if response.status_code == 200:
            return response.json()

    def covert_to_prometheus_metric(self):
        stats = {}
        celltower_stats = self.get_celltower_stats()
        traffic_stats = self.get_traffic_stats()
        if not celltower_stats or not traffic_stats:
            self.get_session_id()
            celltower_stats = self.get_celltower_stats()
            traffic_stats = self.get_traffic_stats()
        if celltower_stats and traffic_stats:
            if celltower_stats["success"]:
                separator = "$"
                FIELD_SEPERATOR = "@"
                temp_stats = celltower_stats["message"].replace(FIELD_SEPERATOR, ":")
                temp_stats = temp_stats.replace(separator, "\n")
                # convert to dictionary
                stats = {}
                for line in temp_stats.split("\n"):
                    if line:
                        key, value = line.split(":")
                        stats[key.replace(" ", "_")] = value
                # Delete UL_MCS and DL_MCS
                del stats["UL_MCS"]
                del stats["DL_MCS"]
                # Convert RRCState to Integer
                if stats["RRCState"] == "CONNECTED":
                    stats["RRCState"] = 1
                else:
                    stats["RRCState"] = 0
            else:
                self.get_session_id()
                logging.critical("Failed to get celltower stats")
                exit(1)
        if traffic_stats["success"]:
            for key, value in traffic_stats.items():
                stats[key] = value
            del stats["flowStatistics"]
        if "success" in stats:
            del stats["success"]
        if "cmd" in stats:
            del stats["cmd"]
        print(stats)
        if self.registered_metrics == 0:
            for key, value in stats.items():
                self.keys[key] = Gauge(f"{key.lower().replace('/', '')}", f"{key}", ["hostname"])
                self.keys[key].labels(self.hostname).set(value)
                self.registered_metrics = 1
        elif self.registered_metrics == 1:
            for key in self.keys.keys():
                self.keys[key].labels(self.hostname).set(stats[key])
