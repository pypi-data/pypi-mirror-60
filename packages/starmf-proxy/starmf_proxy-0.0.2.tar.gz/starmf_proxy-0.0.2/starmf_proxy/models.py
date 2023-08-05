from dataclasses import dataclass
from datetime import date
from dateutil.relativedelta import relativedelta
from .enums import AccountType, Holding, TaxStatus, OccupationCode, ClientType, CommunicationMode, MandateType


@dataclass
class Login:
    UserId: str
    MemberId: str
    Password: str
    PassKey: str


@dataclass
class MfApi:
    Flag: str
    UserId: str
    EncryptedPassword: str
    param: str


@dataclass
class Account:
    acc_type: AccountType
    acc_number: str
    micr_no: str
    ifsc_code: str
    is_default: bool = False


@dataclass
class Dmat:
    dp_id: str
    clt_id: str


@dataclass
class Address:
    line1: str
    city: str
    state: str
    pincode: str
    country: str
    line2: str = ''
    line3: str = ''


@dataclass
class Contact:
    phone: str
    fax: str


@dataclass
class UccMfd:
    code: str
    holding: Holding
    tax_status: TaxStatus
    occupation_code: OccupationCode
    applicant_name_1: str
    dob: str
    gender: str
    pan: str
    client_type: ClientType
    first_account: Account
    address: Address
    email: str
    communication_mode: CommunicationMode
    div_pay_mode: str
    mobile: str
    applicant_name_2: str = ''
    applicant_name_3: str = ''
    father: str = ''
    husband: str = ''
    gaurdian: str = ''
    nominee: str = ''
    nominee_relation: str = ''
    gaurdian_pan: str = ''
    default_dp: str = ''
    cdsl: Dmat = None
    nsdl: Dmat = None
    second_account: Account = None
    third_account: Account = None
    fourth_account: Account = None
    fifth_account: Account = None
    cheque_name: str = ''
    residence_contact: Contact = None
    office_contact: Contact = None
    pan_2: str = ''
    pan_3: str = ''
    mapin_no: str = ''
    foreign_address: Address = None
    foreign_res_contact: Contact = None
    foreign_off_contact: Contact = None

    def __get_gaurdian_name(self):
        if self.tax_status == TaxStatus.OnBehalfOfMinor:
            return self.gaurdian
        else:
            return self.husband if self.father == '' else self.husband

    def __get_dmat(self, d: Dmat):
        if d is not None:
            return f'{d.dp_id}|{d.clt_id}'
        else:
            return '|'

    def __get_account(self, a: Account):
        if a is not None:
            return f"{a.acc_type.name}|{a.acc_number}|{a.micr_no}|{a.ifsc_code}|{'Y' if a.is_default else 'N'}"
        else:
            return '||||'

    def __get_address(self, a: Address):
        if a is not None:
            return f'{a.line1}|{a.line2}|{a.line3}|{a.city}|{a.state}|{a.pincode}|{a.country}'
        else:
            return '||||||'

    def __get_contact(self, c: Contact):
        if c is not None:
            return f'{c.phone}|{c.fax}'
        else:
            return f'|'

    def __repr__(self):
        return (f'{self.code}|{self.holding.name}|{self.tax_status.value}|{self.occupation_code.value}|'
                f'{self.applicant_name_1}|{self.applicant_name_2}|{self.applicant_name_3}|{self.dob}|{self.gender}|'
                f'{self.__get_gaurdian_name()}|{self.pan}|{self.nominee}|{self.nominee_relation}|{self.gaurdian_pan}|'
                f'{self.client_type.name}|{self.default_dp}|{self.__get_dmat(self.cdsl)}|{self.__get_dmat(self.nsdl)}|'
                f'{self.__get_account(self.first_account)}|{self.__get_account(self.second_account)}|'
                f'{self.__get_account(self.third_account)}|{self.__get_account(self.fourth_account)}|'
                f'{self.__get_account(self.fifth_account)}|{self.cheque_name}|{self.__get_address(self.address)}|'
                f'{self.__get_contact(self.residence_contact)}|{self.__get_contact(self.office_contact)}|{self.email}|'
                f'{self.communication_mode.name}|{self.div_pay_mode}|{self.pan_2}|{self.pan_3}|{self.mapin_no}|'
                f'{self.__get_address(self.foreign_address)}|{self.__get_contact(self.foreign_res_contact)}|'
                f'{self.__get_contact(self.foreign_off_contact)}|{self.mobile}')


Register = UccMfd


@dataclass
class Mandate:
    client_code: str
    amount: float
    mandate_type: MandateType
    account: Account
    start_date: date
    end_date: date = date.today() + relativedelta(years=100)

    def __get_account(self, a: Account):
        if a is not None:
            return f"{a.acc_number}|{a.acc_type.name}|{a.ifsc_code}|{a.micr_no}"
        else:
            return '|||'

    def __repr__(self):
        return (f'{self.client_code}|{self.amount}|{self.mandate_type.value[0]}|{self.__get_account(self.account)}|'
                f'{self.start_date.strftime("%d/%m/%Y")}|{self.end_date.strftime("%d/%m/%Y")}')


@dataclass
class MandateStatus:
    member_code: str
    client_code: str
    mandate_id: str

    def __repr__(self):
        return f'{self.member_code}|{self.client_code}|{self.mandate_id}'


@dataclass
class DirectPGReqModel:
    AccNo: str
    BankID: str
    ClientCode: str
    EncryptedPassword: str
    IFSC: str
    LogOutURL: str
    MemberCode: str
    Mode: str
    Orders: str
    TotalAmount: str


@dataclass
class OrderEntryModel:
    TransCode: str
    TransNo: str
    OrderId: str
    UserID: str
    MemberId: str
    ClientCode: str
    SchemeCd: str
    BuySell: str
    BuySellType: str
    DPTxn: str
    OrderVal: str
    AllRedeem: str
    FolioNo: str
    EUIN: str
    EUINVal: str
    MinRedeem: str
    DPC: str
    Qty: str = ''
    Remarks: str = ''
    KYCStatus: str = ''
    RefNo: str= ''
    SubBrCode: str = ''
    IPAdd: str = ''
    Password: str = None
    PassKey: str = ''
    Parma1: str = ''
    Param2: str = ''
    Param3: str = ''


class XorIsipOrderModel:
    TransactionCode: str
    UniqueRefNo: str
    SchemeCode: str
    MemberCode: str
    ClientCode: str
    UserId: str
    InternalRefNo: str
    TransMode: str
    DpTxnMode: str
    StartDate: str
    FrequencyType: str
    FrequencyAllowed: str
    InstallmentAmount: str
    NoOfInstallment: str
    Remarks: str
    FolioNo: str
    FirstOrderFlag: str
    Brokerage: str
    MandateID: str
    SubberCode: str
    Euin: str
    EuinVal: str
    DPC: str
    XsipRegID: str
    IPAdd: str
    Password: str
    PassKey: str
    Param1: str
    Param2: str
    Param3: str

