# Telemetry Server

## KU Solar Car


[Link to Medium Article on Deploying](https://medium.com/@dmahugh_70618/deploying-a-flask-app-to-google-app-engine-faa883b5ffab)


[Setup GCloud Terminal](https://cloud.google.com/appengine/docs/standard/python3/setting-up-environment)

Make sure you are in the TelemetryServer Repo in terminal before continuing

1. Once you get GCloud setup on your terminal, make sure you have the correct project by default

`gcloud config set project MY-PROJECT-ID`

In this case 'MY-PROJECT-ID' is ku-solar-car-b87af

2. Make sure your app.yaml file is correct

##### `runtime: python37`

##### `entrypoint: gunicorn -b :8080 main:app`


3. Then to deploy
`gcloud app deploy`

Creates the URL: https://ku-solar-car-b87af.appspot.com

4. Post To Server (endpoint is `/car`)

Make sure your POST Request body is in the following format with `timeInSecondsSinceMidnight` being the key to the values of each sensor at said time in seconds.  POST request can take multiple times in seconds at a time.  Make sure values are in the following order as well to ensure correct order of values.

`{
    "timeInSecondsSinceMidnight": {
        "battery_voltage": {
            "value":"500"
        },
        "battery_current": {
            "value":"500"
        },
        "battery_temperature": {
            "value":"500"
        },
        "bms_fault": {
            "value":"1"
        },
        "gps_time": {
            "value":"500"
        },
        "gps_lat": {
            "value":"500"
        },
        "gps_lon": {
            "value":"500"
        },
        "gps_velocity_east": {
            "value":"500"
        },
        "gps_velocity_north": {
            "value":"500"
        },
        "gps_velocity_up": {
            "value":"500"
        },
        "gps_speed": {
            "value":"500"
        },
        "solar_voltage": {
            "value":"500"
        },
        "solar_current": {
            "value":"500"
        },
        "motor_speed": {
            "value":"500"
        }
    }
}`

