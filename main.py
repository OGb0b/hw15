from sys import audit

import psycopg2
from sqlalchemy.orm import PassiveFlag

try:
    conn = psycopg2.connect(
        user = 'postgres',
        password='0000',
        host='127.0.0.1',
        port='5432',
        database='postgres'
    )
except Exception as e:
    print('Ошибка подключения к базе данных')

cur = conn.cursor()
def add_book(title, author, quantity, published_year=None):#добавь проверку автора и загловка
    try:
        cur.execute(
            """
            INSERT INTO books (title, author,published_year,quantity)
            VALUES (%s,%s,%s,%s)
            """,
            (title, author,published_year,quantity, )
        )
        conn.commit()
        print(f"Книга '{title}' успешно добавлена.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении книги: {e}")

def add_reader(name, email): #добавь проверку email
    try:
        cur.execute(
            """
            INSERT INTO readers (name, email)
            VALUES (%s, %s)
            """,
            (name,email,)
        )
        conn.commit()
        print('Читатель добавлен')
    except Exception as e:
        conn.rollback()
        print(f'Ошибка при добавлени пользователя: {e}')

def borrow_book(reader_id, book_id):
    try:
        cur.execute(
            """
            SELECT quantity FROM books WHERE id = %s FOR UPDATE
            """
        )
        result = cur.fetchone()
        if not result:
            print(f"Книги с id - {book_id} в библиотеке нет")
            return

        quantity = result[0]
        if quantity == 0:
            print(f'В библиотеке не осталось книг с id - {book_id}')
            return

        cur.execute(
            """
            UPDATE books SET quantity = quantity - 1 WHERE id = %s
            """,
            (book_id,)
        )
        conn.commit()
        cur.execute(
            """
            INSERT INTO borrowedbooks (book_id,reader_id, borrow_date) 
            VALUES (%s, %s, CURRENT_TIMESTAMP)
            """,
            (book_id, reader_id, )
        )
        conn.commit()
        print('Книга успешно выдана')
    except Exception as e:
        print(f'Произошла ошибка при выдаче книги: {e}')

def return_book(reader_id, book_id):
    try:
        cur.execute(
            """
            SELECT 1 FROM borrowedbooks 
            WHERE book_id = %s AND reader_id = %s AND return_date IS NULL
            FOR UPDATE
            """,
            (book_id, reader_id)
        )
        if not cur.fetchone():
            print("Эта книга не числится выданной данному читателю или уже возвращена")
            return
        cur.execute(
            """
            UPDATE books SET quantity = quantity + 1 WHERE id = %s
            """,
            (book_id,)
        )
        conn.commit()
        cur.execute(
            """
            UPDATE borrowedbooks SET return_date=CURRENT_TIMESTAMP WHERE book_id = %s AND reader_id = %s
            AND return_date IS NULL
            """,
            (book_id, reader_id,)
        )
        conn.commit()
        print('Книга успешно возвращена')
    except Exception as e:
        print(f'Произошла ошибка при возврате книги: {e}')

def books_request():
    try:
        cur.execute(
            """
            SELECT title, author, published_year ORDER BY published_year
            """
        )
        result = cur.fetchall()
        for row in result:
            print(f'Книга - {row[0]}, Автор - {row[1]}, Дата издания - {row[2]}')
    except Exception as e:
        print(f'Произошла ошибка при запросе всех книг:{e}')




#if __name__ == '__main__':
