from app.models.base import PlatformSpecificationIn, BaseModelIn
from app.types.fields import CompanyCodeField, NationalCodeField


class LegalUserAuthenticationIn(BaseModelIn):
    company_code: CompanyCodeField
    current_platform: PlatformSpecificationIn
    password: str


class RealUserAuthenticationIn(BaseModelIn):
    national_code: NationalCodeField
    current_platform: PlatformSpecificationIn
    password: str
