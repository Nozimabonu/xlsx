import csv
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from customer.forms import CustomerModelForm
from customer.models import Customer
import json

from openpyxl import Workbook
from app.models import Product

# Create your views here.


def customers(request):
    search_query = request.GET.get('search')
    if search_query:
        customer_list = Customer.objects.filter(
            Q(full_name__icontains=search_query) | Q(address__icontains=search_query))
    else:
        customer_list = Customer.objects.all()
    context = {
        'customer_list': customer_list,
    }
    return render(request, 'customer/customer-list.html', context)


def add_customer(request):
    form = CustomerModelForm()
    if request.method == 'POST':
        form = CustomerModelForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('customers')

    context = {
        'form': form,
    }

    return render(request, 'customer/add-customer.html', context)


def delete_customer(request, pk):
    customer = Customer.objects.get(id=pk)
    if customer:
        customer.delete()
        messages.add_message(
            request,
            messages.SUCCESS,
            'Customer successfully deleted'
        )
        return redirect('customers')


def edit_customer(request, pk):
    customer = Customer.objects.get(id=pk)
    form = CustomerModelForm(instance=customer)
    if request.method == 'POST':
        form = CustomerModelForm(instance=customer, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()

            return redirect('customers')
    context = {
        'form': form,
    }
    return render(request, 'customer/update-customer.html', context)


def export_data(request):
    format = request.GET.get('format', 'csv')
    if format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=customers.csv'
        writer = csv.writer(response)
        writer.writerow(['Id', 'Full Name', 'Email', 'Phone Number', 'Address'])
        for customer in Customer.objects.all():
            writer.writerow([customer.id, customer.full_name, customer.email, customer.phone_number, customer.address])


    elif format == 'json':
        response = HttpResponse(content_type='application/json')
        data = list(Customer.objects.all().values('full_name', 'email', 'phone_number', 'address'))
        # response.content = json.dumps(data, indent=4)
        response.write(json.dumps(data, indent=4))
        response['Content-Disposition'] = 'attachment; filename=customers.json'

    elif format == 'xlsx':
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="products.xlsx"'

        wb = Workbook()
        ws = wb.active
        ws.title = "Products"

        headers = ['full_name', 'email', 'phone_number', 'address']
        ws.append(headers)

        products = Product.objects.all()
        for product in products:
            ws.append([product.name, product.price, product.quantity])

            wb.save(response)
            return response

    else:
        response = HttpResponse(status=404)
        response.content = 'Bad request'

    return response
