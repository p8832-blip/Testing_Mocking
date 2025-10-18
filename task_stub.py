class UserService:
    def __init__(self, db):
        self.db = db

    def get_user_name(self, user_id):
        user = self.db.find_by_id(user_id)
        return user['name'] if user else None

# الاختبار
def test_get_user_name_with_stub():
    class DBStub:
        def find_by_id(self, id):
            return {'id': id, 'name': 'Alice'}  # نتيجة ثابتة
    service = UserService(DBStub())
    assert service.get_user_name(1) == 'Alice'
