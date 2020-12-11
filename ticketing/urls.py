from django.urls import path
from .views import CarView, CarDetail, Parking, Leave, TicketView, RegNoByColor, SlotByReg, SlotByColor, DeviceView
from . import views
#from .views import Parking

urlpatterns = [
    path('home/', CarView.as_view()),
    path('detail/', CarDetail.as_view(), name='car_list'),
    path('park/', Parking.as_view(), name="park_car"),
    path('leave/', Leave.as_view(), name="leave"),
    path('ticket/', TicketView.as_view(), name="ticket_list"),
    path('regNoByColor/', RegNoByColor.as_view(), name="reg_no_by_color"),
    path('slotByReg/', SlotByReg.as_view(), name="slot_by_reg"),
    path('slotByColor/', SlotByColor.as_view(), name="slot_by_reg"),
    path('login/', views.login),
    path('signup/',views.signup),
    path('devices/',DeviceView.as_view())
    #path('park', TicketVi.as_view())
]