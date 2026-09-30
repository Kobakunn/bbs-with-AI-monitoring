from flask import Flask, render_template, request, session, redirect, url_for
import os
import sqlite3

from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

app.secret_key = "dev-secret-key"

DATABASE = "database/bbs.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def add_test_posts():
    connection = get_db_connection()

    now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    connection.execute(
        """
        INSERT INTO posts (
            user_id,
            content,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            1,
            "NLPを使った掲示板を作っています！",
            now,
            now
        )
    )

    connection.execute(
        """
        INSERT INTO posts (
            user_id,
            content,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            1,
            "BERTについて勉強しています。",
            now,
            now
        )
    )

    connection.commit()
    connection.close()


def init_db():
    os.makedirs("database", exist_ok=True)

    connection = get_db_connection()

    # ユーザーテーブル
    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        )
    """)

    # 投稿テーブル
    connection.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        print("ログイン処理が実行されました")

        username = request.form["username"]
        password = request.form["password"]

        print("username:", username)

        connection = get_db_connection()

        user = connection.execute(
            """
            SELECT *
            FROM users
            WHERE username = ?
            """,
            (username,)
        ).fetchone()

        connection.close()

        print("user:", user)

        if user is None:
            print("ユーザーが見つかりません")

            return render_template(
                "login.html",
                error="ユーザー名またはパスワードが正しくありません。"
            )

        print("ユーザーが見つかりました")
        print("password_hash:", user["password_hash"])

        if not check_password_hash(user["password_hash"], password):
            print("パスワードが一致しません")

            return render_template(
                "login.html",
                error="ユーザー名またはパスワードが正しくありません。"
            )

        print("パスワードOK")

        session["user_id"] = user["id"]
        session["username"] = user["username"]

        print("session:", session)

        return redirect(url_for("posts"))

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if password != confirm_password:
            return render_template(
                "register.html",
                error="パスワードが一致していません。"
            )

        # パスワードをハッシュ化
        password_hash = generate_password_hash(password)

        connection = get_db_connection()

        try:
            connection.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
                """,
                (username, password_hash)
            )

            connection.commit()

        except sqlite3.IntegrityError:
            connection.close()

            return render_template(
                "register.html",
                error="そのユーザー名は既に使用されています。"
            )

        connection.close()

        return render_template(
            "register_complete.html",
            username=username
        )

    return render_template("register.html")


@app.route("/posts")
def posts():
    if "user_id" not in session:
        return redirect(url_for("login"))

    # 1ページに表示する投稿数
    per_page = 5

    # URLからページ番号を取得
    page = request.args.get("page", 1, type=int)

    # 0以下のページを防ぐ
    if page < 1:
        page = 1

    # OFFSETを計算
    offset = (page - 1) * per_page

    connection = get_db_connection()

    # 投稿総数を取得
    total_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM posts
        """
    ).fetchone()[0]

    # 現在のページに表示する投稿を取得
    posts = connection.execute(
        """
        SELECT
            posts.id,
            posts.user_id,
            posts.content,
            posts.created_at,
            posts.updated_at,
            users.username
        FROM posts
        INNER JOIN users
            ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
        LIMIT ?
        OFFSET ?
        """,
        (per_page, offset)
    ).fetchall()

    connection.close()

    # ページ数を計算
    total_pages = (total_count + per_page - 1) // per_page

    return render_template(
        "posts.html",
        posts=posts,
        page=page,
        total_pages=total_pages
    )


@app.route("/posts/create", methods=["GET", "POST"])
def create_post():
    # ログインチェック
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        content = request.form["content"].strip()

        # 空文字チェック
        if not content:
            return render_template(
                "create_post.html",
                error="投稿内容を入力してください。"
            )

        # 現在日時
        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        connection = get_db_connection()

        connection.execute(
            """
            INSERT INTO posts (
                user_id,
                content,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                session["user_id"],
                content,
                now,
                now
            )
        )

        connection.commit()
        connection.close()

        # 投稿一覧へ戻る
        return redirect(url_for("posts"))

    return render_template("create_post.html")


@app.route("/posts/edit/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    # ログインチェック
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    post = connection.execute(
        """
        SELECT *
        FROM posts
        WHERE id = ?
        """,
        (post_id,)
    ).fetchone()

    # 投稿が存在しない
    if post is None:
        connection.close()
        return "投稿が見つかりません。", 404

    # 自分の投稿か確認
    if post["user_id"] != session["user_id"]:
        connection.close()
        return "この投稿を修正する権限がありません。", 403

    if request.method == "POST":
        content = request.form["content"].strip()

        # 空文字チェック
        if not content:
            connection.close()

            return render_template(
                "edit_post.html",
                post=post,
                error="投稿内容を入力してください。"
            )

        now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        connection.execute(
            """
            UPDATE posts
            SET content = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (content, now, post_id)
        )

        connection.commit()
        connection.close()

        return redirect(url_for("posts"))

    connection.close()

    return render_template(
        "edit_post.html",
        post=post
    )


@app.route("/posts/delete/<int:post_id>", methods=["GET", "POST"])
def delete_post(post_id):
    # ログインチェック
    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()

    post = connection.execute(
        """
        SELECT *
        FROM posts
        WHERE id = ?
        """,
        (post_id,)
    ).fetchone()

    # 投稿が存在しない
    if post is None:
        connection.close()
        return "投稿が見つかりません。", 404

    # 自分の投稿か確認
    if post["user_id"] != session["user_id"]:
        connection.close()
        return "この投稿を削除する権限がありません。", 403

    # GET → 削除確認画面を表示
    if request.method == "GET":
        connection.close()

        return render_template(
            "delete_confirm.html",
            post=post
        )

    # POST → 実際に削除
    connection.execute(
        """
        DELETE FROM posts
        WHERE id = ?
        """,
        (post_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("posts"))


@app.route("/logout")
def logout():
    session.clear()

    return redirect(url_for("login"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)