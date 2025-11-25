from flask import Flask, jsonify, render_template, request
import sqlite3
import pymongo

app = Flask(__name__)

# -----------------------------
# Database configurations
# -----------------------------

# SQLite setup
DATABASE = 'db/books.db'

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
mongo_db = client['book_database']             # MongoDB database
reviews_collection = mongo_db['reviews']       # MongoDB collection



# Quick connection test
try:
    mongo_db.command("ping")
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print("❌ MongoDB connection failed:", e)

# -----------------------------
# SQLite helper functions
# -----------------------------
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

        book_list = []
        for book in books:
            book_list.append({
                'book_id': book['book_id'],
                'title': book['title'],
                'publication_year': book['publication_year']
            })

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
            return jsonify({'error': 'Missing title or publication_year'}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Books (title, publication_year) VALUES (?, ?)", (title, publication_year))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Book added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------
# API: MongoDB (Reviews)
# -----------------------------

# Get all reviews
@app.route('/api/reviews', methods=['GET'])
def get_all_reviews():
    try:
        print("📡 Fetching all reviews from MongoDB...")

        # Check which database and collection Flask is using
        print("🗂️ Current database:", mongo_db.name)
        print("📁 Collection name:", reviews_collection.name)

        reviews = list(reviews_collection.find({}, {'_id': 0}))
        print("✅ Found", len(reviews), "reviews")
        if len(reviews) > 0:
            print("Sample review:", reviews[0])

        return jsonify({'reviews': reviews})
    except Exception as e:
        print("❌ Error fetching reviews:", e)
        return jsonify({'error': str(e)}), 500



# Add a new review
@app.route('/api/add_review', methods=['POST'])
def add_review():
    try:
        data = request.get_json()
        book_id = int(data.get('book_id')) if data.get('book_id') else None  # 👈 convert to int
        user = data.get('user')
        rating = data.get('rating')
        comment = data.get('comment')

        if not all([book_id, user, rating, comment]):
            return jsonify({'error': 'Missing required fields'}), 400

        review = {
            'book_id': book_id,
            'user': user,
            'rating': rating,
            'comment': comment
        }
        result = reviews_collection.insert_one(review)
        print(f"✅ Inserted review for book {book_id} (id={result.inserted_id})")

        return jsonify({'message': 'Review added successfully'})
    except Exception as e:
        print("❌ Error inserting review:", e)
        return jsonify({'error': str(e)}), 500



# Get reviews for a specific book
@app.route('/api/books/<int:book_id>/reviews', methods=['GET'])
def get_reviews_for_book(book_id):
    try:
        reviews = list(reviews_collection.find({'book_id': book_id}, {'_id': 0}))
        return jsonify({'book_id': book_id, 'reviews': reviews})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------
# Root route for frontend
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')


# -----------------------------
# Run app
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
