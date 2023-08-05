import zeep

from starmf_proxy.enums import SupportedServices, AdditionalServicesFlag
from starmf_proxy.models import Login, MfApi, Register, Mandate, MandateStatus, OrderEntryModel
from starmf_proxy.settings import getuserid, getmemberid, getpassword, getpasskey, getwsdl


class BaseProxy:
    def __init__(self, wsdl, cache: bool):
        self.wsdl = wsdl
        self.cache = cache
        self.user_id = getuserid()
        self.member_id = getmemberid()
        self.password = getpassword()
        self.pass_key = getpasskey()
        if self.cache is True:
            self.client = zeep.CachingClient(wsdl=self.wsdl)
        else:
            self.client = zeep.Client(wsdl=self.wsdl)

    def dump(self):
        self.client.wsdl.dump()

    def ensure_login(self, encrypted_password: str, pass_key: str = None):
        if encrypted_password is None:
            lm = Login(self.user_id, self.member_id,
                       self.password, self.pass_key if pass_key is None else pass_key)
            (code, data) = self.login(lm)
            if code == '100':
                encrypted_password = data
            else:
                raise Exception()
        return encrypted_password

    def login(self, login_model: Login):
        result = self.client.service.getPassword(**vars(login_model))
        (code, data) = result.split('|')
        return code, data

    def call_action(self, action, params):
        print(vars(params))
        return self.client.service[action](**vars(params))


class MfUploadService(BaseProxy):
    def __init__(self, cache: bool):
        wsdl = getwsdl(SupportedServices.ADDITIONAL_SERVICES)
        super().__init__(wsdl, cache)

    def __get_mfapi(self, param_model, flag: AdditionalServicesFlag, encrypted_password: str = None):
        return MfApi(flag.value[0], self.user_id, self.ensure_login(encrypted_password), str(param_model))

    def register_client(self, register_model: Register, encrypted_password: str = None):
        return self.call_action('MFAPI',
                                self.__get_mfapi(register_model, AdditionalServicesFlag.UCC_MFD, encrypted_password))

    def register_mandate(self, mandate: Mandate, encrypted_password: str = None):
        return self.call_action('MFAPI',
                                self.__get_mfapi(mandate, AdditionalServicesFlag.MANDATE_REGISTRATION,
                                                 encrypted_password))

    def get_mandate_status(self, client_code: str, mandate_id: str, encrypted_password: str = None):
        mandate_status_model = MandateStatus(member_code=self.member_id, client_code=client_code, mandate_id=mandate_id)
        return self.call_action('MFAPI', self.__get_mfapi(mandate_status_model, AdditionalServicesFlag.MANDATE_STATUS,
                                                          encrypted_password))


class StarMFPaymentGatewayService(BaseProxy):
    def __init__(self, cache: bool):
        wsdl = getwsdl(SupportedServices.ADDITIONAL_SERVICES)
        super().__init__(wsdl, cache)

    def payment_gateway_api(self):
        return self.call_action(None, None)


class MFOrderEntry(BaseProxy):
    def __init__(self, cache: bool):
        wsdl = getwsdl(SupportedServices.ORDER_ENTRY)
        super().__init__(wsdl, cache)

    def login(self, login_model: Login):
        result = self.client.service.getPassword(login_model.UserId, login_model.Password, login_model.PassKey)
        (code, data) = result.split('|')
        return code, data

    def order_entry(self, order_model: OrderEntryModel):
        order_model.PassKey = getpasskey()
        encrypted_password = self.ensure_login(order_model.Password, order_model.PassKey)
        order_model.Password = encrypted_password
        return self.call_action('orderEntryParam', order_model)
