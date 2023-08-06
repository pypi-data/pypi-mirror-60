from django.contrib.admin import AdminSite as DjangoAdminSite
from edc_locator.models import SubjectLocator
from inte_screening.models import SubjectScreening
from inte_consent.models import SubjectConsent
from inte_subject.models import SubjectRequisition, SubjectVisit


class AdminSite(DjangoAdminSite):
    site_title = "INTE Subject"
    site_header = "INTE Subject"
    index_title = "INTE Subject"
    site_url = "/administration/"


inte_test_admin = AdminSite(name="inte_test_admin")

inte_test_admin.register(SubjectScreening)
inte_test_admin.register(SubjectConsent)
inte_test_admin.register(SubjectLocator)
inte_test_admin.register(SubjectVisit)
inte_test_admin.register(SubjectRequisition)
