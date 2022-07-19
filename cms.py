import logging.config

import requests

from log_config import LOGGING_CONFIG

logger = logging.getLogger(__file__)


def get_access_token(client_id, cms_client_secret):
    url = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'client_secret': cms_client_secret,
        'grant_type': 'client_credentials',
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json().get('access_token')


def get_products(access_token):
    url = 'https://api.moltin.com/v2/products'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    products = {
        product.get('id'): product.get('name')
        for product in response.json().get('data')
    }
    return products


def get_img_link(access_token, img_id):
    url = f'https://api.moltin.com/v2/files/{img_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json().get('data').get('link').get('href')


def get_product_detail(access_token, product_id):
    url = f'https://api.moltin.com/v2/products/{product_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    product_detail = response.json().get('data')
    name = product_detail.get('name')
    description = product_detail.get('description')
    price = product_detail.get('meta').get(
        'display_price').get('with_tax').get('formatted')
    weight = product_detail.get('weight').get('kg')
    img_id = product_detail.get('relationships').get(
        'main_image').get('data').get('id')
    img_link = get_img_link(access_token, img_id)
    return (name, price, description, weight, img_link)


def get_cart_items(access_token, cart_name):
    url = f'https://api.moltin.com/v2/carts/{cart_name}/items'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart_items = response.json().get('data')
    cart_products = []
    for item in cart_items:
        quantity = item.get('quantity')
        name = item.get('name')
        price = item.get('meta').get('display_price').get(
            'with_tax').get('unit').get('formatted')
        cost = item.get('meta').get('display_price').get(
            'with_tax').get('value').get('formatted')
        product_id = item.get('id')
        product = {
            'name': name, 'quantity': quantity,
            'price': price, 'cost': cost,
            'product_id': product_id
        }
        cart_products.append(product)
    return cart_products


def get_total_cost_cart(access_token, cart_name):
    url = f'https://api.moltin.com/v2/carts/{cart_name}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart = response.json().get('data')
    cost = cart.get('meta').get('display_price').get(
        'with_tax').get('formatted')
    return cost


def add_product_to_cart(access_token, cart_name, product, quantity):
    url = f'https://api.moltin.com/v2/carts/{cart_name}/items'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        'data': {
            'id': product,
            'type': 'cart_item',
            'quantity': quantity
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()


def remove_product_from_cart(access_token, cart_name, product_id):
    url = f'https://api.moltin.com/v2/carts/{cart_name}/items/{product_id}'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
