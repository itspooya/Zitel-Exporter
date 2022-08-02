# zitel-exporter

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4567b8ef61694bb9b06b41e3cbec69ea)](https://app.codacy.com/gh/itspooya/Zitel-Exporter?utm_source=github.com&utm_medium=referral&utm_content=itspooya/Zitel-Exporter&utm_campaign=Badge_Grade_Settings)

## What is zitel-exporter?

It is a tool to export zitel data Prometheus compatible format

## How to use zitel-exporter?

### docker-compose

1. Edit `docker-compose.yml` and fill in environment variables with your own values
2. Run `docker-compose up -d` or `docker compose up`

### Manual setup

1. Copy example.env to .env and fill in environment variables with your own values
2. pip3 install -r requirements.txt
3. Run `python3 zitel-exporter.py`
4. Open http://IP:PORT/metrics

### Environment variables

| Name           | ENV            | Description                                                                                                             | Required | Default |
|----------------|----------------|-------------------------------------------------------------------------------------------------------------------------|----------|---------|
| Modem Hostname | MODEM_HOSTNAME | Zitel's Modem Hostname that must be in same network as exporter and you must allow it in your firewall if there are any | YES      | -       |
| Modem Username | MODEM_USERNAME | Zitel's Provided Username to access modem configuration                                                                 | YES      | -       |
| Modem Password | MODEM_PASSWORD | Zitel's Provided Password to access modem configuration                                                                 | YES      | -       |
| Exporter Port  | EXPORTER_PORT  | Exporter's Port which you can add to Prometheus                                                                         | YES      | -       |

### DISCLAIMER
    There are no extra features in this exporter and it is only a simple way to export zitel data to Prometheus.
    This software is provided "as is" without warranty of any kind.
    See the license file for more information.