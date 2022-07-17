from pprint import pprint

import psycopg2


class ClientDB:
    def __init__(self):
        self.conn = psycopg2.connect(database='ClientDB_hometask', user='postgres', password='postgres')

    def open_connect(self):
        return self.conn

    def close_connect(self):
        return self.conn.close()

    def create_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(''' CREATE TABLE if not exists client(
                            id SERIAL PRIMARY KEY,
                            first_name VARCHAR(20) NOT NULL,
                            last_name VARCHAR(20) NOT NULL,
                            email VARCHAR(20) UNIQUE NOT NULL);
                        ''')

            cur.execute(''' CREATE TABLE if not exists phone(
                            id SERIAL PRIMARY KEY,
                            phone_number VARCHAR(40),
                            client_id INTEGER NOT NULL references client(id));
                        ''')
            self.conn.commit()

    def drop_tables(self):
        with self.conn.cursor() as cur:
            cur.execute(''' DROP TABLE  phone;
                            DROP TABLE  client;
                        ''')
            self.conn.commit()

    def add_client(self, first_name, last_name, mail, *args):
        with self.conn.cursor() as cur:
            cur.execute('''INSERT INTO client(first_name, last_name, email)
                        VALUES (%s, %s, %s) RETURNING id;
                        ''', (first_name, last_name, mail)
                        )
            self.conn.commit()
            client_id = cur.fetchone()

            for num in args:
                cur.execute('''INSERT INTO phone(phone_number, client_id)
                            VALUES (%s, %s);
                            ''', (num, client_id)
                            )
            self.conn.commit()

    def add_phone_to_client(self, client_id, phone):
        with self.conn.cursor() as cur:
            cur.execute('''INSERT INTO phone(phone_number, client_id)
                            VALUES (%s, %s);
                        ''', (phone, client_id)
                        )
            self.conn.commit()

    def change_client(self, client_id, first_name, last_name, email, old_phone=None, new_phone=None):
        with self.conn.cursor() as cur:
            cur.execute('''UPDATE client
                            SET first_name = %s
                            WHERE id = %s;
                        ''', (first_name, client_id)
                        )
            self.conn.commit()

        with self.conn.cursor() as cur:
            cur.execute('''UPDATE client
                            SET last_name = %s
                            WHERE id = %s;
                        ''', (last_name, client_id)
                        )
            self.conn.commit()

        with self.conn.cursor() as cur:
            cur.execute('''UPDATE client
                            SET email = %s
                            WHERE id = %s;
                            ''', (email, client_id)
                        )
            self.conn.commit()

        if not old_phone:
            with self.conn.cursor() as cur:
                cur.execute('''INSERT INTO phone(phone_number, client_id)
                               VALUES (%s, %s);
                            ''', (new_phone, client_id)
                            )
                self.conn.commit()

        elif old_phone:
            with self.conn.cursor() as cur:
                cur.execute('''UPDATE phone
                               SET phone_number = %s
                               WHERE phone_number = %s;
                            ''', (new_phone, old_phone)
                            )
                self.conn.commit()

    def del_phone(self, phone_to_del):
        with self.conn.cursor() as cur:
            cur.execute('''DELETE FROM phone
                           WHERE phone_number = %s;
                        ''', (phone_to_del,)
                        )
            self.conn.commit()

    def del_client(self, client_id):
        with self.conn.cursor() as cur:
            cur.execute('''DELETE FROM phone
                           WHERE client_id = %s;
                           ''', (client_id,)
                        )
            self.conn.commit()

        with self.conn.cursor() as cur:
            cur.execute('''DELETE FROM client
                           WHERE id = %s;
                           ''', (client_id,)
                        )
            self.conn.commit()

    def find_client(self, client_id=None, first_name=None, last_name=None, email=None, phone=None):

        if client_id:
            with self.conn.cursor() as cur:
                cur.execute('''select c.id, c.first_name, c.last_name, c.email, p.phone_number from client c
                               left join phone p on c.id = p.client_id
                               where c.id = %s
                               group by c.id, c.first_name, c.last_name, c.email, p.phone_number;
                               ''', (client_id,)
                            )

                res = cur.fetchall()
                print(f'Клиент с индексом: {client_id}:')
                if res:
                    res_to_print = [*res[0][:-1]]
                    res_to_print.append([res[ind][-1] for ind in range(len(res))])
                    print(*res_to_print)
                else:
                    print('Такого клиента не существует.')
                print()


        if first_name:
            with self.conn.cursor() as cur:
                cur.execute(''' select c.id, c.first_name, c.last_name, c.email, p.phone_number from client c
                                left join phone p on c.id = p.client_id
                                where c.first_name = %s
                                group by c.id, c.first_name, c.last_name, c.email, p.phone_number;
                            ''', (first_name,)
                            )
                res = cur.fetchall()
                dict_res = {res[ind][0:-1]: [res[index][-1] for index in range(len(res)) if res[ind][0] == res[index][0]] for ind in range(len(res))}
                print(f'Клиенты с именем: {first_name}:')
                for key_ in dict_res:
                    print(*key_, [*dict_res[key_]])


                print()


        if last_name:
            with self.conn.cursor() as cur:
                cur.execute(''' select c.id, c.first_name, c.last_name, c.email, p.phone_number from client c
                                left join phone p on c.id = p.client_id
                                where c.last_name = %s
                                group by c.id, c.first_name, c.last_name, c.email, p.phone_number;
                            ''', (last_name,)
                            )
                res = cur.fetchall()
                dict_res = {res[ind][0:-1]: [res[index][-1] for index in range(len(res)) if res[ind][0] == res[index][0]] for ind in range(len(res))}
                print(f'Клиенты с фамилией: {last_name}:')
                for key_ in dict_res:
                    print(*key_, [*dict_res[key_]])
                print()

        if email:
            with self.conn.cursor() as cur:
                cur.execute(''' select c.id, c.first_name, c.last_name, c.email, p.phone_number from client c
                                left join phone p on c.id = p.client_id
                                where c.email = %s
                                group by c.id, c.first_name, c.last_name, c.email, p.phone_number;
                            ''', (email,)
                            )
                res = cur.fetchall()
                dict_res = {res[ind][0:-1]: [res[index][-1] for index in range(len(res)) if res[ind][0] == res[index][0]] for ind in range(len(res))}
                print(f'Клиент с e-mail: {email}:')
                for key_ in dict_res:
                    print(*key_, [*dict_res[key_]])
                print()

        if phone:
            with self.conn.cursor() as cur:
                cur.execute(''' select c.id, c.first_name, c.last_name, c.email, p.phone_number from phone p
                                join client c on c.id = p.client_id
                                where c.id = (select client_id from phone where phone_number = %s) 
                                group by c.id, c.first_name, c.last_name, c.email, p.phone_number;
                            ''', (phone,)
                            )
                res = cur.fetchall()
                dict_res = {res[ind][0:-1]: [res[index][-1] for index in range(len(res)) if res[ind][0] == res[index][0]] for ind in range(len(res))}
                print(f'Клиент с номером телефона: {phone}:')
                for key_ in dict_res:
                    print(*key_, [*dict_res[key_]])
                print()

    def print_all(self, *args):
        ''' Печатаем всех в разрезе количество на странице
        1 аргумент: \t количество уникальных клиентов на первой странице
        2 аргумент: \t шаг (перебор по страницам)
        Пример: \tнапечатать клиентов 3 и 4: print_all(2, 2)
        Пример: \tнапечатать всех клиентов: print_all()
        '''
        with self.conn.cursor() as cur:
            if args:
                cur.execute('''select c.id, c.first_name, c.last_name, c.email, p.phone_number from client c
                                full join phone p on c.id = p.client_id
                                where c.id between %s and %s
                                group by c.id, c.first_name, c.last_name, c.email, p.phone_number
                                order by id
                                ;''',(args[0], args[1])
                            )
            else:
                cur.execute('''select c.id, c.first_name, c.last_name, c.email, p.phone_number from client c
                                full join phone p on c.id = p.client_id
                                group by c.id, c.first_name, c.last_name, c.email, p.phone_number
                                order by id;
                            ''')


            res = cur.fetchall()
            dict_res = {res[ind][0:-1]: [res[index][-1] for index in range(len(res)) if res[ind][0] == res[index][0]]
                        for ind in range(len(res))}
            print(f'Клиенты: с {args[0]} по {args[1]}' if args else 'Все клиенты:')
            for key_ in dict_res:
                print(*key_, [*dict_res[key_]])
            print()


request_db = ClientDB()

request_db.open_connect()

request_db.drop_tables()
request_db.create_tables()

request_db.add_client('Иван', 'Иванов', 'Ivan@mail.ru', )
request_db.add_client('Петр', 'Петров', 'Petr@mail.ru', '+70000000021', '+70000000022')
request_db.add_client('Петр', 'Иванов', 'IPetr@mail.ru', '+70000000033')

request_db.add_phone_to_client(2, '+70000000023')
request_db.add_phone_to_client(1, '+70000000001')
request_db.add_phone_to_client(1, '+70000000002')
request_db.add_phone_to_client(1, '+70000000003')

request_db.add_client('Антон', 'Антонов', 'Anton@mail.ru', )

request_db.change_client(3, 'Сергей', 'Сергеев', 'Sergo@mail.ru', new_phone='+70000000331')
request_db.change_client(3, 'Роман', 'Иванов', 'Sergo@mail.ru', '+70000000221', '+70000000222')

request_db.del_phone('+70000000012')

request_db.del_client(4)

request_db.add_client('Иван', 'Антонов', 'IAntonov@mail.ru', )

request_db.add_phone_to_client(5, '+70000000053')

request_db.find_client(client_id=3)
request_db.find_client(client_id=6)
request_db.find_client(first_name='Иван')
request_db.find_client(first_name='Кукиш')
request_db.find_client(last_name='Иванов')
request_db.find_client(email='Petr@mail.ru')
request_db.find_client(phone='+70000000022')

request_db.add_client('Иван', 'Кук', 'IvanK@mail.ru', '+800000')
request_db.add_client('Иван', 'Пук', 'IvanP@mail.ru', )
request_db.add_client('Иван', 'Нук', 'IvanN@mail.ru', )
request_db.add_client('Иван', 'Тук', 'IvanT@mail.ru', )

print(request_db.print_all.__doc__)
request_db.print_all()
request_db.print_all(5,8)

request_db.close_connect()

