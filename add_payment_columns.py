from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    try:
        with db.engine.connect() as connection:
            result = connection.execute(text('PRAGMA table_info(reservations)'))
            columns = [row[1] for row in result]
            print('Current reservation columns:', columns)

            if 'payment_method' not in columns:
                connection.execute(text("ALTER TABLE reservations ADD COLUMN payment_method VARCHAR(20) DEFAULT 'cash'"))
                print('Added payment_method column')
            else:
                print('payment_method column already exists')

            if 'payment_status' not in columns:
                connection.execute(text("ALTER TABLE reservations ADD COLUMN payment_status VARCHAR(20) DEFAULT 'pending'"))
                print('Added payment_status column')
            else:
                print('payment_status column already exists')

            if 'payment_date' not in columns:
                connection.execute(text("ALTER TABLE reservations ADD COLUMN payment_date DATETIME"))
                print('Added payment_date column')
            else:
                print('payment_date column already exists')

            if 'transaction_id' not in columns:
                connection.execute(text("ALTER TABLE reservations ADD COLUMN transaction_id VARCHAR(50)"))
                print('Added transaction_id column')
            else:
                print('transaction_id column already exists')

            connection.commit()
            print('All payment columns processed successfully')

    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()