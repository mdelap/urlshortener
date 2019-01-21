from flask import Flask, request, render_template, redirect
from math import floor
from sqlite3 import OperationalError
import string
import sqlite3

from urllib.parse import urlparse  # Python 3
str_encode = str.encode

#import base64


app = Flask(__name__)
host = 'http://localhost:5000/'


def _encode(num, b=94):
    if b <= 0 or b > 94:
        return 0
    base = string.digits + string.ascii_letters + string.punctuation
    r = num % b
    res = base[r]
    q = floor(num / b)
    while q:
        r = q % b
        q = floor(q / b)
        res = base[int(r)] + res
    return res


def _decode(num, b=94):
    base = string.digits + string.ascii_letters + string.punctuation
    limit = len(num)
    res = 0
    for i in range(limit):
        res = b * res + base.find(num[i])
    return res


@app.route('/', methods=['GET', 'POST'])
def home():
    conn= sqlite3.connect('db.db')
    if request.method == 'POST':
        url = str_encode(request.form.get('url')).strip()
        url = url.decode('utf-8').strip()
        if len(url)==0:
           return render_template('home.html',short_url='Invalid size', original_url='URL can not be empty')
        if len(url)>300:
           return render_template('home.html',short_url='Invalid size', original_url='URL can not be greater than 300 chars lenght')
        with conn:
            cur = conn.cursor()
            cur.execute("SELECT shortUrl FROM URL WHERE longUrl = :longUrl", {"longUrl": url})
            row = cur.fetchall()
            if len(row)==0:
                '''
                long URL has not been found
                '''
                cur.execute('SELECT shortUrl FROM URL WHERE shortUrl=?', [url])
                row = cur.fetchall()       
  
                if len(row)==0:
                   result_cursor=cur.execute("INSERT INTO URL (longUrl) values (?)",[url])
                   lastrowid=result_cursor.lastrowid
                   encoding= _encode(lastrowid)
                   #rollback if the encode/decode fails
                   if _decode(encoding)==lastrowid:
                        encoded_string = 'http://'+str(encoding).strip()
                        update=cur.execute("UPDATE URL set shortUrl = (?) where Id = (?)", [encoded_string, lastrowid])
                        return render_template('home.html', short_url=encoded_string, original_url=url)
                   else:
                        cur = conn.cursor()
                        delete=cur.execute("delete from URL where Id = (?)", [lastrowid])
                        conn.commit()
                        return render_template('home.html', short_url='could not be shortened',  original_url=url)
                else:
                    cur = conn.cursor()
                    cur.execute("SELECT longUrl FROM URL WHERE shortUrl = (?)", [url])
                    row = cur.fetchall()
                    return render_template('home.html', short_url= url +' Original Url:'+str(row[0][0]), original_url=url )            
            else:    
                shortUrl=row[0][0]
                return render_template('home.html', short_url= shortUrl, original_url=url)
    return render_template('home.html')


if __name__ == '__main__':
    app.run(debug=True)