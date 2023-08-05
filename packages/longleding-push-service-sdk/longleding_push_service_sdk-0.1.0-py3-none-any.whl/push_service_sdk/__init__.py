# -*- coding: utf-8 -*-
import re
from . import pushService_pb2
from .grpc_client import PushServiceGRPCClient, PushServiceException

__all__ = ["init_service", "send_register_code", "send_login_code", "send_change_password_code"]
_push_service_grpc_client: PushServiceGRPCClient

_phone_number_reg = re.compile(r"(13\d|14[579]|15[^4\D]|17[^49\D]|18\d)\d{8}")


def _verify_phone_numbers(phone_numbers: str) -> bool:
    return bool(_phone_number_reg.match(phone_numbers))


def init_service(endpoint: str, source: str) -> None:
    global _push_service_grpc_client
    assert type(endpoint) == str, "endpoint must be a str"
    assert type(source) == str, "source must be a str"
    _push_service_grpc_client = PushServiceGRPCClient(endpoint=endpoint, source=source)


def send_register_code(phone_numbers: str = "", code: str = "") -> None:
    global _push_service_grpc_client
    assert _push_service_grpc_client is not None, "push service sdk must be init first"
    assert type(phone_numbers) == str, "phone_numbers must be a str"
    assert type(code) == str, "code must be a str"
    assert _verify_phone_numbers(phone_numbers), "illegal phone number"
    _push_service_grpc_client.send_sms(phone_numbers, pushService_pb2.SMSMessageType.REGISTER_CODE, {"code": code})


def send_login_code(phone_numbers: str = "", code: str = "") -> None:
    global _push_service_grpc_client
    assert _push_service_grpc_client is not None, "push service sdk must be init first"
    assert type(phone_numbers) == str, "phone_numbers must be a str"
    assert type(code) == str, "code must be a str"
    assert _verify_phone_numbers(phone_numbers), "illegal phone number"
    _push_service_grpc_client.send_sms(phone_numbers, pushService_pb2.SMSMessageType.LOGIN_CODE, {"code": code})


def send_change_password_code(phone_numbers: str = "", code: str = "") -> None:
    global _push_service_grpc_client
    assert _push_service_grpc_client is not None, "push service sdk must be init first"
    assert type(phone_numbers) == str, "phone_numbers must be a str"
    assert type(code) == str, "code must be a str"
    assert _verify_phone_numbers(phone_numbers), "illegal phone number"
    _push_service_grpc_client.send_sms(phone_numbers, pushService_pb2.SMSMessageType.CHANGE_PASSWORD_CODE, {"code": code})
