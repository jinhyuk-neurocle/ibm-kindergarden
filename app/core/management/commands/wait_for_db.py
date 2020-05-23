import time
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    """Django command에 DB 체크 함수 추가"""
    
    def handle(self, *args, **options):
        self.stdout.write('Waiting for database...')
        db_conn = None
        success = False
        trycnt = 0 
        while not success and trycnt<6:
            try:
                db_conn = connections['default']
                c = db_conn.cursor()
                c.execute('select * from pg_tables')
                c.fetchall()
                success = True
                
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 0.5 second...')
                time.sleep(0.5)
            trycnt+=1

        if success:
           self.stdout.write(self.style.SUCCESS('Database available!'))
        else:
           self.stdout.write(self.style.ERROR('Database connection fail'))