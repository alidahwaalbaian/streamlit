import sqlite3
import streamlit as st
from datetime import datetime
import os

# Initialize database
def init_db():
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                date TEXT NOT NULL,
                page_id INTEGER NOT NULL,
                FOREIGN KEY(page_id) REFERENCES pages(id)
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                description TEXT,
                page_id INTEGER NOT NULL,
                FOREIGN KEY(page_id) REFERENCES pages(id)
            )
        ''')
        conn.commit()

# Function to add a new page
def add_page(name):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO pages (name) VALUES (?)', (name,))
        conn.commit()

# Function to get all pages
def get_pages():
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM pages')
        return c.fetchall()

# Function to delete a page and its posts and links
def delete_page(page_id):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('DELETE FROM posts WHERE page_id = ?', (page_id,))
        c.execute('DELETE FROM links WHERE page_id = ?', (page_id,))
        c.execute('DELETE FROM pages WHERE id = ?', (page_id,))
        conn.commit()

# Function to update a page name
def update_page(page_id, name):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('UPDATE pages SET name = ? WHERE id = ?', (name, page_id))
        conn.commit()

# Function to add a new blog post
def add_post(title, content, page_id):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO posts (title, content, date, page_id) VALUES (?, ?, ?, ?)', 
                  (title, content, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), page_id))
        conn.commit()

# Function to get all blog posts for a page
def get_posts(page_id):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM posts WHERE page_id = ?', (page_id,))
        return c.fetchall()

# Function to delete a blog post
def delete_post(post_id):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('DELETE FROM posts WHERE id = ?', (post_id,))
        conn.commit()

# Function to update a blog post
def update_post(post_id, title, content):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('UPDATE posts SET title = ?, content = ?, date = ? WHERE id = ?', 
                  (title, content, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), post_id))
        conn.commit()

# Function to add a new link
def add_link(url, description, page_id):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('INSERT INTO links (url, description, page_id) VALUES (?, ?, ?)', 
                  (url, description, page_id))
        conn.commit()

# Function to get all links for a page
def get_links(page_id):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM links WHERE page_id = ?', (page_id,))
        return c.fetchall()

# Function to delete a link
def delete_link(link_id):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('DELETE FROM links WHERE id = ?', (link_id,))
        conn.commit()

# Function to update a link
def update_link(link_id, url, description):
    with sqlite3.connect('blog.db') as conn:
        c = conn.cursor()
        c.execute('UPDATE links SET url = ?, description = ? WHERE id = ?', 
                  (url, description, link_id))
        conn.commit()

# User authentication using session state
class SessionState:
    def __init__(self):
        self.is_admin = False

# Main App
def main():
    # Get the directory of the current script
    THIS_DIR = Path(__file__).parent
    ASSETS = THIS_DIR / "assets"
    gif_path = ASSETS / "nwlg.gif"

    # Check if the file exists
    if not gif_path.exists():
        st.error(f"File not found: {gif_path}")
        return

    try:
        # Display the GIF image
        st.image(str(gif_path))
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return

    # Render the HTML content
    st.markdown(
        """
        <div style="display: flex; align-items: center; flex-direction: row;">
            <h1 style="margin: 0 10px;">أرشيف محاضرات الشيخ حسن الأشقر</h1>
        </div>
        """, 
        unsafe_allow_html=True
    )

    #st.title("Simple Blog App")
    session_state = st.session_state.get("session", SessionState())
    st.session_state["session"] = session_state

    # Inject CSS for RTL support
    st.markdown(
        """
        <style>
        body {
            direction: rtl;
            text-align: right;
        }
        </style>
        """, unsafe_allow_html=True
    )

    menu = ["الرئيسية", "الإدارة"]  # Arabic menu items
    choice = st.sidebar.selectbox("القائمة", menu)

    if choice == "الرئيسية":  # Home
        st.subheader("الرئيسية")
        pages = get_pages()
        if pages:
            page_names = [page[1] for page in pages]
            selected_page = st.selectbox("اختر الصفحة", page_names)
            page_id = next((page[0] for page in pages if page[1] == selected_page), None)
            if page_id is not None:
                posts = get_posts(page_id)
                links = get_links(page_id)
                if posts:
                    st.subheader("المقالات")
                    for post in posts:
                        st.markdown(f"## {post[1]}", unsafe_allow_html=True)
                        st.markdown(f"#### {post[3]}", unsafe_allow_html=True)
                        st.markdown(post[2], unsafe_allow_html=True)
                else:
                    st.write("لا توجد مقالات متاحة لهذه الصفحة.")

                if links:
                    st.subheader("الروابط")
                    for link in links:
                        st.markdown(f"[{link[2]}]({link[1]})", unsafe_allow_html=True)
                else:
                    st.write("لا توجد روابط متاحة لهذه الصفحة.")
            else:
                st.write("اختر صفحة من القائمة الجانبية لعرض محتوياتها.")
        else:
            st.write("لا توجد صفحات متاحة.")

    elif choice == "الإدارة":  # Admin
        if not session_state.is_admin:
            st.subheader("صفحة الإدارة")
            username = st.text_input("اسم المستخدم")
            password = st.text_input("كلمة المرور", type="password")
            if st.button("تسجيل الدخول"):
                if username == "admin" and password == "password":  # Replace with actual authentication logic
                    session_state.is_admin = True
                    st.success("تم تسجيل الدخول كمسؤول!")
                else:
                    st.error("اسم المستخدم أو كلمة المرور غير صحيحة.")
        else:
            st.subheader("صفحة الإدارة")

            admin_choice = st.selectbox("الخيارات", ["إضافة صفحة", "تعديل صفحة", "حذف صفحة", "إضافة مقال", "تعديل مقال", "حذف مقال", "إضافة رابط", "تعديل رابط", "حذف رابط"])

            if st.button("تسجيل الخروج"):
                session_state.is_admin = False
                st.success("تم تسجيل الخروج بنجاح")

            if admin_choice == "إضافة صفحة":  # Add Page
                st.subheader("إضافة صفحة جديدة")
                new_page_name = st.text_input("اسم الصفحة")
                if st.button("إضافة الصفحة"):
                    add_page(new_page_name)
                    st.success(f"تمت إضافة الصفحة: '{new_page_name}' بنجاح")

            elif admin_choice == "تعديل صفحة":  # Edit Page
                st.subheader("تعديل صفحة")
                pages = get_pages()
                if pages:
                    page_names = [page[1] for page in pages]
                    selected_page = st.selectbox("اختر الصفحة للتعديل", page_names)
                    page_id = next((page[0] for page in pages if page[1] == selected_page), None)
                    new_page_name = st.text_input("اسم الصفحة", value=selected_page)
                    if st.button("تحديث الصفحة"):
                        update_page(page_id, new_page_name)
                        st.success(f"تم تحديث الصفحة: '{new_page_name}' بنجاح")
                else:
                    st.write("لا توجد صفحات متاحة للتعديل.")

            elif admin_choice == "حذف صفحة":  # Delete Page
                st.subheader("حذف صفحة")
                pages = get_pages()
                if pages:
                    page_names = [page[1] for page in pages]
                    selected_page = st.selectbox("اختر الصفحة للحذف", page_names)
                    page_id = next((page[0] for page in pages if page[1] == selected_page), None)
                    if st.button("حذف الصفحة"):
                        delete_page(page_id)
                        st.success(f"تم حذف الصفحة: '{selected_page}' بنجاح")
                else:
                    st.write("لا توجد صفحات متاحة للحذف.")

            elif admin_choice == "إضافة مقال":  # Add Post
                st.subheader("إضافة مقال جديد")
                pages = get_pages()
                if pages:
                    page_names = [page[1] for page in pages]
                    selected_page = st.selectbox("اختر الصفحة", page_names)
                    page_id = next((page[0] for page in pages if page[1] == selected_page), None)
                    new_title = st.text_input("عنوان المقال")
                    new_content = st.text_area("محتوى المقال")
                    if st.button("إضافة المقال"):
                        add_post(new_title, new_content, page_id)
                        st.success(f"تمت إضافة المقال: '{new_title}' بنجاح")
                else:
                    st.write("لا توجد صفحات متاحة. يرجى إضافة صفحة أولاً.")

            elif admin_choice == "تعديل مقال":  # Edit Post
                st.subheader("تعديل مقال")
                pages = get_pages()
                if pages:
                    page_names = [page[1] for page in pages]
                    selected_page = st.selectbox("اختر الصفحة", page_names)
                    page_id = next((page[0] for page in pages if page[1] == selected_page), None)
                    posts = get_posts(page_id)
                    if posts:
                        post_titles = [post[1] for post in posts]
                        selected_title = st.selectbox("اختر المقال للتعديل", post_titles)
                        selected_post = next((post for post in posts if post[1] == selected_title), None)
                        new_title = st.text_input("عنوان المقال", value=selected_post[1])
                        new_content = st.text_area("محتوى المقال", value=selected_post[2])
                        if st.button("تحديث المقال"):
                            update_post(selected_post[0], new_title, new_content)
                            st.success(f"تم تحديث المقال: '{new_title}' بنجاح")
                    else:
                        st.write("لا توجد مقالات متاحة لهذه الصفحة.")
                else:
                    st.write("لا توجد صفحات متاحة.")

            elif admin_choice == "حذف مقال":  # Delete Post
                st.subheader("حذف مقال")
                pages = get_pages()
                if pages:
                    page_names = [page[1] for page in pages]
                    selected_page = st.selectbox("اختر الصفحة", page_names)
                    page_id = next((page[0] for page in pages if page[1] == selected_page), None)
                    posts = get_posts(page_id)
                    if posts:
                        post_titles = [post[1] for post in posts]
                        selected_title = st.selectbox("اختر المقال للحذف", post_titles)
                        selected_post = next((post for post in posts if post[1] == selected_title), None)
                        if st.button("حذف المقال"):
                            delete_post(selected_post[0])
                            st.success(f"تم حذف المقال: '{selected_title}' بنجاح")
                    else:
                        st.write("لا توجد مقالات متاحة لهذه الصفحة.")
                else:
                    st.write("لا توجد صفحات متاحة.")

            elif admin_choice == "إضافة رابط":  # Add Link
                st.subheader("إضافة رابط جديد")
                pages = get_pages()
                if pages:
                    page_names = [page[1] for page in pages]
                    selected_page = st.selectbox("اختر الصفحة", page_names)
                    page_id = next((page[0] for page in pages if page[1] == selected_page), None)
                    new_url = st.text_input("الرابط")
                    new_description = st.text_input("وصف الرابط")
                    if st.button("إضافة الرابط"):
                        add_link(new_url, new_description, page_id)
                        st.success(f"تمت إضافة الرابط: '{new_description}' بنجاح")
                else:
                    st.write("لا توجد صفحات متاحة. يرجى إضافة صفحة أولاً.")

            elif admin_choice == "تعديل رابط":  # Edit Link
                st.subheader("تعديل رابط")
                pages = get_pages()
                if pages:
                    page_names = [page[1] for page in pages]
                    selected_page = st.selectbox("اختر الصفحة", page_names)
                    page_id = next((page[0] for page in pages if page[1] == selected_page), None)
                    links = get_links(page_id)
                    if links:
                        link_descriptions = [link[2] for link in links]
                        selected_description = st.selectbox("اختر الرابط للتعديل", link_descriptions)
                        selected_link = next((link for link in links if link[2] == selected_description), None)
                        new_url = st.text_input("الرابط", value=selected_link[1])
                        new_description = st.text_input("وصف الرابط", value=selected_link[2])
                        if st.button("تحديث الرابط"):
                            update_link(selected_link[0], new_url, new_description)
                            st.success(f"تم تحديث الرابط: '{new_description}' بنجاح")
                    else:
                        st.write("لا توجد روابط متاحة لهذه الصفحة.")
                else:
                    st.write("لا توجد صفحات متاحة.")

            elif admin_choice == "حذف رابط":  # Delete Link
                st.subheader("حذف رابط")
                pages = get_pages()
                if pages:
                    page_names = [page[1] for page in pages]
                    selected_page = st.selectbox("اختر الصفحة", page_names)
                    page_id = next((page[0] for page in pages if page[1] == selected_page), None)
                    links = get_links(page_id)
                    if links:
                        link_descriptions = [link[2] for link in links]
                        selected_description = st.selectbox("اختر الرابط للحذف", link_descriptions)
                        selected_link = next((link for link in links if link[2] == selected_description), None)
                        if st.button("حذف الرابط"):
                            delete_link(selected_link[0])
                            st.success(f"تم حذف الرابط: '{selected_description}' بنجاح")
                    else:
                        st.write("لا توجد روابط متاحة لهذه الصفحة.")
                else:
                    st.write("لا توجد صفحات متاحة.")

if __name__ == "__main__":
    init_db()
    main()
