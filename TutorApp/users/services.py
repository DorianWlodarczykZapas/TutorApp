class UserService:
    def __init__(self, user):
        self.user = user

    def is_teacher(self):
        return self.user.is_authenticated and self.user.role_type == 2

    def is_student(self):
        return self.user.is_authenticated and self.user.role_type == 1

    def is_admin(self):
        return self.user.is_authenticated and self.user.role_type == 3
