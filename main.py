from sys import audit

import psycopg2
from sqlalchemy.orm import PassiveFlag
from sqlalchemy.util.langhelpers import inject_param_text

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
def add_book(title, author, quantity, published_year=None):
    try:
        cur.execute(
            """
            SELECT title, author FROM books
            """
        )
        books = cur.fetchall()

        for book in books :
            if book[0].lower() == title.lower() and book[1].lower() == author.lower():
                print('Данная книга уже есть в библиотеке')
                return

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

def add_reader(name, input_email):
    try:
        cur.execute(
            """
            SELECT email from readers
            """
        )
        emails = cur.fetchall()
        for email in emails:
            if email[0] == input_email:
                print('Пользователь с таким email уже зарегистрирован')
                return
        cur.execute(
            """
            INSERT INTO readers (name, email)
            VALUES (%s, %s)
            """,
            (name, input_email,)
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
            SELECT id FROM readers WHERE id = %s
            """,
            (reader_id, )
        )
        result = cur.fetchone()
        if not result:
            print('Читателя с таким id не существует')
            return
        cur.execute(
            """
            SELECT quantity FROM books WHERE id = %s FOR UPDATE
            """,
            (book_id,)
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
            SELECT title, author, published_year, id FROM books ORDER BY published_year
            """
        )
        result = cur.fetchall()
        for row in result:
            print(f'Книга - {row[0]}, Автор - {row[1]}, Дата издания - {row[2]}, id - {row[3]}')
    except Exception as e:
        print(f'Произошла ошибка при запросе всех книг:{e}')
reader_id=[]
def readers_request():
    try:
        cur.execute(
            """
            SELECT reader_id from borrowedbooks
            """
        )
        readers = cur.fetchall()
        reader_id = []
        for reader in readers:
            if reader[0] not in reader_id:
                reader_id.append(reader[0])
                cur.execute(
                    """
                    SELECT name, email, id from readers WHERE id = %s
                    """,
                    (reader[0],)
                )
                user = cur.fetchall()
                print(f'Имя - {user[0][0]}, email - {user[0][1]}, id - {user[0][2]}')
    except Exception as e:
        print(f'Произошла ошибка: {e}')

def borrowed_books_request():
    try:
        cur.execute(
            """
            SELECT book_id from borrowedbooks WHERE return_date is NULL
            """
        )
        books = cur.fetchall()
        if not books:
            print('Все книги вернули')
            return
        book_id = set()
        for book in books:
            if book[0] not in book_id:
                book_id.add(book[0])
                cur.execute(
                    """
                    SELECT title, author, id FROM books WHERE id = %s
                    """,
                    (book[0],)
                )
                print_book = cur.fetchall()
                print(f'{print_book[0][0]} - {print_book[0][1]}, id - {print_book[0][2]}')
    except Exception as e:
        print(f'Произошла ошибка: {e}')

def find_by_author(author):
    cur.execute(
        """
        SELECT title, author from books WHERE author = %s
        """,
        (author,)
    )
    result = cur.fetchall()
    if not result:
        print('Книг данного автора не найдено')
    else:
        for auth in result:
            print(f'{auth[0]} - {auth[1]}')

def find_by_title(title):
    cur.execute(
        """
        SELECT title, author from books WHERE title = %s
        """,
        (title,)
    )
    result = cur.fetchall()
    if not result:
        print('Книг не найдено')
    else:
        for tit in result:
            print(f'{tit[0]} - {tit[1]}')


def delete_readers(reader_id):
    try:
        cur.execute(
        """
        SELECT reader_id FROM borrowedbooks WHERE reader_id = %s AND return_date IS NOT NULL
        """,
        (reader_id,)
        )
        result = cur.fetchone()
        if not result:
            print('Пользователя с таким id не существует или у него есть задолженности')
            return
        cur.execute(
            """
            DELETE FROM borrowedbooks WHERE reader_id = %s
            """,
            (reader_id,)
        )
        cur.execute(
            """
            DELETE FROM readers WHERE id = %s
            """,
            (reader_id,)
        )
        conn.commit()
        print('Пользователь удален')
    except Exception as e:
        print(f'Произошла ошибка: {e}')

def delete_books(book_id):
    try:
        cur.execute(
            """
            SELECT id FROM books WHERE id = %s AND quantity IS NOT NULL
            """,
            (book_id,)
        )
        result = cur.fetchone()
        if not result:
            print('Данной книги нет в библиотеке на данный момент')
            return
        cur.execute(
            """
            DELETE FROM borrowedbooks WHERE book_id = %s
            """,
            (book_id, )
        )
        cur.execute(
            """
            DELETE FROM books WHERE id = %s
            """,
            (book_id, )
        )
        conn.commit()
        print('Книга успешно удалена')
    except Exception as e:
        print(f'Произошла ошибка: {e}')

def main():
    while True:
        print('\n1. Добавить книгу')
        print('2. Добавить читателя')
        print('3. Взять книгу')
        print('4. Вернуть книгу')
        print('5. Посмотреть все книги в библиотеке')
        print('6. Посмотреть читателей, которые хоть раз брали книгу')
        print('7. Посмотреть книги, которые не еще не вернули')
        print('8. Найти книгу по автору')
        print('9. Найти книгу по названию')
        print('10. Удалить читателя')
        print('11. Удалить книгу')
        print('12. Выйти')
        choice = input('Выберите действие: ')
        if choice == '1':
            title = input('Введите название книги: ')
            author = input('Укажите автора книги: ')
            quantity = input('Введите количество книг: ')
            published_year = input('Введите год издания (необязательно): ')
            if len(published_year) != 0:
                add_book(title, author, quantity, published_year)
            else:
                add_book(title, author, quantity)
        elif choice == '2':
            name = input('Введите имя читателя: ')
            email = input('Введите email читателя: ')
            add_reader(name, email)
        elif choice == '3':
            reader_id = input('Введите id читателя: ')
            book_id = input('Введите id книги: ')
            borrow_book(reader_id, book_id)
        elif choice == '4':
            reader_id = input('Введите id читателя: ')
            book_id = input('Введите id книги: ')
            return_book(reader_id, book_id)
        elif choice == '5':
            books_request()
        elif choice == '6':
            readers_request()
        elif choice == '7':
            borrowed_books_request()
        elif choice == '8':
            find_by_author(input('Введите имя автора: '))
        elif choice == '9':
            find_by_title(input('Введите название книги: '))
        elif choice == '10':
            delete_readers(input('Введите id читателя: '))
        elif choice == '11':
            delete_books(input('Введите id книги: '))
        elif choice == '12':
            break
        else:
            print('Неверный ввод, попробуйте еще раз')


if __name__ == '__main__':
    main()