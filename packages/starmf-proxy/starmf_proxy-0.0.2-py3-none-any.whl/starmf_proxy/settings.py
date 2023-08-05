import os
import secrets
from .enums import SupportedServices

wsdl_default_map = {
    SupportedServices.ADDITIONAL_SERVICES: 'http://bsestarmfdemo.bseindia.com/MFUploadService/MFUploadService.svc?singleWsdl',
    SupportedServices.DIRECT_PAYMENT_GATEWAY: 'http://bsestarmfdemo.bseindia.com/StarMFPaymentGatewayService/StarMFPaymentGatewayService.svc?singleWsdl',
    SupportedServices.FILE_UPLOAD: 'http://bsestarmfdemo.bseindia.com/StarMFFileUploadService/StarMFFileUploadService.svc?singleWsdl',
    SupportedServices.ORDER_ENTRY: 'http://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc?singleWsdl'
}


def getuserid():
    return os.getenv("USER_ID")


def getmemberid():
    return os.getenv("MEMBER_ID")


def getpassword():
    return os.getenv("PASSWORD")


def getpasskey():
    return secrets.token_hex(5)


def getwsdl(service: SupportedServices):
    return os.getenv(service.name, wsdl_default_map[service])
