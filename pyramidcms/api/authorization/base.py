class Authorization(object):
    """
    Basic authorization class that always allows everything.
    """

    def read_list(self, obj_list, bundle):
        return obj_list

    def read_detail(self, obj, bundle):
        return True

    def create_list(self, obj_list, bundle):
        return obj_list

    def create_detail(self, obj, bundle):
        return True

    def update_list(self, obj_list, bundle):
        return obj_list

    def update_detail(self, obj, bundle):
        return True

    def delete_list(self, obj_list, bundle):
        return obj_list

    def delete_detail(self, obj, bundle):
        return True
