import base64
import json
import requests


requests.packages.urllib3.disable_warnings()


class User(object):
    def __init__(self, user_id, token):
        self.id = user_id
        self.token = token


class Basket(object):
    def __init__(self, bid, etag):
        self.id = bid
        self.etag = etag

API_PREFIX = "https://your-SFCC-instance-goes-here/s/yoursite/dw/shop/v17_6/"
CLIENT_ID = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
REGISTERED_EMAIL = "registered@user.com"
REGISTERED_PASSWORD = "yourpassword"
USER_EMAIL = "registered@user.com"

ITEM_ID = "095068990509"
DEFAULT_CARD = {
    "number": "4242424242424242",
    "security_code": "345",
    "holder": "Sarah Conway",
    "card_type": "Visa",
    "expiration_month": 10,
    "expiration_year": 2018
}
ALTER_CARD = {
    "number": "4012888888881881",
    "security_code": "345",
    "holder": "Sarah Conway",
    "card_type": "Visa",
    "expiration_month": 7,
    "expiration_year": 2018
}
PAYMENT_METHOD = 'CREDIT_CARD'

def _url(path):
    return "%s%s?client_id=%s" % (API_PREFIX, path, CLIENT_ID)


def _headers(auth_user=None, etag=None):
    headers = {
        "Content-Type": "application/json",
    }
    if auth_user:
        headers['Authorization'] = "Bearer " + auth_user.token
    if etag:
        headers['If-Match'] = etag
    return headers


def _process_response(r, basket):
    if r.ok:
        if r.headers.get('etag'):
            basket.etag = r.headers['etag']
            print ("Etag changed: %s" % basket.etag)
        return r.json()
    else:
        print (r.text)
        r.raise_for_status()


def create_user(guest=True, email=REGISTERED_EMAIL, password=REGISTERED_PASSWORD):
    url = _url("customers/auth")
    headers = _headers(False, False)
    if guest:
        data = '{"type": "guest"}'
    else:
        headers['Authorization'] = "Basic " + base64.b64encode("%s:%s" % (email, password))
        data = '{"type": "credentials"}'

    r = requests.post(url, headers=headers, data=data, verify=False)
    if r.ok:
        access_token = r.headers['authorization'][7:]  # removing the "Bearer " part
        customer_id = r.json()['customer_id']
        return User(customer_id, access_token)
    else:
        print (r.text)
        r.raise_for_status()


def refresh_user(user):
    url = _url("customers/auth")
    headers = _headers(user)
    data = '{"type": "refresh"}'
    r = requests.post(url, headers=headers, data=data)
    if r.ok:
        access_token = r.headers['authorization'][7:]  # removing the "Bearer " part
        customer_id = r.json()['customer_id']
        return User(customer_id, access_token)
    else:
        print (r.text)
        r.raise_for_status()


def create_basket(user):
    url = _url("baskets")
    r = requests.post(url, headers=_headers(user, False), data='{}', verify=False)
    if r.ok:
        etag = r.headers['etag']
        basket_id = r.json()['basket_id']
        basket = Basket(basket_id, etag)
        return basket
    else:
        print (r.text)
        r.raise_for_status()


def get_baskets_for_user(user):
    url = _url("customers/%s/baskets" % user.id)
    r = requests.get(url, headers=_headers(user))
    if r.ok:
        return r.json()
    else:
        print (r.text)
        r.raise_for_status()


def get_basket(user, basket_id):
    url = _url("baskets/%s" % basket_id)
    r = requests.get(url, headers=_headers(user))
    if r.ok:
        basket_data = r.json()
        basket = Basket(basket_data['basket_id'], r.headers['etag'])
        return (basket, basket_data)
    else:
        print (r.text)
        r.raise_for_status()


def delete_basket(user, basket):
    url = _url("baskets/%s" % basket.id)
    r = requests.delete(url, headers=_headers(user, basket.etag))
    if r.ok:
        return r.text
    else:
        print (r.text)
        r.raise_for_status()


def add_item_to_basket(user, basket, item_id, quantity=1):
    url = _url("baskets/%s/items" % basket.id)
    data = [{
        "product_id": str(item_id),
        "quantity": quantity,
    }]
    print ("url: %s" % url)
    print ("data: %s" % json.dumps(data))       
    r = requests.post(url, headers=_headers(user, basket.etag), data=json.dumps(data), verify=False)
    return _process_response(r, basket)


def delete_item(user, basket, item_id):
    url = _url("baskets/%s/items/%s" % (basket.id, item_id))
    r = requests.delete(url, headers=_headers(user, basket.etag))
    return _process_response(r, basket)


def update_item(user, basket, item_id, product_id, quantity):
    url = _url("baskets/%s/items/%s" % (basket.id, item_id))
    data = {
        "product_id": product_id,
        "quantity": quantity,
    }
    r = requests.patch(url, headers=_headers(user, basket.etag), data=json.dumps(data), verify=False)
    return _process_response(r, basket)


def set_customer_email(user, basket, email):
    url = _url("baskets/%s/customer" % basket.id)
    data = {"email": email}
    r = requests.put(url, headers=_headers(user, basket.etag), data=json.dumps(data), verify=False)
    return _process_response(r, basket)


def get_shipping_methods(user, basket, shipment_id):
    url = _url("baskets/%s/shipments/%s/shipping_methods" % (basket.id, shipment_id))
    r = requests.get(url, headers=_headers(user), verify=False)
    if r.ok:
        results = r.json()
        if r.headers.get('etag'):
            basket.etag = r.headers['etag']
            print ('Etag changed: %s' % basket.etag)
        return results
    else:
        print (r.text)
        r.raise_for_status()


def set_shipping_method(user, basket, shipment_id, shipping_method_id):
    url = _url("baskets/%s/shipments/%s/shipping_method" % (basket.id, shipment_id))
    data = {
        'id': shipping_method_id
    }
    r = requests.put(url, headers=_headers(user, basket.etag), data=json.dumps(data), verify=False)
    return _process_response(r, basket)


def set_shipping_address(user, basket, shipment_id, **kwargs):
    url = _url("baskets/%s/shipments/%s/shipping_address" % (basket.id, shipment_id))
    data = {
        'first_name': kwargs.get('first_name', ''),
        'last_name': kwargs.get('last_name', ''),
        'address1': kwargs.get('address1', ''),
        'city': kwargs['city'],
        'state_code': kwargs['state'],
        'country_code': kwargs['country'],
        'postal_code': kwargs['zip'],
    }
    if kwargs.get('address2'):
        data['address2'] = kwargs['address2']
    if kwargs.get('phone'):
        data['phone'] = kwargs['phone']

    r = requests.put(url, headers=_headers(user, basket.etag), data=json.dumps(data), verify=False)
    return _process_response(r, basket)


def get_payment_methods(user, basket):
    url = _url("baskets/%s/payment_methods" % basket.id)
    r = requests.get(url, headers=_headers(user), verify=False)
    return _process_response(r, basket)


def create_payment_instrument(user, basket):
    url = _url("baskets/%s/payment_instruments" % basket.id)
    data = {
        'amount': 1.00,
        'payment_card': DEFAULT_CARD,
        'payment_method_id': PAYMENT_METHOD
    }
    r = requests.post(url, headers=_headers(user, basket.etag), data=json.dumps(data), verify=False)
    return _process_response(r, basket)


def delete_payment_instrument(user, basket, payment_id):
    url = _url("baskets/%s/payment_instruments/%s" % (basket.id, payment_id))
    r = requests.delete(url, headers=_headers(user, basket.etag))
    return _process_response(r, basket)


def set_billing_address(user, basket, **kwargs):
    url = _url("baskets/%s/billing_address" % basket.id)
    data = {
        'first_name': kwargs.get('first_name', ''),
        'last_name': kwargs.get('last_name', ''),
        'address1': kwargs.get('address1', ''),
        'city': kwargs['city'],
        'state_code': kwargs['state'],
        'country_code': kwargs['country'],
        'postal_code': kwargs['zip'],
    }
    r = requests.put(url, headers=_headers(user, basket.etag), data=json.dumps(data), verify=False)
    return _process_response(r, basket)


def submit_basket(user, basket):
    print ("Creating an order from basket...")
    url = _url("baskets/%s/submit" % basket.id)
    r = requests.post(url, headers=_headers(user, basket.etag), data='{}', verify=False)
    if r.ok:
        order = r.json()
        order["etag"] = r.headers.get("etag")
        return order
    else:
        print (r.text)
        r.raise_for_status()
        
def submit_order(user, basket):
    print ("Creating an order from basket...")
    url = _url("orders")
    data = {
        'basket_id': basket.id
    }
    r = requests.post(url, headers=_headers(user, basket.etag), data=json.dumps(data), verify=False)

    if r.ok:
        order = r.json()
        order["etag"] = r.headers.get("etag")
        return order
    else:
        print (r.text)
        r.raise_for_status()


def test_basket(guest=True):
    u = create_user(guest)
    bk = create_basket(u)

    basket_data = add_item_to_basket(u, bk, ITEM_ID, 1)
    item_data = basket_data["product_items"][0]
    basket_data = update_item(u, bk, item_data["item_id"], item_data["product_id"], 2)
    basket_data = set_customer_email(u, bk, USER_EMAIL)
    shipment = basket_data["shipments"][0]
    shipping_methods_result = get_shipping_methods(u, bk, shipment["shipment_id"])
    shipping_methods = shipping_methods_result["applicable_shipping_methods"]
    basket_data = set_shipping_method(u, bk, shipment["shipment_id"], shipping_methods[1]["id"])
    basket_data = set_shipping_address(
        u, bk, shipment["shipment_id"],
        first_name="Sarah",
        last_name="Conway",
        address1="5 Wall Street",
        city="Burlington",
        state="MA",
        country="US",
        zip="01703")
    basket_data = set_billing_address(
        u, bk,
        first_name="Sarah",
        last_name="Conway",
        address1="5 Main Street",
        city="Burlington",
        state="MA",
        country="US",
        zip="01703")
    payment_methods_result = get_payment_methods(u, bk)
    payment_methods = payment_methods_result["applicable_payment_methods"]
    basket_data = create_payment_instrument(u, bk)

    return (u, bk, basket_data)


def get_orders_for_user(user, status='new'):
    url = _url("orders")
    url = url + "&status=" + status
    r = requests.get(url, headers=_headers(user))
    return r


def get_order(user, order_id):
    url = _url("orders/%s" % order_id)
    r = requests.get(url, headers=_headers(user))
    if r.ok:
        order = r.json()
        order["etag"] = r.headers.get("etag")
        return order
    else:
        print (r.text)
        r.raise_for_status()


def set_order_payment_detail(user, order, paymentCard):
    payment_instrument = order["payment_instruments"][0]

    url = _url("orders/%s/payment_instruments/%s" % (order["order_no"], payment_instrument["uuid"]))
    data = {
        "amount": order["order_total"],
        "payment_card": paymentCard,
        "payment_method_id": PAYMENT_METHOD,
    }
    r = requests.patch(url, headers=_headers(user, order["etag"]), data=json.dumps(data))
    if r.ok:
        order = r.json()
        order["etag"] = r.headers.get("etag")
        return order
    else:
        print (r.text)
        r.raise_for_status()


def add_order_payment_detail(user, order, paymentCard):
    url = _url("orders/%s/payment_instruments" % order["order_no"])
    data = {
        "amount": order["order_total"],
        "payment_card": paymentCard,
        "payment_method_id": PAYMENT_METHOD,
    }
    r = requests.post(url, headers=_headers(user, order["etag"]), data=json.dumps(data), verify=False)
    if r.ok:
        order = r.json()
        order["etag"] = r.headers.get("etag")
        return order
    else:
        print (r.text)
        r.raise_for_status()


def pay_order(user, order):
    print ("Paying the order...")
    payment_instrument = order["payment_instruments"][0]

    url = _url("orders/%s/payment_authorize" % order["order_no"])
    data = {"payment_method_id": PAYMENT_METHOD}
    headers = _headers(user, order['etag'])
    headers['x-dw-order-token'] = order['order_token']

    r = requests.post(url, headers=headers, data=json.dumps(data), verify=False)
    if r.ok:
        order = r.json()
        order["etag"] = r.headers.get("etag")
        return order
    else:
        print (r.text)
        r.raise_for_status()


def test_order(guest=True):
    u, bk, basket_data = test_basket(guest)
    order = submit_order(u,bk)
    order = add_order_payment_detail(u, order, DEFAULT_CARD)
    return order

if __name__ == "__main__":
    test_order()