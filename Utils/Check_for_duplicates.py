import os
import hashlib
import sqlite3

def find_duplicates(base_folder):
    conn = sqlite3.connect('duplicate_search.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS progress
                 (root text, PRIMARY KEY (root))''')
    c.execute('''CREATE TABLE IF NOT EXISTS duplicates
                 (file_path text, file_hash text, PRIMARY KEY (file_path))''')
    c.execute('''CREATE TABLE IF NOT EXISTS original_files
                 (file_path text, file_hash text, PRIMARY KEY (file_path))''')

    hashes = {}
    last_root = None
    c.execute('''SELECT root FROM progress''')
    result = c.fetchone()
    if result is not None:
        last_root = result[0]
    for root, dirs, files in os.walk(base_folder):
        if last_root is not None:
            if root == last_root:
                last_root = None
            else:
                continue
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha1(f.read()).hexdigest()
            if file_hash in hashes:
                print(f'Duplicate found: {file_path}')
                print(f'Original file: {hashes[file_hash]}')
                c.execute('''INSERT INTO duplicates (file_path, file_hash)
                              VALUES (?, ?)''', (file_path, file_hash))
                c.execute('''SELECT file_path FROM original_files
                              WHERE file_hash=?''', (file_hash,))
                original_file = c.fetchone()[0]
                c.execute('''INSERT INTO original_files (file_path, file_hash)
                              VALUES (?, ?)''', (original_file, file_hash))
            else:
                hashes[file_hash] = file_path
                c.execute('''INSERT INTO original_files (file_path, file_hash)
                              VALUES (?, ?)''', (file_path, file_hash))
        c.execute('''INSERT OR REPLACE INTO progress (root) VALUES (?)''', (root,))
        conn.commit()
    conn.close()

find_duplicates('C:\\')
