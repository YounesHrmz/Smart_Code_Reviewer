from app.database.connection import DBConnection

class BaseRepository:
    """
    مستودع أساسي فارغ يوفر ممر اتصالات موحد لجميع المستودعات المتفرعة
    """
    def __init__(self):
        pass