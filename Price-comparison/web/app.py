import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'change-this-secret-key')

# إعدادات قاعدة البيانات
def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "YOUR_PASSWORD"),
        database=os.getenv("DB_NAME", "price_compare")
    )

# ديكوريتر للتحقق من تسجيل الدخول
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('يجب تسجيل الدخول أولاً', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# الصفحة الرئيسية
@app.route('/')
def home():
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM categories LIMIT 6")
    categories = cur.fetchall()
    
    user_id = session.get('user_id')
    
    # تأكد من وجود EXISTS هنا وتمرير user_id
    cur.execute("""
        SELECT p.*, c.name as category_name,
        (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price,
        EXISTS(SELECT 1 FROM favorites WHERE user_id = %s AND product_id = p.id) as is_favorite
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC LIMIT 8
    """, (user_id,))
    products = cur.fetchall()
    
    cur.close()
    db.close()
    return render_template('index.html', categories=categories, products=products)

# صفحة الفئات
@app.route('/categories')
def categories():
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM categories")
    categories = cur.fetchall()
    
    category_id = request.args.get('id')
    user_id = session.get('user_id') # الحصول على id المستخدم الحالي
    
    if category_id:
        # أضفنا سطر الـ EXISTS هنا ليعرف النظام إذا كان المنتج مفضلاً أم لا
        cur.execute("""
            SELECT p.*, c.name as category_name,
            (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price,
            EXISTS(SELECT 1 FROM favorites WHERE user_id = %s AND product_id = p.id) as is_favorite
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.category_id = %s
        """, (user_id, category_id))
    else:
        cur.execute("""
            SELECT p.*, c.name as category_name,
            (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price,
            EXISTS(SELECT 1 FROM favorites WHERE user_id = %s AND product_id = p.id) as is_favorite
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
        """, (user_id,))
        
    products = cur.fetchall()
    cur.close()
    db.close()
    return render_template('categories.html', categories=categories, products=products)

# صفحة المنتجات حسب الفئة
@app.route('/category/<int:category_id>')
def category_products(category_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # جلب معلومات الفئة
    cur.execute("SELECT * FROM categories WHERE id = %s", (category_id,))
    category = cur.fetchone()
    
    if not category:
        flash('الفئة غير موجودة', 'danger')
        return redirect(url_for('categories'))
    
    # جلب المنتجات
    user_id = session.get('user_id')
    cur.execute("""
        SELECT p.*,
        (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price,
        EXISTS(SELECT 1 FROM favorites WHERE user_id = %s AND product_id = p.id) as is_favorite
        FROM products p
        WHERE p.category_id = %s
    """, (user_id, category_id))
    products = cur.fetchall()
    
    cur.close()
    db.close()
    
    return render_template('category_products.html', category=category, products=products)

# صفحة الخصومات
@app.route('/discounts')
def discounts():
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    user_id = session.get('user_id')
    # جلب المنتجات التي تملك سعراً قديماً أكبر من السعر الحالي في أي متجر
    cur.execute("""
        SELECT DISTINCT p.*, c.name as category_name,
        (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price,
        (SELECT old_price FROM product_stores WHERE product_id = p.id AND old_price > price LIMIT 1) as old_price,
        EXISTS(SELECT 1 FROM favorites WHERE user_id = %s AND product_id = p.id) as is_favorite
        FROM products p
        JOIN product_stores ps ON p.id = ps.product_id
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE ps.old_price > ps.price
    """, (user_id,))
    products = cur.fetchall()
    
    cur.close()
    db.close()
    
    return render_template('discounts.html', products=products)

# صفحة تفاصيل المنتج
@app.route('/product/<int:product_id>')
def product(product_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # جلب معلومات المنتج
    cur.execute("""
        SELECT p.*, c.name as category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.id = %s
    """, (product_id,))
    product_info = cur.fetchone()
    
    if not product_info:
        flash('المنتج غير موجود', 'danger')
        return redirect(url_for('home'))
    
    # جلب أسعار المنتج من المتاجر
    cur.execute("""
        SELECT ps.*, s.name as store_name, s.logo as store_logo, s.rating as store_rating
        FROM product_stores ps
        JOIN stores s ON ps.store_id = s.id
        WHERE ps.product_id = %s
        ORDER BY ps.price ASC
    """, (product_id,))
    stores = cur.fetchall()
    
    # التحقق من المفضلة للمستخدم
    is_favorite = False
    if 'user_id' in session:
        cur.execute("SELECT * FROM favorites WHERE user_id = %s AND product_id = %s", 
                   (session['user_id'], product_id))
        is_favorite = cur.fetchone() is not None
        
    
    cur.close()
    db.close()
    
    return render_template('product.html', product=product_info, stores=stores, is_favorite=is_favorite)

# البحث
@app.route('/search')
def search():
    query = request.args.get('q', '')
    
    if not query:
        return redirect(url_for('home'))
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    user_id = session.get('user_id')
    cur.execute("""
        SELECT p.*, c.name as category_name,
        (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price,
        EXISTS(SELECT 1 FROM favorites WHERE user_id = %s AND product_id = p.id) as is_favorite
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.name LIKE %s OR p.description LIKE %s
    """, (user_id, f'%{query}%', f'%{query}%'))
    products = cur.fetchall()
    
    cur.close()
    db.close()
    
    return render_template('search.html', products=products, query=query)

# API للبحث المباشر
@app.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    
    if not query or len(query) < 2:
        return jsonify([])
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    cur.execute("""
        SELECT p.id, p.name, c.name as category_name,
        (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.name LIKE %s
        LIMIT 5
    """, (f'%{query}%',))
    results = cur.fetchall()
    
    cur.close()
    db.close()
    
    return jsonify(results)

# تسجيل الدخول
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        
        db = get_db()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()
        db.close()

        # التأكد من مطابقة الهاش
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin'] # تأكد من تخزين هذه في السيشن
            flash('تم تسجيل الدخول بنجاح', 'success')
            return redirect(url_for('home'))
        else:
            flash('خطأ في اسم المستخدم أو كلمة المرور', 'danger')
            
    return render_template('login.html')

# التسجيل
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # استخدام strip() هنا ضروري جداً لإزالة أي مسافات مخفية
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password').strip()
        
        # تشفير كلمة المرور
        hashed_password = generate_password_hash(password)
        
        db = get_db()
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                       (username, email, hashed_password))
            db.commit()
            flash('تم إنشاء الحساب بنجاح! جرب تسجيل الدخول الآن', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('اسم المستخدم أو الإيميل مستخدم مسبقاً', 'danger')
        finally:
            cur.close()
            db.close()
            
    return render_template('register.html')

@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    username = request.form.get('username').strip()
    email = request.form.get('email').strip()
    
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    try:
        cur.execute("SELECT id FROM users WHERE (username = %s OR email = %s) AND id != %s", 
                   (username, email, session['user_id']))
        if cur.fetchone():
            flash('اسم المستخدم أو البريد الإلكتروني مستخدم بالفعل', 'danger')
        else:
            cur.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", 
                       (username, email, session['user_id']))
            db.commit()
            session['username'] = username
            flash('تم تحديث البيانات بنجاح', 'success')
    except Exception as e:
        flash('حدث خطأ أثناء التحديث', 'danger')
    finally:
        cur.close()
        db.close()
        
    return redirect(url_for('profile'))

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        # استخدام strip() لمنع مشاكل المسافات
        old_password = request.form.get('old_password').strip()
        new_password = request.form.get('new_password').strip()
        confirm_password = request.form.get('confirm_password').strip()

        if new_password != confirm_password:
            flash('كلمات المرور الجديدة غير متطابقة', 'danger')
            return redirect(url_for('change_password'))

        db = get_db()
        cur = db.cursor(dictionary=True)
        
        # جلب بيانات المستخدم الحالي
        cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()

        if user and check_password_hash(user['password'], old_password):
            new_hashed = generate_password_hash(new_password)
            cur.execute("UPDATE users SET password = %s WHERE id = %s", (new_hashed, session['user_id']))
            db.commit()
            flash('تم تغيير كلمة المرور بنجاح', 'success')
            return redirect(url_for('profile'))
        else:
            flash('كلمة المرور القديمة غير صحيحة', 'danger')
        
        cur.close()
        db.close()
        
    return render_template('change_password.html')


# تسجيل الخروج
@app.route('/logout')
def logout():
    session.clear()
    flash('تم تسجيل الخروج بنجاح', 'success')
    return redirect(url_for('home'))

# الملف الشخصي
@app.route('/profile')
@login_required
def profile():
    db = get_db()
    cur = db.cursor(dictionary=True)
    
    cur.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    
    # عدد المنتجات المفضلة
    cur.execute("SELECT COUNT(*) as count FROM favorites WHERE user_id = %s", (session['user_id'],))
    favorites_count = cur.fetchone()['count']
    
    cur.close()
    db.close()
    
    return render_template('profile.html', user=user, favorites_count=favorites_count)

# المفضلة
@app.route('/favorites')
@login_required
def favorites():
    db = get_db()
    cur = db.cursor(dictionary=True)
    user_id = session['user_id']
    
    cur.execute("""
        SELECT p.*, 
        (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price
        FROM products p
        JOIN favorites f ON p.id = f.product_id
        WHERE f.user_id = %s
    """, (user_id,))
    
    favorites_list = cur.fetchall()
    cur.close()
    db.close()
    return render_template('favorites.html', favorites=favorites_list)

# إضافة/إزالة من المفضلة
@app.route('/toggle_favorite/<int:product_id>', methods=['GET', 'POST'])
@login_required
def toggle_favorite(product_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    user_id = session['user_id']

    # فحص هل هو موجود؟
    cur.execute("SELECT * FROM favorites WHERE user_id = %s AND product_id = %s", (user_id, product_id))
    if cur.fetchone():
        cur.execute("DELETE FROM favorites WHERE user_id = %s AND product_id = %s", (user_id, product_id))
        flash('تمت الإزالة من المفضلة', 'info')
    else:
        cur.execute("INSERT INTO favorites (user_id, product_id) VALUES (%s, %s)", (user_id, product_id))
        flash('تمت الإضافة للمفضلة', 'success')
    
    db.commit() # <--- تأكد من وجود هذا السطر ضروري جداً!
    cur.close()
    db.close()
    return redirect(request.referrer or url_for('home'))

# لوحة الإدارة
@app.route('/admin')
@login_required
def admin_panel():
    if not session.get('is_admin'):
        flash("غير مسموح لك بالدخول هنا!", "danger")
        return redirect(url_for('home'))

    db = get_db()
    cur = db.cursor(dictionary=True)
    
    # جلب الفئات والمتاجر
    cur.execute("SELECT * FROM categories ORDER BY name")
    categories = cur.fetchall()
    cur.execute("SELECT * FROM stores ORDER BY name")
    stores = cur.fetchall()
    
    # جلب المنتجات مع أقل سعر
    cur.execute("""
        SELECT p.*, c.name as category_name,
        (SELECT MIN(price) FROM product_stores WHERE product_id = p.id) as min_price
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        ORDER BY p.id DESC
    """)
    products = cur.fetchall()
    
    # الإحصائيات
    products_count = len(products)
    stores_count = len(stores)
    categories_count = len(categories)

    cur.close()
    db.close()
    
    return render_template('admin.html', 
                         products=products, 
                         categories=categories, 
                         stores=stores,
                         products_count=products_count,
                         stores_count=stores_count,
                         categories_count=categories_count)
# إضافة فئة
@app.route('/admin/add_category', methods=['POST'])
@login_required
def add_category():
    name = request.form.get('name')
    icon = request.form.get('icon')
    
    db = get_db()
    cur = db.cursor()
    
    cur.execute("INSERT INTO categories (name, icon) VALUES (%s, %s)", (name, icon))
    db.commit()
    
    cur.close()
    db.close()
    
    flash('تم إضافة الفئة بنجاح', 'success')
    return redirect(url_for('admin_panel'))

# إضافة متجر
@app.route('/admin/add_store', methods=['POST'])
@login_required
def add_store():
    name = request.form.get('name')
    logo = request.form.get('logo')
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO stores (name, logo) VALUES (%s, %s)", (name, logo))
    db.commit()
    cur.close()
    db.close()
    flash('تم إضافة المتجر بنجاح', 'success')
    return redirect(url_for('admin_panel'))

@app.route('/admin/edit/<int:product_id>')
def edit_product(product_id):
    db = get_db()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM products WHERE id = %s", (product_id,))
    product = cur.fetchone()
    cur.execute("SELECT * FROM categories ORDER BY name")
    categories = cur.fetchall()
    cur.close()
    db.close()
    return render_template('edit_product.html', product=product, categories=categories)

# إضافة منتج
@app.route('/admin/add_product', methods=['POST'])
@login_required
def add_product():
    name = request.form.get('name')
    description = request.form.get('description')
    category_id = request.form.get('category_id')
    image = request.form.get('image')
    has_discount = 1 if request.form.get('has_discount') else 0
    
    db = get_db()
    cur = db.cursor()
    
    cur.execute("""
        INSERT INTO products (name, description, category_id, image, has_discount)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, description, category_id, image, has_discount))
    db.commit()
    
    cur.close()
    db.close()
    
    flash('تم إضافة المنتج بنجاح', 'success')
    return redirect(url_for('admin_panel'))

# تحديث منتج
@app.route('/admin/update_product/<int:product_id>', methods=['POST'])
@login_required
def update_product(product_id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))   

    # جلب البيانات الجديدة من فورم التعديل
    name = request.form.get('name')
    image = request.form.get('image')
    description = request.form.get('description')
    category_id = request.form.get('category_id')

    db = get_db()
    cur = db.cursor()
    
    try:
        # تحديث بيانات المنتج الأساسية
        cur.execute("""
            UPDATE products 
            SET name=%s, image=%s, description=%s, category_id=%s 
            WHERE id=%s
        """, (name, image, description, category_id, product_id))
        
        db.commit()
        flash('تم تحديث بيانات المنتج بنجاح!', 'success')
    except Exception as e:
        flash(f'حدث خطأ: {str(e)}', 'danger')
    finally:
        cur.close()
        db.close()
        
    return redirect(url_for('admin_panel'))

# حذف منتج
@app.route('/admin/delete_product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if not session.get('is_admin'):
        return redirect(url_for('home'))

    db = get_db()
    cur = db.cursor()
    try:
        # حذف الارتباطات أولاً لتجنب مشاكل Foreign Key
        cur.execute("DELETE FROM favorites WHERE product_id = %s", (product_id,))
        cur.execute("DELETE FROM product_stores WHERE product_id = %s", (product_id,))
        cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
        db.commit()
        flash('تم حذف المنتج وكل بياناته بنجاح', 'warning')
    except Exception as e:
        flash(f'خطأ أثناء الحذف: {str(e)}', 'danger')
    finally:
        cur.close()
        db.close()
    return redirect(url_for('admin_panel'))
# إضافة سعر منتج في متجر

@app.route('/admin/add_product_store', methods=['POST'])
@login_required
def add_product_store():
    # جلب البيانات من الفورم
    product_id = request.form.get('product_id')
    store_id = request.form.get('store_id')
    price = request.form.get('price')
    old_price = request.form.get('old_price')
    product_url = request.form.get('product_url') # رابط الشراء
    shipping = request.form.get('shipping', 'مجاني')
    
    # التحقق من المدخلات الرقمية لتجنب خطأ DataError
    if not price:
        flash('السعر الحالي مطلوب', 'danger')
        return redirect(url_for('admin_panel'))
    
    # تحويل النص الفارغ إلى None ليعتبر NULL في قاعدة البيانات
    if not old_price or old_price.strip() == '':
        old_price = None

    db = get_db()
    cur = db.cursor()
    cur.execute("""
        INSERT INTO product_stores (product_id, store_id, price, old_price, product_url, shipping)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE price=%s, old_price=%s, product_url=%s, shipping=%s
    """, (product_id, store_id, price, old_price, product_url, shipping, price, old_price, product_url, shipping))
    db.commit()
    cur.close()
    db.close()
    flash('تم إضافة السعر والرابط بنجاح', 'success')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)