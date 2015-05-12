class BaseAuthorization(object):

    def update_resource(self, resource):
        print(resource)
        self.resource = resource

    def read_list(self, obj_list):
        return True

    def read_detail(self, obj):
        return True

    def create_list(self, obj_list):
        return True

    def create_detail(self, obj):
        return True

    def update_list(self, obj_list):
        return True

    def update_detail(self, obj):
        return True

    def delete_list(self, obj_list):
        return True

    def delete_detail(self, obj):
        return True
