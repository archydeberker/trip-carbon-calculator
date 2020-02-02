from flask import jsonify


class InvalidFile(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['title'] = 'Invalid file upload'
        rv['message'] = '''
        It looks like you have uploaded a file which is not a valid Excel file. If you're into computers,
        see the error raised below!
        '''

        rv['details'] = self.message
        return rv


class UnknownError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['title'] = 'Something went wrong'
        rv['message'] = '''
        Something went wrong here, and we are not sure what. You can find the details of the
        error below if you're into that sort of thing.
        '''

        rv['details'] = self.message
        return rv


class InvalidAddressError(Exception):
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['title'] = 'Something went wrong'
        rv['message'] = '''
        One or more of the addresses in your excel file was not findable using Google Maps.
        Please verify that all of the addresses you submitted can be found by 
        typing them in a Google Maps search box!
        '''

        rv['details'] = self.message
        return rv
