# -*- coding: utf-8 -*-
import time as time_b
from typing import Dict

import grpc

from . import pushService_pb2, pushService_pb2_grpc


class PushServiceException(Exception):
    """ Operation Log Service Exception. """
    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def __new__(*args, **kwargs):
        pass


class PushServiceGRPCClient:
    _endpoint = None
    _retry_time = 3
    _retry_interval = 2

    def __init__(self, endpoint: str, source: str):
        self._endpoint = endpoint
        self._source = source

    def send_sms(self, phone_numbers: str, sms_type: pushService_pb2.SMSMessageType, params: Dict[str, str] = {}):
        with grpc.insecure_channel(self._endpoint) as channel:
            stub = pushService_pb2_grpc.SMSServiceStub(channel)
            sms_message = pushService_pb2.SMSMessage(
                source=self._source,
                phoneNumbers=phone_numbers,
                type=sms_type,
                params=params)
            response = None
            error = None
            for i in range(self._retry_time):
                try:
                    response = stub.SendSMS(sms_message)
                    break
                except grpc.RpcError as e:
                    error = e
                    time_b.sleep(self._retry_interval * (i + 1))
            if response is None:
                raise error
            if response.code != 0:
                raise PushServiceException(response.msg)
            return response
