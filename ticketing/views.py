from django.shortcuts import render
from rest_framework import generics, status
from ticketing.serializers import CarSerializer, TicketSerializer, DynamicCarSerializer, CarSlotSerializer, SignupSerializer
from ticketing.models import Car, Ticket, Device
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
import heapq
import traceback, jwt, uuid
from django.conf import settings
from .utils import is_login
# Create your views here.

AVAILABLE_SLOTS = [11,12,13,14,15,16,17,18,19,10]
heapq.heapify(AVAILABLE_SLOTS)

class CarView(APIView):
    def get(self, request):
        model = Car.objects.all()
        serializer = CarSerializer(model, many = True)
        return Response(serializer.data)

    @is_login
    def post(self, request, id):
        if id is None:
            return Response("Device unauthorized", status=status.HTTP_403_FORBIDDEN)
        data = request.data
        data['deviceId']=id
        serializer = CarSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TicketView(APIView):
    def get(self, request):
        model = Ticket.objects.all()
        serializer = TicketSerializer(model, many = True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TicketSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CarDetail(APIView):
    def get(self, request):
        regno = request.GET.get('regno')
        if regno is None:
            return Response("Registration no. can't be null", status = status.HTTP_400_BAD_REQUEST)
        else:
            try:
                model = Car.objects.get(pk=regno)
            except Car.DoesNotExist:
                return Response("Car not found", status = status.HTTP_404_NOT_FOUND)

            serializer = CarSerializer(model)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        regno = request.GET.get('regno')
        if regno is None:
            return Response("Registration no. can't be null", status = status.HTTP_400_BAD_REQUEST)
        else:
            try:
                model = Car.objects.get(regno= regno)
            except Car.DoesNotExist:
                return Response("Car not found", status = status.HTTP_404_NOT_FOUND)

            model.delete()
            return Response(status=status.HTTP_200_OK)
    

class Parking(APIView):
    @is_login
    def get(self,request,id):
        if id is None:
            return Response("Device unauthorized", status=status.HTTP_403_FORBIDDEN)
        regno = request.GET.get('regno')
        if regno is None:
            return Response("Registration no. can't be null", status = status.HTTP_400_BAD_REQUEST)
        else:
            try:
                car = Car.objects.get(regno = regno)
            except Car.DoesNotExist:
                return Response("Car does not exist in our database", status = status.HTTP_404_NOT_FOUND)

            if car.slot!=100:
                return Response("Car is already parked", status = status.HTTP_208_ALREADY_REPORTED)

            data = request.data
            data['carId'] = car.regno
            data['slotAllotted'] =  heapq.heappop(AVAILABLE_SLOTS)
            data_car = request.data
            data_car['level'] = int(str(data['slotAllotted'])[0])
            data_car['slot'] = int(str(data['slotAllotted'])[1])
            serializer = TicketSerializer(data=data)
            car_serializer = CarSerializer(car, data=data_car)
            if serializer.is_valid():
                if car_serializer.is_valid():
                    serializer.save()
                    car_serializer.save()
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Leave(APIView):
    @is_login
    def get(self, request, id):
        if id is None:
            return Response("Device unauthorized", status=status.HTTP_403_FORBIDDEN)
        ticketNo = request.GET.get('ticketNo')
        if ticketNo is None:
            return Response("Ticket no. can't be null", status = status.HTTP_400_BAD_REQUEST)
        else:
            try:
                ticket = Ticket.objects.get(ticketNo = ticketNo)
            except Ticket.DoesNotExist:
                return Response("OOPS! This ticket has not been issued from our system", status = status.HTTP_404_NOT_FOUND)

            if ticket.slotAllotted=='00':
                return Response("You have already taken you vehicle from our space", status=status.HTTP_404_NOT_FOUND)

            data = request.data
            heapq.heappush(AVAILABLE_SLOTS, int(ticket.slotAllotted))
            data['slotAllotted'] =  '00'
            data['carId'] = ticket.carId
            car = Car.objects.get(regno=ticket.carId)
            data_car = request.data
            data_car['level'] = 100
            data_car['slot'] = 100
            serializer = TicketSerializer(ticket, data=data)
            car_serializer = CarSerializer(car, data=data_car)
            if serializer.is_valid():
                if car_serializer.is_valid():
                    serializer.save()
                    car_serializer.save()
                
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegNoByColor(APIView):

    def get(self, request):
        color = request.GET.get('color')
        if color is None:
            return Response("Color can't be null", status = status.HTTP_400_BAD_REQUEST)
        else:
            try:
                cars = Car.objects.filter(color__exact=color).values('regno')
            except Car.DoesNotExist:
                return Response("OOPS! We don't have any car in this color", status = status.HTTP_404_NOT_FOUND)

        serializer = DynamicCarSerializer(cars, many=True)
        return Response(serializer.data, status=status.HTTP_302_FOUND)

class SlotByReg(APIView):

    def get(self, request):    
        regno = request.GET.get('regno')
        if regno is None:
            return Response("Registration no. can't be null", status = status.HTTP_400_BAD_REQUEST)
        else:
            try:
                cars = Car.objects.filter(regno=regno).values('slot')
            
            except Car.DoesNotExist:
                return Response("Car not found", status = status.HTTP_404_NOT_FOUND)

        serializer = CarSlotSerializer(cars, many=True)
        return Response(serializer.data, status=status.HTTP_302_FOUND)


class SlotByColor(APIView):

    def get(self, request):    
        color = request.GET.get('color')
        if color is None:
            return Response("Color can't be null", status = status.HTTP_400_BAD_REQUEST)
        else:
            try:
                cars = Car.objects.filter(color__exact=color).values('slot')
            except Car.DoesNotExist:
                return Response("OOPS! We don't have any car in this color", status = status.HTTP_404_NOT_FOUND)

        serializer = CarSlotSerializer(cars, many=True)
        return Response(serializer.data, status=status.HTTP_302_FOUND)


@api_view(['POST'])
def signup(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        if username == "" or username.isspace():
            return Response("Username can't be null", status = status.HTTP_404_NOT_FOUND)
        else:
            hash = Device.encrypt(Device, password)
            hash = hash.decode("utf-8")
            newDevice = Device(name=username, password=hash)
            newDevice.save()
            return Response("Registered successfully", status = status.HTTP_200_OK)
    except Exception:
        if settings.DEBUG:
            print(traceback.format_exc())
        return Response("Could not register! Please try again",status=404)

@api_view(['POST'])
def login(request):
    try:
        userName = request.data.get('username')
        if userName == "" or userName.isspace():
            return Response("Username is a mandatory field",status=403)
        device = Device.objects.get(name=userName)
        if device.compare(password=request.data.get('password')):
            response = Response(status=200)
            payload = {
                'id': str(device.id)
            }
            value = jwt.encode(payload, settings.SECRET_KEY).decode("utf-8")
            response.set_cookie('jwt', value)
            return response
        else:
            return Response("Wrong password",status=status.HTTP_403_FORBIDDEN)
    except Exception:
        if settings.DEBUG:
            print(traceback.format_exc())
        return Response("Username not found",status=status.HTTP_404_NOT_FOUND)

class DeviceView(APIView):
    def get(self, request):
        model = Device.objects.all()
        serializer = SignupSerializer(model, many = True)
        return Response(serializer.data)