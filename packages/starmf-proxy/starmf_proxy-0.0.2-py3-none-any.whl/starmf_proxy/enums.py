from enum import Enum, auto


class NoValue(Enum):
    def __repr__(self):
        return '<%s.%s>' % (self.__class__.__name__, self.name)


class SupportedServices(Enum):
    ADDITIONAL_SERVICES = auto(),
    DIRECT_PAYMENT_GATEWAY = auto(),
    FILE_UPLOAD = auto(),
    ORDER_ENTRY = auto()


class Holding(Enum):
    SI = auto(),
    JO = auto(),
    AS = auto()


class TaxStatus(NoValue):
    Individual = '01'
    OnBehalfOfMinor = '02'


class OccupationCode(NoValue):
    Business = '01'
    Services = '02'
    Professional = '03'
    Agriculture = '04'
    Retired = '05'
    Housewife = '06'
    Student = '07'
    Others = '08'


class AccountType(Enum):
    SB = 1,
    CE = 2,
    NE = 3,
    NO = 4


class ClientType(Enum):
    P = 1,
    D = 2


class TransactionCode(NoValue):
    New = 'NEW',
    Modification = 'MOD',
    Cancellation = 'CXL'


class CommunicationMode(Enum):
    P = auto(),
    E = auto(),
    M = auto()


class AdditionalServicesFlag(NoValue):
    FATCA_UPLOAD = '01',
    UCC_MFD = '02',
    PAYMENT_GATEWAY = '03',
    CHANGE_PASSWORD = '04',
    UCC_MFI = '05',
    MANDATE_REGISTRATION = '06',
    STP_REGISTRATION = '07',
    SWP_REGISTRATION = '08',
    CLIENT_ORDER_PAYMENT_STATUS = '11',
    CLIENT_REDEMPTION_SMS_AUTHENTICATION = '12',
    CKYC_UPLOAD = '13',
    MANDATE_STATUS = '14',
    SYSTEMATIC_PLAN_AUTHENTICATION = '15'


class MandateType(NoValue):
    XSIP = 'X',
    ISIP = 'I',
    EMandate = 'E'

class TransactionType(NoValue):
    Purchase = 'P',
    Redemption = 'R'
