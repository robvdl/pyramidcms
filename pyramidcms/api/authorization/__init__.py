from pyramid.httpexceptions import HTTPForbidden


class Authorization(object):
    """
    Basic authorization class that always allows everything.
    """

    def read_list(self, obj_list):
        return obj_list

    def read_detail(self, obj):
        return True

    def create_list(self, obj_list):
        return obj_list

    def create_detail(self, obj):
        return True

    def update_list(self, obj_list):
        return obj_list

    def update_detail(self, obj):
        return True

    def delete_list(self, obj_list):
        return obj_list

    def delete_detail(self, obj):
        return True


class ReadOnlyAuthorization(Authorization):
    """
    Basic authorization class that only allows read and read_list.

    This is the default authorization class.
    """

    def create_list(self, obj_list):
        raise HTTPForbidden()

    def create_detail(self, obj):
        raise HTTPForbidden()

    def update_list(self, obj_list):
        raise HTTPForbidden()

    def update_detail(self, obj):
        raise HTTPForbidden()

    def delete_list(self, obj_list):
        raise HTTPForbidden()

    def delete_detail(self, obj):
        raise HTTPForbidden()
