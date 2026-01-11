from rest_framework.permissions import BasePermission


class BaseRolePermission(BasePermission):
    required_group = ''

    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            return False
        return request.user.groups.filter(name=self.required_group).exists()


class IsSystemAdministrator(BaseRolePermission):
    required_group = 'SysAdmin'


class IsRestaurantManager(BaseRolePermission):
    required_group = 'Manager'


class IsDeliveryStaff(BaseRolePermission):
    required_group = 'Delivery Crew'


class IsRegularCustomer(BaseRolePermission):
    required_group = 'Customer'


class IsCustomerOrDeliveryStaff(BasePermission):
    def has_permission(self, request, view):
        if not bool(request.user and request.user.is_authenticated):
            return False
        user_groups = request.user.groups.values_list('name', flat=True)
        return 'Customer' in user_groups or 'Delivery Crew' in user_groups