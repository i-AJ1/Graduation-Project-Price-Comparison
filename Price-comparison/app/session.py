# session.py - Shared session state across pages

class Session:
    def __init__(self):
        self.user_id = None
        self.username = None
        self.is_admin = False

    def login(self, user):
        self.user_id = user['id']
        self.username = user['username']
        self.is_admin = bool(user.get('is_admin', False))

    def logout(self):
        self.user_id = None
        self.username = None
        self.is_admin = False

    def is_logged_in(self):
        return self.user_id is not None

# Global session instance
session = Session()