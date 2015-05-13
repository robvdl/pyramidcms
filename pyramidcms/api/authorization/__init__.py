class BaseAuthorization(object):

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
