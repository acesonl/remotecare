from django.conf.urls import url

from apps.healthperson.healthprofessional.views import\
    HealthProfessionalPhotoView, HealthProfessionalCropPhoto,\
    HealthProfessionalEditPhoto, HealthProfessionalNotificationView,\
    HealthProfessionalOutOfOfficeView, HealthProfessionalOutOfOfficeEdit,\
    HealthProfessionalNotificationEdit, HealthProfessionalPersonaliaView,\
    HealthProfessionalPersonaliaEdit, HealthProfessionalSearchView,\
    HealthProfessionalAddView, HealthProfessionalRemove,\
    HealthProfessionalSetPassword


urlpatterns = (
    url('^add/$',
        HealthProfessionalAddView.as_view(),
        name='healthprofessional_add'),

    url('^search/$',
        HealthProfessionalSearchView.as_view(),
        name='healthprofessional_search'),

    url('^(?P<healthprofessional_session_id>\S+)/crop/photo/$',
        HealthProfessionalCropPhoto.as_view(),
        name='healthprofessional_crop_photo'),

    url('^(?P<healthprofessional_session_id>\S+)/view/photo/$',
        HealthProfessionalPhotoView.as_view(),
        name='healthprofessional_view_photo'),

    url('^(?P<healthprofessional_session_id>\S+)/edit/photo/$',
        HealthProfessionalEditPhoto.as_view(),
        name='healthprofessional_edit_photo'),

    url('^(?P<healthprofessional_session_id>\S+)/view/notification/$',
        HealthProfessionalNotificationView.as_view(),
        name='healthprofessional_view_notification'),

    url('^(?P<healthprofessional_session_id>\S+)/edit/notification/$',
        HealthProfessionalNotificationEdit.as_view(),
        name='healthprofessional_edit_notification'),

    url('^(?P<healthprofessional_session_id>\S+)/view/personalia/$',
        HealthProfessionalPersonaliaView.as_view(),
        name='healthprofessional_view_personalia'),

    url('^(?P<healthprofessional_session_id>\S+)/edit/personalia/$',
        HealthProfessionalPersonaliaEdit.as_view(),
        name='healthprofessional_edit_personalia'),

    url('^(?P<healthprofessional_session_id>\S+)/set/password/$',
        HealthProfessionalSetPassword.as_view(),
        name='healthprofessional_set_password'),

    url('^(?P<healthprofessional_session_id>\S+)/view/out_of_office/$',
        HealthProfessionalOutOfOfficeView.as_view(),
        name='healthprofessional_view_out_of_office'),

    url('^(?P<healthprofessional_session_id>\S+)/edit/out_of_office/$',
        HealthProfessionalOutOfOfficeEdit.as_view(),
        name='healthprofessional_edit_out_of_office'),

    url('^(?P<healthprofessional_session_id>\S+)/remove/$',
        HealthProfessionalRemove.as_view(),
        name='healthprofessional_remove'),
)
