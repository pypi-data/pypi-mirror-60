class DynamicValue(object):
    def __init__(self, value_type):
        self.value_type = value_type

    def validate(self, value):
        return type(value) == self.value_type


class ResponseChecker:
    def __init__(self, control_sample, debug=False):
        '''
        :param control_sample: the dict which weill be used as a control sample for comparing with testing response.
         If the sample have a dynamic valus (tokes, ids, dates and etc), just replace it to DynamicValue(VALUE_TYPE).
         Examples is below.
        '''
        self.control_sample = control_sample
        self.debug = debug

    def validate(self, testing_response, list_keys=None):
        '''
        Comparing the dictionaries (the DynamicValue fields checks only types of values)

        :param testing_response: the dict with response of testing function/request
        :param list_keys: list of keys, which we must consistently pass to get to the compared fragment.
        If the key is string, function will try the .get() method, else if integer, its will be using as index
        for get from list
        For example, if we need check the first value (list) of key "customer" in dict below, the list_keys argument
        must be equals ['orders', 'customers', 0]:
        {
        'orders': { 'id': 1,
            'client_fullname': 'Name Lastname',
            'time_created': '12-08-2019'
            'customers': [{
                        'client_fullname': 'Name Lastname',
                        },
                        {
                        'client_fullname': 'Name Lastname',
                        }]
                    }
        }
        If argument is None, comparing starts from root keys.
        :return: Boolean value. True, if response is valid
        '''

        # With the help of list_keys we consistently select the section of data to be checked in current method call
        control_sample_fragment = self.control_sample
        testing_response_fragment = testing_response

        if list_keys is None:
            list_keys = []
        for i in list_keys:
            if isinstance(i, str):
                control_sample_fragment = control_sample_fragment.get(i)
                testing_response_fragment = testing_response_fragment.get(i)
            elif isinstance(i, int):
                control_sample_fragment = control_sample_fragment[i]
                testing_response_fragment = testing_response_fragment[i]
            else:
                raise AttributeError('Incorrect value in list_keys')

        # We will start the verification directly:
        # If completely identical, just return True.
        # If are lists, we sequentially compare each element, having previously numbered.
        # If the key value in the control dictionary is equal to DynamicValue (type), we check only the data types.
        # If are dictionaries, we check each key in sequence.
        # If none of the above work, the data is not valid.
        is_list = isinstance(testing_response_fragment, list)
        is_dict = isinstance(testing_response_fragment, dict)
        if control_sample_fragment == testing_response_fragment:
            pass
        elif is_dict and testing_response_fragment.keys() == control_sample_fragment.keys():
            for i in control_sample_fragment.keys():
                list_keys.append(i)
                if not self.validate(testing_response, list_keys):
                    self.printd('invalid', testing_response, list_keys)
                    return False
                del list_keys[-1]
        elif is_list and len(testing_response_fragment) == len(control_sample_fragment):
            for index, elem in enumerate(testing_response_fragment):
                list_keys.append(index)
                if not self.validate(testing_response, list_keys):
                    self.printd('invalid', testing_response, list_keys)
                    return False
                del list_keys[-1]
        elif control_sample_fragment.__class__ == DynamicValue:
            control_field_is_valid = control_sample_fragment.validate(testing_response_fragment)
            if not control_field_is_valid:
                self.printd('invalid type', control_sample_fragment.value_type, testing_response_fragment)
                return False
        else:
            self.printd('wrong values', control_sample_fragment, testing_response_fragment)
            return control_sample_fragment == testing_response_fragment
        return True

    def printd(self, *string):
        if self.debug:
            print(string)
