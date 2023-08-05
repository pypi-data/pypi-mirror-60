from .response_checker import DynamicValue
from decimal import Decimal
from datetime import timedelta

test_info_scheme = {'last_login': DynamicValue(str), 'username': 'courier_innova@innova.ru',
                    'first_name': 'Courier', 'last_name': 'Lastname', 'email': 'courier_innova@innova.ru',
                    'date_joined': DynamicValue(str), 'phone': '+1(222)222-22-22',
                    'photo': '', 'photo_min': '', 'photo_middle': '', 'image1': '', 'image1_min': '',
                    'image1_middle': '', 'image2': '', 'image2_min': '', 'image2_middle': '',
                    'image3': '', 'image3_min': '', 'image3_middle': '', 'vehicle': None, 'ssn': None,
                    'status': 'not_available', 'latitude': Decimal('0E-7'), 'longitude': Decimal('0E-7'),
                    'is_activated': True, 'last_push': None, 'update_time': None
}

