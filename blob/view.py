import json
import requests

from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from django.views.decorators.cache import cache_page
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from blob.settings import headers, connect_str, storage_url


def load_orders(redirect_url):
    """
    Access the orders(InProcess or Shipped) from liftoff and store them as blobs in Azure container
    :param redirect_url:
    :return redirect_url:
    """
    # Create the BlobServiceClient object which will be used to create a container client
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    if redirect_url == 'home_page':
        orders = requests.get("https://odata.liftoff.shop/odata/v1/Order?$filter=Status eq 'InProcess'",
                              headers=headers).json()['value']
        for order in orders:
            file_name = str(order['OrderNumber']) + '.' + str(order['SubmissionDate'].split('T')[0]) + ".json"
            blob1 = BlobClient.from_connection_string(conn_str=connect_str, container_name="new-orders",
                                                      blob_name=file_name)
            blob2 = BlobClient.from_connection_string(conn_str=connect_str, container_name="updated-orders",
                                                      blob_name=file_name)
            blob3 = BlobClient.from_connection_string(conn_str=connect_str, container_name="deleted-orders",
                                                      blob_name=file_name)
            if not blob1.exists() and not blob2.exists() and not blob3.exists():
                blob_client = blob_service_client.get_blob_client(container='new-orders', blob=file_name)
                blob_client.upload_blob(json.dumps(order))

    elif redirect_url == 'completed_orders':
        orders = requests.get("https://odata.liftoff.shop/odata/v1/Order?$filter=Status eq 'Shipped' ",
                              headers=headers).json()['value']
        for order in orders:
            file_name = str(order['OrderNumber']) + '.' + str(order['SubmissionDate'].split('T')[0]) + ".json"
            blob1 = BlobClient.from_connection_string(conn_str=connect_str, container_name='completed-orders',
                                                      blob_name=file_name)
            blob2 = BlobClient.from_connection_string(conn_str=connect_str, container_name='deleted-orders',
                                                      blob_name=file_name)
            if not blob1.exists() and not blob2.exists():
                blob_client = blob_service_client.get_blob_client(container='completed-orders', blob=file_name)
                blob_client.upload_blob(json.dumps(order))
    return redirect(redirect_url)


# def home_page(request):
#     added = False
#     if request.is_ajax():  # Asynchronous JavaScript And XML / JSON
#         print("Ajax request")
#         json_data = {
#             "added": added,
#             "removed": not added,
#         }
#     return render(request, 'testing/testing.html', {})


@cache_page(60 * 60)
def home_page(request):
    """
    Access new orders from Azure 'new-orders' container,
    splits the order number and submission date from
    order's name and lists them to home page.
    """
    container_client = ContainerClient(storage_url, 'new-orders', credential=None)
    new_orders = container_client.list_blobs()

    order_list = []
    i = 1
    for order in new_orders:
        order_no = order['name'].split('.')[0]
        creation_date = order['name'].split('.')[1]
        order_no_and_date_tuple = [order_no, creation_date]
        order_list.append(order_no_and_date_tuple)
        i += 1

    order_list.sort(reverse=True)
    n = 1
    for order in order_list:
        order.insert(0, n)
        n += 1
    paginator = Paginator(order_list, 12)
    page = request.GET.get('page', 1)
    orders = paginator.page(page)
    context = {
        'new_orders': orders,
        'page_obj': orders,
        'redirect_url': 'home_page',
    }
    # print(order_list)
    return JsonResponse(order_list, safe=False)
    # return render(request, 'index.html', context)


def display_order(request, container, order_no, date):
    """
    Access a single blob from Azure container and displays it
    :param request:
    :param container:
    :param order_no:
    :param date:
    :return:
    """
    response = requests.get(f'{storage_url}{container}/{order_no}.{date}.json').text

    data = json.loads(response)
    context = {
        'order': data,
    }
    return JsonResponse(data, safe=False)
    # return render(request, 'display_order.html', context)


@cache_page(60 * 60)
def updated_orders(request):
    """
    Access orders(with appended tracking number) from Azure
    'updated-orders' container, splits the order number and
    submission date from order's name and lists them
    """
    container_client = ContainerClient(storage_url, 'updated-orders',  credential=None)
    updated_order = container_client.list_blobs()
    order_list = []
    i = 1
    for order in updated_order:
        order_no = order['name'].split('.')[0]
        creation_date = order['name'].split('.')[1]
        order_no_and_date_tuple = [order_no, creation_date]
        order_list.append(order_no_and_date_tuple)
        i += 1
    order_list.sort(reverse=True)
    n = 1
    for order in order_list:
        order.insert(0, n)
        n += 1
    page = request.GET.get('page', 1)
    paginator = Paginator(order_list, 6)
    orders = paginator.page(page)
    context = {
        'orders': orders,
        'container': 'updated-orders',
        'redirect_url': 'updated_orders'
    }
    return JsonResponse(order_list, safe=False)
    # return render(request, 'orders_temp.html', context)


@cache_page(60 * 60)
def completed_orders(request):
    """
    Access shippped orders from Azure
    'completed-orders' container, splits the order number and
    submission date from order's name and lists them
    """
    container_client = ContainerClient(storage_url, 'completed-orders', credential=None)
    updated_order = container_client.list_blobs()
    order_list = []
    i = 1
    for order in updated_order:
        order_no = order['name'].split('.')[0]
        creation_date = order['name'].split('.')[1]
        order_no_and_date_tuple = [order_no, creation_date]
        order_list.append(order_no_and_date_tuple)
        i += 1
    order_list.sort(reverse=True)
    n = 1
    for order in order_list:
        order.insert(0, n)
        n += 1
    page = request.GET.get('page', 1)
    paginator = Paginator(order_list, 6)
    orders = paginator.page(page)
    context = {
        'orders': orders,
        'container': 'completed-orders',
        'redirect_url': 'completed_orders',
    }
    return JsonResponse(order_list, safe=False)
    # return render(request, 'orders_temp.html', context)


def add_tracking_no(request):
    """
    Receives the tracking and order number, gets
    shipment from the order and updates this
    shipment with the received tracking number
    """
    tracking_no = request.POST.get('tracking_no')
    order_no = request.POST.get('order_no')
    date = request.POST.get('date')
    shipment_id = requests.get(f'https://odata.liftoff.shop/odata/v1/Shipment?$filter=OrderId eq {order_no}',
                               headers=headers).json()['value'][0]['Id']
    body_parameters = {
        'TrackingNumber': tracking_no,
    }
    url = f'https://odata.liftoff.shop/odata/v1/Shipment({shipment_id})'
    r = requests.patch(url, headers=headers, json=body_parameters)

    # After updating the tracking No, shift the blob order from 'orders' container to 'updated' container
    if r.status_code == 200:
        # Source
        source_container_name = "new-orders"
        source_file_path = order_no + '.' + date + '.json'
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        source_blob = f'{storage_url}{source_container_name}/{source_file_path}'

        # Target
        target_container_name = "updated-orders"
        target_file_path = order_no + '.' + date + '.json'
        copied_blob = blob_service_client.get_blob_client(target_container_name, target_file_path)
        copied_blob.start_copy_from_url(source_blob)

        # If you would like to delete the source file
        remove_blob = blob_service_client.get_blob_client(source_container_name, source_file_path)
        remove_blob.delete_blob()
        messages.info(request, 'Tracking No appended Successfully!')
    return redirect('/')


def remove_order(request, container, order_no, date):
    """
    Adds the order blob from given container to the 'deleted-orders' container
    :param request:
    :param container:
    :param order_no:
    :param date:
    :return:
    """
    # Source
    source_file_path = str(order_no) + '.' + date + '.json'
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    source_blob = f'{storage_url}{container}/{source_file_path}'

    # Target
    target_container_name = "deleted-orders"
    target_file_path = str(order_no) + '.' + date + '.json'
    copied_blob = blob_service_client.get_blob_client(target_container_name, target_file_path)
    copied_blob.start_copy_from_url(source_blob)

    # If you would like to delete the source file
    remove_blob = blob_service_client.get_blob_client(container, source_file_path)
    remove_blob.delete_blob()
    messages.info(request, f'Order# {order_no} removed Successfully!')
    if container == 'completed-orders':
        return redirect('completed_orders')
    return redirect('updated_orders')


# @cache_page(60 * 60)
def deleted_orders(request):
    """
    Access all deleted orders from 'deleted-orders' container,
    splits the order number and submission date from order's
    name and lists them
    :param request:
    :return:
    """
    container_client = ContainerClient(storage_url, 'deleted-orders',  credential=None)
    deleted_order_list = container_client.list_blobs()
    order_list = []
    i = 1
    for order in deleted_order_list:
        order_no = order['name'].split('.')[0]
        creation_date = order['name'].split('.')[1]
        order_id_and_date_tuple = [order_no, creation_date]
        order_list.append(order_id_and_date_tuple)
        i += 1
    order_list.sort(reverse=True)
    n = 1
    for order in order_list:
        order.insert(0, n)
        n += 1
    page = request.GET.get('page', 1)
    paginator = Paginator(order_list, 4)
    orders = paginator.page(page)
    # messages.info(request, 'yes man yes')
    context = {
        'deleted_orders': orders,
        'redirect_url': 'deleted_orders',
    }
    print(request.COOKIES)
    response = render(request, 'deleted_orders.html', context)
    # response.delete_cookie('cookie_name1')

    return response
