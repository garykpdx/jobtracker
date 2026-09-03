from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        UPDATE jobapps_jobapp
        SET applied_dt = applied_dt || ' 00:00:00'
        WHERE length(applied_dt) = 10
    """)
    print(f"Fixed {cursor.rowcount} JobApp rows")

    cursor.execute("""
        UPDATE jobapps_jobcomment
        SET change_dt = change_dt || ' 00:00:00'
        WHERE length(change_dt) = 10
    """)
    print(f"Fixed {cursor.rowcount} JobComment rows")
