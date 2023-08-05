"""
Cloud Watch Interaction tool
"""
import boto3
import gevent.monkey

gevent.monkey.patch_all()

from datetime import datetime

DATE_FMT = "%Y-%m-%d %H:%M:%S"


class CWLInteraction:
    """
    Wrapper on boto3 CloudWatch logs
    """

    def __init__(self, region=None, aws_access_key=None, aws_secret_key=None):
        try:
            self.client = None
            self.region = region
            self.aws_access_key = aws_access_key
            self.aws_secret_key = aws_secret_key
        except Exception as e:
            raise e

    def init(self):
        self.client = boto3.client(
            "logs",
            region_name=self.region,
            aws_access_key_id=self.aws_access_key,
            aws_secret_access_key=self.aws_secret_key,
        )

    @staticmethod
    def parse_and_print_events(events):
        """Pretty print logs with datetime"""
        print("There are {} events to look through!".format(len(events)))

        for event in events:
            # ingestion_time = event['ingestionTime']
            timestamp = event["timestamp"]
            message = event["message"]
            message_dt = datetime.utcfromtimestamp(float(timestamp) / 1000.0).strftime(
                DATE_FMT
            )
            print(message_dt + ": " + message)

    def get_log_events(self, log_group, log_stream):
        """Get log events for given log stream"""

        resp = self.client.get_log_events(
            logGroupName=log_group, logStreamName=log_stream, startFromHead=True
        )

        response_code = resp["ResponseMetadata"]["HTTPStatusCode"]

        if response_code == 200:

            events = resp["events"]

            if not events:  # return False if no logs
                return False

            self.parse_and_print_events(events)

            forward_token = resp["nextForwardToken"]

            print("There is maybe more to see, checking for more logs!")

            while True:  # continue until no more logs found

                resp = self.client.get_log_events(
                    logGroupName=log_group,
                    logStreamName=log_stream,
                    nextToken=forward_token,
                    startFromHead=True,
                )
                if response_code == 200:

                    next_forward_token = resp["nextForwardToken"]

                    if (
                        next_forward_token == forward_token
                    ):  # if no more logs, token will be the same
                        print("Nope, no more logs")
                        print("\n\n")
                        break  # no more logs
                    else:
                        forward_token = (
                            # reset for potential multiple loops
                            next_forward_token
                        )

                    events = resp["events"]

                    self.parse_and_print_events(events)

                else:
                    raise ValueError(
                        "Request failed with response code: {}".format(response_code)
                    )

            return True  # had logs

        else:
            raise ValueError(
                "Request failed with response code: {}".format(response_code)
            )
