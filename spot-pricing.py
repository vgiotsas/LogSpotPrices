import boto3, json
from datetime import datetime, timedelta
from influxdb import InfluxDBClient

ec2 = boto3.resource('ec2')
client = boto3.client(service_name='ec2')

start_time = datetime.utcnow() - timedelta(minutes=1)

instance_type = "m3.medium"
operating_system = 'Linux/UNIX'
availability_zone = "us-east-1a"

prices = client.describe_spot_price_history(InstanceTypes=[
                                                instance_type
                                            ],
                                            AvailabilityZone=availability_zone,
                                            StartTime=start_time,
                                            Filters=[
                                                {
                                                    'Name': 'product-description',
                                                    'Values': [
                                                        operating_system,
                                                    ]
                                                },
                                            ],
                                            )

# Connect to the DB
client = InfluxDBClient('localhost', 8086, 'root', 'root', 'spotprices')
measurement = "LINUX_SPOT_PRICES"
tags = {"instance_type": instance_type,
        "availability_zone": availability_zone}

for point in prices['SpotPriceHistory']:
    timestamp = point['Timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')
    price = point['SpotPrice']

    point_data = [
        {
            "measurement": measurement,
            "tags": tags,
            "time": timestamp,
            "fields": {
                "spot_price": price
            }
        }
    ]

    client.write_points(point_data)


