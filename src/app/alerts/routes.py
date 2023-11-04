from src.app.alerts import router

@router.post("/alertmanager-callback", status_code=200)
async def webhook():
    """{
  "receiver": "webhook-critical",
  "status": "firing",
  "alerts": [
    {
      "status": "firing",
      "labels": {
        "alertname": "PrometheusTargetMissing",
        "instance": "postgres_exporter:9187",
        "job": "postgres",
        "severity": "critical"
      },
      "annotations": {
        "description": "A Prometheus target has disappeared. An exporter might be crashed. VALUE = 0  LABELS: map[__name__:up instance:postgres_exporter:9187 job:postgres]",
        "summary": "Prometheus target missing (instance postgres_exporter:9187)"
      },
      "startsAt": "2023-11-03T19:23:04.807Z",
      "endsAt": "0001-01-01T00:00:00Z",
      "generatorURL": "http://ec694b615a13:9090/graph?g0.expr=up+%3D%3D+0\\u0026g0.tab=1",
      "fingerprint": "1b0137ea1b8c08b6"
    }
  ],
  "groupLabels": {
    "alertname": "PrometheusTargetMissing"
  },
  "commonLabels": {
    "alertname": "PrometheusTargetMissing",
    "instance": "postgres_exporter:9187",
    "job": "postgres",
    "severity": "critical"
  },
  "commonAnnotations": {
    "description": "A Prometheus target has disappeared. An exporter might be crashed. VALUE = 0  LABELS: map[__name__:up instance:postgres_exporter:9187 job:postgres]",
    "summary": "Prometheus target missing (instance postgres_exporter:9187)"
  },
  "externalURL": "http://b16f1e84e073:9093",
  "version": "4",
  "groupKey": "{}:{alertname=\"PrometheusTargetMissing\"}",
  "truncatedAlerts": 0
}"""
