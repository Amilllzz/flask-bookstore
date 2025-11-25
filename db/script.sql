CREATE TABLE IF NOT EXISTS Books (
book_id INTEGER PRIMARY KEY,
title TEXT NOT NULL,
publication_year INTEGER
);

CREATE TABLE IF NOT EXISTS Authors (
author_id INTEGER PRIMARY KEY,
name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Users (
user_id INTEGER PRIMARY KEY,
username TEXT NOT NULL,
email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Reviews (
review_id INTEGER PRIMARY KEY,
book_id INTEGER NOT NULL,
user_id INTEGER NOT NULL,
rating INTEGER,
review_text TEXT,
review_date DATE,
FOREIGN KEY (book_id) REFERENCES Books (book_id),
FOREIGN KEY (user_id) REFERENCES Users (user_id)
);

CREATE TABLE IF NOT EXISTS book_author (
book_id INTEGER NOT NULL,
author_id INTEGER NOT NULL,
PRIMARY KEY (book_id, author_id),
FOREIGN KEY (book_id) REFERENCES Books (book_id),
FOREIGN KEY (author_id) REFERENCES Authors (author_id)
);
CREATE TABLE IF NOT EXISTS logs (
  id                BIGINT AUTO_INCREMENT PRIMARY KEY,
  ts                TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  function_name     VARCHAR(128) NOT NULL,
  status            ENUM('ok','error') NOT NULL,
  execution_time_ms INT NULL,
  message           TEXT NULL,
  http_method       VARCHAR(10) NULL,
  path              VARCHAR(255) NULL,
  request_id        CHAR(36) NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


------------------
