from flask import Flask, jsonify, render_template, request
import sqlite3
import os

app = Flask(__name__)

# -----------------------------
# SQLite configuration
# -----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'db', 'books.db')


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------------
# API: Books
# -----------------------------
@app.route('/api/books', methods=['GET'])
def get_all_books():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Books")
        books = cursor.fetchall()
        conn.close()

        book_list = [{
            'book_id': b['book_id'],
            'title': b['title'],
            'publication_year': b['publication_year']
        } for b in books]

        return jsonify({'books': book_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------
# API: Authors
# -----------------------------
@app.route('/api/authors', methods=['GET'])
def get_all_authors():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Authors")
        authors = cursor.fetchall()
        conn.close()

        author_list = [{'author_id': a['author_id'], 'name': a['name']} for a in authors]
        return jsonify({'authors': author_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------
# API: Add Book
# -----------------------------
@app.route('/api/add_book', methods=['POST'])
def add_book():
    try:
        data = request.get_json()
        title = data.get('title')
        publication_year = data.get('publication_year')

        if not title or not publication_year:
            return jsonify({'error': 'Missing fields'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Books (title, publication_year) VALUES (?, ?)",
            (title, publication_year)
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Book added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------
# Reviews (SQLite version)
# -----------------------------

@app.route('/api/reviews', methods=['GET'])
def get_all_reviews():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT r.id, r.book_id, b.title AS book_title,
                   r.user, r.rating, r.comment, r.created_at
            FROM Reviews r
            JOIN Books b ON r.book_id = b.book_id
            ORDER BY r.created_at DESC
            """
        )
        rows = cursor.fetchall()
        conn.close()

        reviews = []
        for r in rows:
            reviews.append({
                "id": r["id"],
                "book_id": r["book_id"],
                "book_title": r["book_title"],
                "user": r["user"],
                "rating": r["rating"],
                "comment": r["comment"],
                "created_at": r["created_at"]
            })
        return jsonify({"reviews": reviews})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/add_review', methods=['POST'])
def add_review():
    try:
        data = request.get_json()
        book_id = data.get('book_id')
        user = data.get('user')
        rating = data.get('rating')
        comment = data.get('comment')

        if not all([book_id, user, rating, comment]):
            return jsonify({'error': 'Missing fields'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Reviews (book_id, user, rating, comment)
            VALUES (?, ?, ?, ?)
            """,
            (book_id, user, rating, comment)
        )
        conn.commit()
        conn.close()

        return jsonify({'message': 'Review added'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/books/<int:book_id>/reviews', methods=['GET'])
def get_reviews_for_book(book_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, book_id, user, rating, comment, created_at
            FROM Reviews
            WHERE book_id = ?
            ORDER BY created_at DESC
            """,
            (book_id,)
        )
        rows = cursor.fetchall()
        conn.close()

        reviews = [{
            'id': r['id'],
            'book_id': r['book_id'],
            'user': r['user'],
            'rating': r['rating'],
            'comment': r['comment'],
            'created_at': r['created_at']
        } for r in rows]

        return jsonify({'book_id': book_id, 'reviews': reviews})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------
# Root route (frontend)
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')


# -----------------------------
# Run app
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
