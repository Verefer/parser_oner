import datetime

import mysql.connector.cursor
from mysql.connector import connect, Error


class DataBase:
    def __init__(self, HOST, USER, PASSWORD):
        self.HOST: str = HOST
        self.USER: str = USER
        self.PASSWORD: str = PASSWORD

        self._uploadIdFromDB()

    def _uploadIdFromDB(self):  # обновляет список айди
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    all_data_in_db = f"""SELECT `id` from balances"""
                    cursor.execute(all_data_in_db)
                    records = cursor.fetchall()
                    self.ALL_IDs_FROM_DB = [i[0] for i in records]
        except Error as error:
            print("Ошибка при работе с MYSQL", error)

    def _get_connect(self):
        return connect(
            host=self.HOST,
            user=self.USER,
            password=self.PASSWORD,
            database='ParserOlxDB'
        )

    def add_user(self, ID):  # добавление пользователя в бд
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    sqlite_insert_with_param = f"""INSERT INTO usersOlxUa (ID) VALUES (%s)"""

                    cursor.execute(sqlite_insert_with_param, (ID,))
                    conn.commit()
                    self.ALL_IDs_FROM_DB.append(int(ID))
                    print(f'Добавлен пользователь {ID}')
                    sqlite_insert_with_param = f"""INSERT INTO balances (ID) VALUES (%s)"""

                    cursor.execute(sqlite_insert_with_param, (ID,))
                    conn.commit()


        except Exception as ex:
            print(ex)

    def get_user(self, id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    sqlite_insert_with_param = """SELECT * FROM usersOlxUa WHERE ID = %s"""
                    cursor.execute(sqlite_insert_with_param, (id,))
                    records = cursor.fetchone()
                    return records
        except Exception as ex:
            print(ex)

    def get_balance_user(self, user_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    sqlite_insert_with_param = f"""SELECT * FROM balances WHERE ID = %s"""
                    cursor.execute(sqlite_insert_with_param, (user_id,))
                    records = cursor.fetchone()
                    return records
        except Exception as ex:
            print(ex)

    def add_token(self, user_id, token):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """INSERT INTO tokensOlxUa (ID, token) VALUES (%s, %s)"""
                    cursor.execute(query, (user_id, token))
                    conn.commit()
                    return 1
        except Exception as ex:
            print(ex)
            return 0

    def get_token(self, user_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    sqlite_insert_with_param = f"""SELECT * FROM tokensOlxUa WHERE ID = %s LIMIT 1"""
                    cursor.execute(sqlite_insert_with_param, (user_id,))
                    records = cursor.fetchone()
                    return records
        except Exception as ex:
            print(ex)

    def delete_token(self, token_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """DELETE FROM tokensOlxUa WHERE TokenId = %s"""
                    cursor.execute(query, (token_id,))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def set_filter_price(self, user_id, price):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE usersOlxUa SET announce_price = %s WHERE ID = %s"""
                    cursor.execute(query, (price, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def set_filter_success_deliveries(self, user_id, success_delivery):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE usersOlxUa SET filter_successful_deliveries = %s WHERE ID = %s"""
                    cursor.execute(query, (success_delivery, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def set_filter_amount_days(self, user_id, amount_days):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE usersOlxUa SET registration_announce = %s WHERE ID = %s"""
                    cursor.execute(query, (amount_days, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def set_filter_interval_create(self, user_id, interval_create):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE usersOlxUa SET interval_create_announce = %s WHERE ID = %s"""
                    cursor.execute(query, (interval_create, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def set_filter_auto_text_wa(self, user_id, auto_text):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE usersOlxUa SET auto_text_wa = %s WHERE ID = %s"""
                    cursor.execute(query, (auto_text, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def update_user_balance(self, user_id, summa):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE balances SET balance = balance + %s WHERE ID = %s"""
                    cursor.execute(query, (summa, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def set_new_time_for_subscription(self, user_id, time_subscription):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE usersOlxUa SET subscription_to = %s WHERE ID = %s"""
                    cursor.execute(query, (time_subscription, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def set_status_parsing(self, user_id, status):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE usersOlxUa SET status_parsing = %s WHERE ID = %s"""
                    cursor.execute(query, (status, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def add_proxies_olx_ua(self, proxies):
        with self._get_connect() as conn:
            with conn.cursor() as cursor:
                query = """INSERT INTO proxyOlxUa (proxy) VALUES (%s)"""
                for proxy in proxies:
                    try:
                        cursor.execute(query, (proxy,))
                    except Exception as ex:
                        print(ex)
                conn.commit()

    def get_all_users(self):
        with self._get_connect() as conn:
            with conn.cursor() as cursor:
                query = """SELECT * FROM usersolxua"""
                cursor.execute(query)
                return cursor.fetchall()

    def get_proxy(self):
        try:
            with self._get_connect() as conn:
                with conn.cursor(buffered=True) as cursor:
                    query = "SELECT * FROM proxyOlxUa WHERE proxy = ''"
                    cursor.execute(query)
                    proxy = cursor.fetchone()
                    if not proxy:
                        query = """SELECT * FROM proxyOlxUa ORDER BY id LIMIT 1"""
                        cursor.execute(query)
                        return cursor.fetchone()
                    return proxy
        except Exception as ex:
            print(ex)

    def delete_proxy(self, proxy_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """DELETE FROM proxyOlxUa WHERE id = %s"""
                    cursor.execute(query, (proxy_id,))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def set_referer_id(self, user_id, referer_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE usersOlxUa SET referer_id = %s WHERE ID = %s"""
                    cursor.execute(query, (referer_id, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def get_amount_refers(self, referer_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """SELECT * FROM usersOlxUa WHERE referer_id = %s"""
                    cursor.execute(query, (referer_id,))
                    return len(cursor.fetchall())
        except Exception as ex:
            print(ex)

    def create_promo(self, promo, percent):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """INSERT INTO promoCodes (promo, discount) VALUES (%s, %s)"""
                    cursor.execute(query, (promo, percent))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def get_all_promo_codes(self):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """SELECT * FROM promoCodes"""
                    cursor.execute(query)
                    return cursor.fetchall()
        except Exception as ex:
            print(ex)

    def set_promo_code_and_discount(self, user_id, promo, discount):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE balances SET promo = %s, discount = %s WHERE ID = %s"""
                    cursor.execute(query, (promo, discount, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def add_user_to_last_parse_consignment(self, user_id, filename):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """INSERT INTO lastParseConsignmentOlxUa (ID, filename) VALUES (%s, %s)"""
                    cursor.execute(query, (user_id, filename))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def set_new_filename_in_last_parse(self, user_id, filename):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE lastParseConsignmentOlxUa SET filename = %s WHERE ID = %s"""
                    cursor.execute(query, (filename, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def get_filename_from_last_parse(self, user_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """SELECT * FROM lastParseConsignmentOlxUa WHERE ID = %s"""
                    cursor.execute(query, (user_id,))
                    return cursor.fetchone()
        except Exception as ex:
            print(ex)

    def set_new_parse_category(self, user_id, category):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE usersOlxUa SET parse_category = %s WHERE ID = %s"""
                    cursor.execute(query, (category, user_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def delete_promo_and_discounts(self, promo):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """DELETE FROM promoCodes WHERE promo = %s"""
                    cursor.execute(query, (promo,))
                    query = """UPDATE balances SET promo = '', discount = 0 WHERE promo = %s"""
                    cursor.execute(query, (promo,))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def add_announce(self, title, price_value, price_currency, description, city, region, date_create_announce,
                     date_create_account, photo_url, page_id, amount_delivery, contact_name, category, url):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """INSERT INTO announcementsOlxUa (title, price_value, price_currency, description, city, region, date_create_announce, date_create_account, photo_url, page_id, amount_delivery, contact_name, category, url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    cursor.execute(query, (
                        title, price_value, price_currency, description, city, region, date_create_announce,
                        date_create_account, photo_url, page_id,
                        amount_delivery, contact_name, category, url))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def add_proxy_to_timeout(self, proxy, proxy_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """INSERT INTO timeoutProxiesOlxUa (proxy) VALUES (%s)"""
                    cursor.execute(query, (proxy,))
                    conn.commit()
                    self.delete_proxy(proxy_id)
        except Exception as ex:
            print(ex)

    def selection_of_announces(self, price_min: int, price_max: int, registration_seller: datetime.datetime,
                               successful_deliveries: int, create_announce: datetime.datetime, categories: list):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """SELECT * FROM announcementsolxua WHERE price_value >= %s AND price_value <= %s AND 
                    date_create_account >= %s AND amount_delivery <= %s AND date_create_announce >= %s AND category IN (%s) 
                    ORDER BY date_create_announce DESC LIMIT 100 """
                    cursor.execute(query, (
                        price_min, price_max, registration_seller, successful_deliveries, create_announce,
                        ','.join(map(str, categories))))
                    data = cursor.fetchall()
                    return data
        except Exception as ex:
            print(ex)

    def delete_olds_announces(self, max_create_announce_interval: int):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    max_create_announce = datetime.datetime.now() - datetime.timedelta(
                        minutes=max_create_announce_interval)
                    print(max_create_announce)
                    query = """DELETE FROM announcementsolxua WHERE %s > date_create_announce"""
                    cursor.execute(query, (max_create_announce,))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def revive_proxies(self, interval):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    max_added_proxy = datetime.datetime.now() - datetime.timedelta(minutes=interval)
                    query = """SELECT * FROM timeoutProxiesOlxUa WHERE %s > start_timeout"""
                    cursor.execute(query, (max_added_proxy,))
                    rows = cursor.fetchall()
                    if rows:
                        for row in rows:
                            query = """INSERT INTO proxyOlxUa (proxy) VALUES (%s)"""
                            cursor.execute(query, (row[1],))
                            query = """DELETE FROM timeoutProxiesOlxUa WHERE proxyID = %s"""
                            cursor.execute(query, (row[0],))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def get_announce(self, announce_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """SELECT * FROM announcementsolxua WHERE id = %s"""
                    cursor.execute(query, (announce_id,))
                    return cursor.fetchone()
        except Exception as ex:
            print(ex)

    def update_phone_in_announce(self, phone, announce_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE announcementsolxua SET phone = %s WHERE id = %s"""
                    cursor.execute(query, (phone, announce_id))
                    conn.commit()
        except Exception as ex:
            print(ex)

    def save_browsing_announces(self, announces_id):
        try:
            with self._get_connect() as conn:
                with conn.cursor() as cursor:
                    query = """UPDATE announcementsolxua SET views = 1 WHERE id = %s"""
                    for i in announces_id:
                        cursor.execute(query, (i,))
                    conn.commit()
        except Exception as ex:
            print(ex)
