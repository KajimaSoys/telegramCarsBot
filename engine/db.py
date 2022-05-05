import psycopg2
from typing import Dict, List, Tuple
import variables

conn = psycopg2.connect(
    database="cars_bot",
    user="postgres",
    password=variables.password)

cursor = conn.cursor()

print("Database opened successfully")

def insert(table: str, column_values: Dict):
    columns = ', '.join( column_values.keys() )
    values = tuple(column_values.values())
    placeholders = "%s, " * len(column_values.keys())
    placeholders = placeholders[:-2]
    cursor.execute(f"""
        INSERT INTO {table} ({columns})
        VALUES ({placeholders});""",
        values)
    conn.commit()

def select(table: str, search_str: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    cursor.execute('SELECT set_limit(0.15);')
    conn.commit()
    cursor.execute(f"""
        SELECT {columns_joined}, similarity(search_string, '{search_str}') as sml
        FROM {table} WHERE search_string % '{search_str}'
        ORDER BY sml
        DESC, search_string LIMIT 25;
        """)
    rows = cursor.fetchall()
    count = cursor.rowcount
    result = []
    for row in rows:
        # print(row)
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        dict_row['sml'] = row[-1:][0]
        dict_row['db'] = table
        result.append(dict_row)
    return result, count


def handle_all(table: str, column: str) -> List[Tuple]:
    cursor.execute(f"""
        SELECT {column} FROM {table};
        """)
    rows = cursor.fetchall()
    # print(rows)
    result = []
    for row in rows:
        try:
            result.append(row[0])
        except Exception as E:
            print(f'[!] Error during handle all saleid: {E}\nСontinuation of the operation\n')

    return result

def handle_staff(table: str, column: str):
    cursor.execute(f"""
        SELECT id, username
        FROM {table}
        WHERE {column}=True;
        """)
    result = cursor.fetchall()
    return result

# def handle_waiting(table: str):
#     cursor.execute(f"""
#         SELECT id,
#         """)

def update_confirm(table: str, where_column: str, where_string: str, status: str):
    cursor.execute(f"""
        UPDATE {table}
        SET wait_confirm = {status} 
        WHERE {where_column}={where_string};
        """)
    conn.commit()

def update_status(table: str, id: int, status: str):
    cursor.execute(f"""
        UPDATE {table}
        SET is_manager={status}
        WHERE id={id};
        """)
    conn.commit()

def delete_dupes(table: str, column: str):
    print('Удаление дубликатов..')
    cursor.execute(f"""
        DELETE FROM {table} a USING (
        SELECT MIN(ctid) as ctid, {column}
        FROM {table}
        GROUP BY {column}
        HAVING COUNT(*) > 1
        ) b
        WHERE a.{column} = b.{column}
        AND a.ctid <> b.ctid;
        """)
    conn.commit()
    print('Все дубликаты удалены!')

def reindex():
    print('Пересоздание таблицы слов..')
    cursor.execute(f"""
        TRUNCATE words RESTART IDENTITY;
        """)
    conn.commit()
    cursor.execute(f"""
        INSERT INTO words (word)
        SELECT word FROM
        ts_stat('SELECT to_tsvector(''simple'', search_string) FROM autoru');
        """)
    conn.commit()
    cursor.execute(f"""
        INSERT INTO words (word)
        SELECT word FROM
        ts_stat('SELECT to_tsvector(''simple'', search_string) FROM avito');
        """)
    conn.commit()
    print('Таблица слов пересоздана!')
    print('Перестроение триграммного индексирования..')
    cursor.execute(f"""
        REINDEX INDEX words_idx;
        """)
    conn.commit()
    cursor.execute(f"""
            REINDEX INDEX autoru_trgm_idx;
            """)
    conn.commit()
    cursor.execute(f"""
            REINDEX INDEX avito_trgm_idx;
            """)
    conn.commit()
    print('Перестроение завершено. Таблица пригодна для поиска.')


def select_request(user: str):
    cursor.execute(f"""
        SELECT request FROM requests
        WHERE user_id='{user}';
        """)
    result = cursor.fetchall()[0][0]
    return result
# def insert_request(user: str, request: str):
#     cursor.execute(f"""
#         INSERT INTO requests
#         """)

def delete_row(table: str, column: str, column_match: str):
    cursor.execute(f"""
        DELETE FROM {table}
        WHERE {column}='{column_match}';
        """)
    conn.commit()

def show_managers():
    cursor.execute(f"""
        SELECT id, username, is_manager FROM users;
        """)
    result = cursor.fetchall()
    conn.commit()
    return result

