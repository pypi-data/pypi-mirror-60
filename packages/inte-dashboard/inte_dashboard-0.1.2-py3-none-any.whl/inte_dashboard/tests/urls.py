from django.urls.conf import path, include
from edc_appointment.admin_site import edc_appointment_admin

from inte_ae.admin_site import inte_ae_admin
from inte_consent.admin_site import inte_consent_admin
from inte_prn.admin_site import inte_prn_admin
from inte_screening.admin_site import inte_screening_admin
from inte_subject.admin_site import inte_subject_admin
from django.contrib import admin
from django.views.generic.base import RedirectView
from edc_action_item.admin_site import edc_action_item_admin
from edc_consent.admin_site import edc_consent_admin
from edc_dashboard.views import AdministrationView
from edc_locator.admin_site import edc_locator_admin
from edc_reference.admin_site import edc_reference_admin

from .admin import inte_test_admin

urlpatterns = [
    path("accounts/", include("edc_auth.urls")),
    path("admin/", include("edc_auth.urls")),
    path("admin/", edc_appointment_admin.urls),
    path("admin/", edc_consent_admin.urls),
    path("admin/", inte_test_admin.urls),
    path("admin/", inte_ae_admin.urls),
    path("admin/", inte_prn_admin.urls),
    path("admin/", edc_reference_admin.urls),
    path("admin/", edc_locator_admin.urls),
    path("admin/", inte_consent_admin.urls),
    path("admin/", inte_subject_admin.urls),
    path("admin/", inte_screening_admin.urls),
    path("admin/", edc_action_item_admin.urls),
    path("admin/", admin.site.urls),
    path("administration/", AdministrationView.as_view(), name="administration_url"),
    path("inte_ae/", include("inte_ae.urls")),
    path("inte_prn/", include("inte_prn.urls")),
    path("inte_screening/", include("inte_screening.urls")),
    path("inte_consent/", include("inte_consent.urls")),
    path("inte_subject/", include("inte_subject.urls")),
    path("edc_action_item/", include("edc_action_item.urls")),
    path("edc_adverse_event/", include("edc_adverse_event.urls")),
    path("edc_appointment/", include("edc_appointment.urls")),
    path("edc_auth/", include("edc_auth.urls")),
    path("edc_consent/", include("edc_consent.urls")),
    path("edc_dashboard/", include("edc_dashboard.urls")),
    path("edc_data_manager/", include("edc_data_manager.urls")),
    path("edc_device/", include("edc_device.urls")),
    path("edc_lab/", include("edc_lab.urls")),
    path("edc_export/", include("edc_export.urls")),
    path("edc_lab_dashboard/", include("edc_lab_dashboard.urls")),
    path("edc_locator/", include("edc_locator.urls")),
    path("edc_pharmacy_dashboard/", include("edc_pharmacy_dashboard.urls")),
    path("edc_protocol/", include("edc_protocol.urls")),
    path("edc_reference/", include("edc_reference.urls")),
    path("edc_subject_dashboard/", include("edc_subject_dashboard.urls")),
    path("edc_visit_schedule/", include("edc_visit_schedule.urls")),
    path("subject/", include("inte_dashboard.urls")),
    path("", RedirectView.as_view(url="admin/"), name="home_url"),
]
