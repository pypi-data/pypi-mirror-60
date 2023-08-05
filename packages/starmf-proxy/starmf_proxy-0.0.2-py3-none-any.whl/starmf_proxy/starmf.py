from .enums import SupportedServices
import importlib

_proxy_mod = importlib.import_module('starmf_proxy.proxy')

_service_class_map = {
    SupportedServices.ADDITIONAL_SERVICES: 'MfUploadService',
    SupportedServices.DIRECT_PAYMENT_GATEWAY: 'StarMFPaymentGatewayService',
    SupportedServices.ORDER_ENTRY: 'MFOrderEntry'
}


class Starmf:
    def __init__(self, service: SupportedServices, cache: bool):
        self.current_service_name = service.name
        self.service = getattr(_proxy_mod, _service_class_map[service])(cache)
