from flask import Flask, jsonify, render_template, request, redirect, url_for, session, make_response
from functools import wraps
from flask_mysqldb import MySQL
import config as cfg
import MySQLdb
import string
import secrets
import sql_queries as sql
import json
from random import randint
import re
import html
from flask_cors import CORS
import os
import csv
import io

app = Flask(__name__, static_url_path='', static_folder='web/assets',template_folder='web/templates')

app.config['MYSQL_HOST'] = cfg.MYSQL_HOST
app.config['MYSQL_USER'] = cfg.MYSQL_USER
app.config['MYSQL_PASSWORD'] = cfg.MYSQL_PASSWORD
app.config['MYSQL_DB'] = cfg.MYSQL_DB
app.secret_key = cfg.SESSION_SECRET_KEY
app.config['SESSION_TYPE'] = cfg.SESSION_TYPE
mysql = MySQL(app)

app.config['FILE_UPLOADS'] = cfg.UPLOAD_FOLDER
CORS(app)

# # Decorator for API key authentication
def require_api_key(view_function):
    @wraps(view_function)    
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-Key")
        user_obj = get_user_obj(api_key)
        if api_key and user_obj:
            # role/permission check     
            print('permission checked')       
            result = view_function(user_obj, *args, **kwargs)
            # add systems notes and logs
            add_log(user_obj, view_function.__name__)
            return result
        else:
            return jsonify({"error": "Unauthorized"}), 401
    return decorated_function

# Decorator for Logged in
def logged_in(f):
    @wraps(f)
    def decorated_func(*args, **kwargs):
        if session.get("logged_in"):
            add_log({'id':session.get('user_id')}, f.__name__)
            return f(*args, **kwargs)
        else:
            return redirect("/login")
    return decorated_func

def get_user_obj(api_key):
    cmd = sql.get_user_query_from_token(api_key)
    rv = run_mysql_command(cmd, one_row=True)
    print(rv)
    if rv is None or len(rv) == 0:
        return False    
    return {'id': rv['userID'], 'name': rv['Name'], 'role':rv['userRoleValue'], 'roleText':rv['userRoleText']}

@app.route('/')
def page_index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def page_login():    
    if request.method == "GET":
        return render_template('login.html')
    else:        
        api_key = request.form.get('api_key')
        user_obj = get_user_obj(api_key)
        if api_key and user_obj:            
            # add systems notes and logs
            add_log(user_obj, 'logged in')
            session['logged_in'] = True
            session['user_id'] = user_obj['id']
            session['user_name'] = user_obj['name']
            session['user_role'] = user_obj['role']
            session['user_role_text'] = user_obj['roleText']
            return redirect(url_for("admin_page_dashboard"))            
        else:
            return jsonify({"error": "Unauthorized"}), 401


@app.route('/admin/dashboard/', methods=['GET'])
@logged_in
def admin_page_dashboard():
    # Get User Data
    users = run_mysql_command(sql.ALL_USERS_WIDGET)
    tickets = run_mysql_command(sql.ALL_OPEN_TICKETS)
    logs_by_date = run_mysql_command(sql.ALL_SYSTEM_NOTES_BY_DATE)    
    logs_by_func = run_mysql_command(sql.ALL_SYSTEM_NOTES_BY_FUNC)       
    return render_template('admin/dashboard.html', users=json.dumps(users), tickets=tickets, logs=json.dumps(logs_by_date, default=str), logs_by_func=json.dumps(logs_by_func))

@app.route('/admin/error', methods=['GET'], defaults={'err':None})
@app.route('/admin/error/<err>', methods=['GET'])
@logged_in
def admin_page_error(err):
    return render_template('admin/error.html', err=err)

@app.route('/admin/api_usages/', methods=['GET'])
@logged_in
def admin_page_api_usages():
    logs_by_date = run_mysql_command(sql.ALL_SYSTEM_NOTES_BY_DATE)    
    logs_by_func = run_mysql_command(sql.ALL_SYSTEM_NOTES_BY_FUNC)   
    logs_by_user = run_mysql_command(sql.ALL_SYSTEM_NOTES_BY_USER)   
    logs_by_user = run_mysql_command(sql.ALL_SYSTEM_NOTES_BY_USER)   
    uid = session.get('user_id')
    logs_by_func_user = run_mysql_command(sql.get_system_notes_func_by_user(uid))
    return render_template('admin/api_usages.html', logs=json.dumps(logs_by_date, default=str), logs_by_func=json.dumps(logs_by_func), logs_by_user=json.dumps(logs_by_user), user_name = session.get('user_name'), logs_by_func_user=json.dumps(logs_by_func_user))

@app.route('/admin/users/', methods=['GET', 'POST'])
@logged_in
def admin_page_users():    
    if request.method == "GET":
        users = {}        
        cmd = sql.ALL_USERS_TABLE
        users = run_mysql_command(cmd)
        return render_template('admin/users.html', users=users)
    else:
        return render_template('admin/users.html')
    
@app.route('/admin/account_settings/', methods=['GET', 'POST'])
@logged_in
def admin_page_account_settings():    
    if request.method == "GET":
        user = {}
        user_id = session.get('user_id')

        cmd = sql.get_user_query_from_id(user_id)
        user = run_mysql_command(cmd, False, True)

        templates = run_mysql_command(sql.ALL_TEMPLATES)
        return render_template('admin/account_settings.html', user=user, templates=templates)
    else:
        return render_template('admin/account_settings.html')
    
@app.route('/admin/account/delete/', methods=['GET', 'POST'], defaults={'id':None})
@app.route('/admin/account/delete/<id>', methods=['GET', 'POST'])
@logged_in
def admin_page_delete_account(id):    
    if request.method == "GET":        
        if id is None:
            user_id = session.get('user_id')        
        else:
            user_id = id
        return render_template('admin/account_delete.html', userID=user_id)
    else:        
        user_id = request.form.get('userID')
        new_status = randint(1,4)
        sql = f"UPDATE `flask_testing_db`.`users` SET `Status` = {new_status} WHERE `User ID` = {user_id}"
        user = run_mysql_command(sql)

        return redirect(url_for('admin_page_account_settings'))
    
@app.route('/admin/user/', methods=['GET', 'POST'], defaults={'id':None})
@app.route('/admin/user/<id>', methods=['GET', 'POST'])
@logged_in
def admin_page_user(id):    
    if request.method == "GET":        
        logged_in_user_id = session.get('user_id')        
        user = {}
        statuses = run_mysql_command(sql.ALL_USER_STATUES)
        roles = run_mysql_command(sql.ALL_USER_ROLES)
        if id is not None:
            cmd = sql.get_user_query_from_id(id)
            user = run_mysql_command(cmd, insert_cmd=False, one_row=True)

            if user is None:
                return redirect(url_for('admin_page_user', id=None))
        return render_template('admin/user.html', userID=logged_in_user_id, user=user, userStatuses=statuses, userRoles=roles)
    else:        
        logged_in_user_id = session.get('user_id')        
        user_id = request.form.get('userID')
        name = request.form.get('userName')
        display_name = request.form.get('displayName')
        age = request.form.get('Age')
        user_role = request.form.get('userRoles')
        user_status = request.form.get('userStatus')        
        token = cfg.API_TOKEN_PREFIX + generate_random_string(30)
        if user_id is None or user_id == '':                
            _create_new_user(logged_in_user_id, {'name':name, 'display_name': display_name, 'token': token, 'age': age, 'user_role':user_role, 'user_status':user_status}, request_from='admin')        
        else:
            _update_user(logged_in_user_id, user_id, {'name':name, 'display_name': display_name, 'token': token, 'age': age, 'user_role':user_role, 'user_status':user_status}, request_from='admin')

        return redirect(url_for('admin_page_users'))
    
@app.route('/admin/account/upgrade/', methods=['GET', 'POST'])
@logged_in
def admin_page_upgrade_account():    
    if request.method == "GET":
        user = {}
        user_id = session.get('user_id')
        sql = f"SELECT u.Name, u.`User ID` as 'userID', u.`Display Name` as 'displayName', u.Name, u.Status as 'userStatusValue', us.Status AS 'userStatusText', u.`User Role` as 'userRoleValue', ur.`Role Name` AS 'userRoleText', u.Age FROM users AS u LEFT JOIN user_status AS us ON u.Status = us.ID LEFT JOIN user_roles AS ur ON ur.ID = u.`User Role` WHERE u.`User ID` = {user_id}"
        user = run_mysql_command(sql, False, True)
        return render_template('admin/account_upgrade.html', user=user)
    else:
        user_id = request.form.get('userID')
        new_role = randint(1,4)
        sql = f"UPDATE `flask_testing_db`.`users` SET `User Role` = {new_role} WHERE `User ID` = {user_id}"        
        user = run_mysql_command(sql)
    
        return redirect(url_for('admin_page_account_settings'))

@app.route('/admin/reviews/', methods=['GET', 'POST'], defaults={'pid':None})
@app.route('/admin/reviews/<pid>', methods=['GET', 'POST'])
@logged_in
def admin_page_reviews(pid):
    if request.method == "GET":
        reviews = []

        products = run_mysql_command(sql.ALL_PRODUCTS_NAMES)

        if pid is None:
            reviews_db_res = run_mysql_command(sql.ALL_REVIEWS)        
            if reviews_db_res is not None and len(reviews_db_res) != 0:
                for res in reviews_db_res:            
                    reviews.append({
                        "ID": res["ID"],
                        "Title": res["Title"],
                        "Content": res["Content"],
                        "Rate": res["Rate"],
                        "Approved": False if res["Approved"] == 0 else True,
                        "UpVote": res["Thumbs Up"],
                        "DownVote": res["Thumbs Down"],
                        "Writer Name": res["Writer Name"],
                        "Writer Position": res["Writer Position"],
                        "Product Name": res["Product Name"],
                        "Product URL": res["Product Store URL"],
                        "Store Name": res["Store Name"]
                    })
        else:
            reviews_db_res = run_mysql_command(sql.get_reviews_from_pid(pid))        
            if reviews_db_res is not None and len(reviews_db_res) != 0:
                for res in reviews_db_res:            
                    reviews.append({
                        "ID": res["ID"],
                        "Title": res["Title"],
                        "Content": res["Content"],
                        "Rate": res["Rate"],
                        "Approved": False if res["Approved"] == 0 else True,
                        "UpVote": res["Thumbs Up"],
                        "DownVote": res["Thumbs Down"],
                        "Writer Name": res["Writer Name"],
                        "Writer Position": res["Writer Position"],
                        "Product Name": res["Product Name"],
                        "Product URL": res["Product Store URL"],
                        "Store Name": res["Store Name"]
                    })
        return render_template('admin/reviews.html', reviews=reviews, pid=pid, products=products)
    else:
        pid = request.form.get('productID')
        return redirect(url_for('admin_page_reviews', pid=pid))
    

@app.route('/admin/templates/', methods=['GET'])
@logged_in
def admin_page_templates():
    if request.method == "GET":        
        
        user_role = session.get('user_role')
        user_id = session.get('user_id')
        if user_role == 1:
            templates = run_mysql_command(sql.ALL_TEMPLATES)        
        else:
            templates = run_mysql_command(sql.get_templates_from_uid(user_id))
        return render_template('admin/templates.html', templates=templates)

@app.route('/admin/template', methods=['GET', 'POST'], defaults={'tid':None})
@app.route('/admin/template/<tid>', methods=['GET', 'POST'])
@logged_in
def admin_page_template(tid):
    if request.method == "GET":
        template = {}
        if tid is None:
            template['Content'] = cfg.DEFAULT_TEMPLATE_HTML
        else:
            template = run_mysql_command(sql.get_template_from_tid(tid), one_row=True)
        return render_template('admin/template.html', template=template)    
    else:
        name = request.form.get('templateName')
        content = request.form.get('templateContent')
        tid = request.form.get('templateID')
        run_mysql_command(sql.new_template_query(tid, name, content, session.get('user_id')), insert_cmd=True)
        return redirect(url_for('admin_page_templates'))


@app.route('/admin/stores/', methods=['GET'])
@logged_in
def admin_page_stores():
    stores = run_mysql_command(sql.ALL_STORES)
    users = run_mysql_command(sql.ALL_USERS)
    return render_template('admin/stores.html', stores=stores, users=users)

@app.route('/admin/import-csv/', methods=['GET','POST'])
@logged_in
def admin_page_csv_import():
    if request.method == "GET":
        return render_template('admin/csvimport.html', rec_types=cfg.CSV_IMPORTABLE_RECORD_TYPES)
    else:
        data = []
        rec_type_selected = request.form.get('recordType')        
        columns = []
        if rec_type_selected == "Product":
            columns = cfg.CSV_PRODUCT_COLUMNS
        elif rec_type_selected == "Review":
            columns = cfg.CSV_REVIEWS_COLUMNS            
        csv_data_columns = []    
        if request.files:
            uploaded_file = request.files['filename'] # This line uses the same variable and worked fine
            filepath = os.path.join(app.config['FILE_UPLOADS'], uploaded_file.filename)
            uploaded_file.save(filepath)
            with open(filepath) as file:
                csv_file = csv.reader(file)
                for idx, row in enumerate(csv_file):
                    if idx == 0:
                        csv_data_columns = row
                    data.append(row)               


        return render_template('admin/csvimport2.html', csv_data_columns=csv_data_columns, columns=columns, rec_types=cfg.CSV_IMPORTABLE_RECORD_TYPES, data=data, rec_type_selected=rec_type_selected)

@app.route('/admin/post/import-csv/', methods=["POST"])
@logged_in
def admin_post_csv_import():
    if request.form.get('recordType') == "Product":
        print("import products")
    elif request.form.get('recordType') == "Review":
        print("import reviews")
    return redirect(url_for('admin_page_csv_import'))
    

@app.route('/admin/tickets/', methods=['GET', 'POST'])
@logged_in
def admin_page_tickets():    
    tickets = run_mysql_command(sql.ALL_OPEN_TICKETS)
    return render_template('admin/tickets.html', tickets=tickets)

@app.route('/admin/post/mark-ticket-solved/<id>', methods=['POST'])
@logged_in
def admin_post_mark_solved(id):
    run_mysql_command(sql.mark_ticket_solved(id))
    return redirect(url_for('admin_page_tickets'))

@app.route('/admin/post/export-csv/', methods=['POST'])
@logged_in
def admin_post_csv_export():
    recordType = request.form.get('recordType')
    columns = []
    csvList = []
    if recordType == "Product":
        columns = cfg.CSV_PRODUCT_COLUMNS
        all_products_db_res = run_mysql_command(sql.EXPORT_PRODUCT_CSV_QUERY)

        csvList.append([p['label'] for p in columns])

        for product in all_products_db_res:
            csvList.append([product['Name'], product['ID'], product['pc.Name'],product['s.Name'], product['URL']])   
    else:
        columns = cfg.CSV_REVIEWS_COLUMNS
        all_review_db_res = run_mysql_command(sql.EXPORT_REVIEW_CSV_QUERY)

        csvList.append([p['label'] for p in columns])

        for review in all_review_db_res:            
            csvList.append([review['Title'], review['Content'], review['Rate'],review['Thumbs Up'], review['Thumbs Down'], review['Writer Name'], review['Writer Position'], review['Product ID'], review['Product Name'], review['Store Name'], review['Product Store URL']])   

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerows(csvList)
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=export.csv"
    output.headers["Content-type"] = "text/csv"
    return output     

@app.route('/admin/post/write-message', methods=['POST'])
@logged_in
def admin_post_write_message():
    title = request.form.get('messageTitle')
    content = request.form.get('messageContent')
    created_by = session.get('user_id')
    created_from = request.form.get('messageType') #Ticket        
    related_rec_id = request.form.get('relatedRecID')
    run_mysql_command(sql.new_message_query({'Title':title, 'Content':content, 'Created By':created_by, 'Created From':created_from, 'Related Record ID':related_rec_id}), insert_cmd=True)
    
    if created_from is 1 or created_from is '1':
        return redirect(url_for('admin_page_ticket', id=related_rec_id))
    else:
        return redirect(url_for('admin_page_review', id=related_rec_id))

@app.route('/admin/ticket/<id>', methods=['GET'])
@logged_in
def admin_page_ticket(id):   
    if request.method == "GET":
        ticket = run_mysql_command(sql.get_ticket_from_id(id), one_row=True)
        messages = run_mysql_command(sql.get_messages_from_id(id, 'ticket'))
        return render_template('admin/ticket.html', ticket=ticket, messages=messages)

@app.route('/admin/review/', methods=['GET', 'POST'])
@logged_in
def admin_page_review():    
    p_id = request.args.get('pid')
    review_id = request.args.get('id')
    logged_in_user_id = session.get('user_id')        
    if request.method == "GET":
        if p_id is None and review_id is None:
            return redirect(url_for('admin_page_reviews'))
        product = {}        

        review = {}
        if review_id is not None:
            review = run_mysql_command(sql.get_review_from_id(review_id), one_row=True)

        if not p_id:
            p_id = review['Product ID']
        
        product = run_mysql_command(sql.get_product_from_id(p_id), one_row=True)

        product_stores = run_mysql_command(sql.get_product_from_id(p_id))        
        products = run_mysql_command(sql.ALL_PRODUCTS_NAMES)
        
        messages = run_mysql_command(sql.get_messages_from_id(review_id, 'review'))
        return render_template('admin/review.html', product=product, review=review, product_stores=product_stores, products=products, messages=messages)
    else:
        review_id = request.form.get('reviewID')        
        product_id = request.form.get('reviewProduct')
        product_store_id = request.form.get('reviewProductStore')
        title = request.form.get('reviewTitle')
        content = request.form.get('reviewContent')
        rate = request.form.get('reviewRate')
        thumbs_up = request.form.get('reviewThumbsUp') or 0
        thumbs_down = request.form.get('reviewThumbsDown') or 0
        writer_name = request.form.get('reviewWriterName')
        writer_position = request.form.get('reviewWriterPosition')

        if review_id is None or review_id == '':
            '''Insert new review'''
            run_mysql_command(sql.new_review_query({'title':title, 'content':content, 'rate':rate, 'thumbs_up':thumbs_up, 'thumbs_down':thumbs_down, 'writer_name':writer_name, 'writer_position':writer_position, 'product_id':product_id, 'product_store_id':product_store_id}, logged_in_user_id), insert_cmd=True)
        else:
            '''Update current review'''            
            run_mysql_command(sql.update_review_from_id({'title':title, 'content':content, 'rate':rate, 'thumbs_up':thumbs_up, 'thumbs_down':thumbs_down, 'writer_name':writer_name, 'writer_position':writer_position, 'product_id':product_id, 'product_store_id':product_store_id}, review_id, logged_in_user_id))
        return redirect(url_for('admin_page_reviews'))

@app.route('/admin/filters', methods=['GET', 'POST'])
@logged_in
def admin_page_filters():
    if request.method == "GET":                
        return render_template('admin/filters.html', filter={}, results={}, no_filter=True)
    else:        
        name = request.form.get('filterName')

        rate = request.form.get('filterRate')
        tags_str = request.form.get('filterTags')
        
        tags = [fruit.strip() for fruit in tags_str.split(',')]
        if tags_str.strip() == "":
            tags = []

        results = run_mysql_command(sql.search_products(name, rate, tags=tags))        
        return render_template('admin/filters.html', filter={'name':name, 'rate':rate, 'tags':tags_str}, results=results, no_filter=False)

@app.route('/admin/store', methods=['GET', 'POST'], defaults={'id':None})
@app.route('/admin/store/<id>', methods=['GET', 'POST'])
@logged_in
def admin_page_store(id):
    if request.method == "GET":
        store = {}
        if id is not None:
            store = run_mysql_command(f"SELECT * FROM stores WHERE ID = {id}", one_row=True)

        users = run_mysql_command(sql.ALL_USERS)

        if store is None:
            return redirect(url_for('admin_page_store'))
        
        return render_template('admin/store.html', store=store, users=users)
    else:        
        store_id = request.form.get('storeID')

        store_name = request.form.get('storeName')
        store_url = request.form.get('storeURL')
        store_location = request.form.get('storeLocation')
        store_owner = request.form.get('storeOwner')

        logged_in_user = session.get('user_id')        
        if not store_id:
            run_mysql_command(f"INSERT INTO stores (`Name`, `Owner`, `Created By`, `Location`, `URL`) VALUES ('{store_name}', {store_owner}, {logged_in_user}, '{store_location}', '{store_url}')", insert_cmd=True)
        else:
            run_mysql_command(f"UPDATE stores SET `Name` = '{store_name}', `Owner` = {store_owner}, `Created By` = {logged_in_user}, `Location` = '{store_location}', `URL` = '{store_url}' WHERE `ID` = {store_id}")
        return redirect(url_for('admin_page_stores'))

@app.route('/admin/products/', methods=['GET'])
@logged_in
def admin_page_products():
    
    rv = run_mysql_command(sql.ALL_PRODUCTS)
    
    product_none = False
    if rv is None or len(rv) == 0:
        product_none = True
    
    products = []

    unique_product_ids = []
    for record in rv:        
        product_id = record['ID']
        product_name = record['Name']
        product_uuid = record['UUID']
        product_store_name = record['s.Name']
        product_store_url = record['URL']
        product_category = record['Category']
        product_category_name = record['pc.Name']
        if not product_id in unique_product_ids:
            tmp = {
                "ID": product_id,
                "Name": product_name,
                "UUID": product_uuid,
                "Category Name": product_category_name,
                "Stores": [
                    {
                        "Store Name": product_store_name,
                        "Store URL": product_store_url
                    }
                ]
            }
            products.append(tmp)

            unique_product_ids.append(product_id)
        else:
            #get index for products and add store            
            i = get_index_from_products(product_id, products)
            products[i]['Stores'].append({
                "Store Name": product_store_name,
                "Store URL": product_store_url
            })        
    
    return render_template('admin/products.html', products=products, product_none=product_none)


@app.route('/admin/product', methods=['GET', 'POST'], defaults={'id':None})
@app.route('/admin/product/<id>', methods=['GET', 'POST'])
@logged_in
def admin_page_product(id):
    if request.method == "GET":        
        categories_db_res = run_mysql_command(sql.ALL_CATEGORIES)
        categories = []
        for res in categories_db_res:
            categories.append({
                "ID": res["ID"],
                "Name": res["Name"]
            })

        stores_db_res = run_mysql_command(sql.ALL_STORES)
        stores = []
        for res in stores_db_res:
            stores.append({
                "ID": res["ID"],
                "Name": res["Name"]
            })
        product = {}
        
        if id is not None:
            cmd = sql.get_product_from_id(id)
            
            product_db_res = run_mysql_command(cmd)

            product_tags = run_mysql_command(sql.get_product_tags_from_pid(id), one_row=True)

            if product_db_res is not None and len(product_db_res) != 0:
                product = {
                    "ID": id,
                    "Name": product_db_res[0]["Name"],
                    "Category": product_db_res[0]["Category"],
                    "Stores": [],
                    "StoreInfo": "",
                    "Tags": "" if product_tags['tags'] is None else product_tags['tags']
                }                
                for res in product_db_res:
                    if res['s.Name'] is not None:
                        product['Stores'].append({
                            'Store ID': res['StoreID'],
                            'Store Name': res['s.Name'],
                            'Store URL': res['URL'],
                            'psID': res['psID']
                        })
                        
                product['StoreInfo'] = json.dumps(product['Stores'], separators=(',', ":"))
            else:
                return redirect("/admin/product")
        return render_template('admin/product.html', product= product, categories=categories, stores=stores)
    else:        
        pn = request.form.get('productName')
        pc = request.form.get('productCategory')
        pid = request.form.get('productID')   
        user_id = session.get('user_id')
        pstoreStr = request.form.get('storeInfo')
        
        pStores = {}
        if pstoreStr:            
            pStores = json.loads(request.form.get('storeInfo'))        
        
        tags_string = request.form.get('productTags')

        # Use regular expression to find all occurrences of the 'value' attribute
        tags = tags_string.split(",")

        # Remove leading spaces from each match
        tags = [match.strip() for match in tags]

        # Join the matches into a comma-separated string                
        if pid is None or pid == '':
            _create_new_product(user_id, {}, request_from="admin")            
        else:
            '''Update Product and Product Stores table'''
            cmd = f"UPDATE `flask_testing_db`.`products` SET `Name` = '{pn}', `Category` = '{pc}' WHERE `ID` = {pid}"
            run_mysql_command(cmd)
            for store in pStores:
                if store['psID'] is None or store['psID'] == "":
                    cmd = f"INSERT INTO product_stores (`Product ID`,`Created By`,`Store ID`, `URL`) VALUES({pid}, {user_id}, {store['Store ID']}, '{store['Store URL']}')"    
                    run_mysql_command(cmd)
            
            ''' Insert Product Tags'''            
            run_mysql_command(f"DELETE FROM `flask_testing_db`.`product_tags` WHERE `ID` IN (SELECT ID FROM product_tags WHERE `Product ID` = {pid})")

            for tag in tags:
                check_cmd = f"SELECT id FROM tags WHERE `tag name` = '{tag}'"
                tagId = run_mysql_command(check_cmd, one_row=True)
                if not tagId:
                    cmd = f"INSERT INTO tags (`Tag Name`) VALUES ('{tag}');"
                    tagId = run_mysql_command(cmd, insert_cmd=True)
                else:
                    tagId = tagId['id']                
                
                cmd = f"INSERT INTO product_tags (`Tag ID`, `Product ID`) VALUES ({tagId}, {pid})"
                run_mysql_command(cmd)
                
        return redirect(url_for('admin_page_products'))

@app.route('/api/'+cfg.API_VERSION+'/hello', methods=['GET'])
@require_api_key
def api_hello(user_obj):
    return jsonify({'message': 'Hello, World!'})

@app.route('/api/'+cfg.API_VERSION+'/greet/<name>', methods=['GET'])
@require_api_key
def api_greet(user_obj, name):
    print('greet function called')
    return jsonify({'message': f'Hello, {name}!'})

@app.route('/api/' + cfg.API_VERSION + '/review/', methods=['GET', 'POST'])
@require_api_key
def api_get_reviews_from_puid(user_obj):
    if request.method == "GET":
        puid = request.args.get('puid')            
        reviews = []

        pid_res = run_mysql_command(sql.get_product_id_from_puid(puid), one_row=True)
        pid = pid_res['id']

        if pid is not None:            
            reviews_db_res = run_mysql_command(sql.get_reviews_from_pid(pid))        
            if reviews_db_res is not None and len(reviews_db_res) != 0:
                for res in reviews_db_res:            
                    reviews.append({
                        "ID": res["ID"],
                        "Title": res["Title"],
                        "Content": res["Content"],
                        "Rate": res["Rate"],
                        "Approved": False if res["Approved"] == 0 else True,
                        "UpVote": res["Thumbs Up"],
                        "DownVote": res["Thumbs Down"],
                        "Writer Name": res["Writer Name"],
                        "Writer Position": res["Writer Position"],
                        "Product Name": res["Product Name"],
                        "Product URL": res["Product Store URL"],
                        "Store Name": res["Store Name"]
                    })
            
            summary = run_mysql_command(sql.get_review_summary_from_pid(pid), one_row=True)
            # return ({'puid':puid, 'user_id':user_obj['id'], 'pid':pid, 'reviews':reviews, 'summary':summary})
            return _make_html_from_template(2, reviews=reviews, summary=summary)
        else:
            return ({'puid':puid, 'message':'Wrong puid'})
    else:
        pid = request.form.get('productID')
        return redirect(url_for('admin_page_reviews', pid=pid))
    
@app.route('/api/'+cfg.API_VERSION+'/new_user', methods=['POST'])
@require_api_key
def api_new_user(user_obj):            
    json_data = request.get_json()
    # json_data = json.loads(json_str)
    name, display_name, age = json_data['name'], json_data['display_name'], json_data['age']
            
    token = cfg.API_TOKEN_PREFIX + generate_random_string(30)
    
    user_role = cfg.DEFAULT_USER_ROLE
    user_status = cfg.DEFAULT_USER_STATUS
    
    _create_new_user(user_obj['id'], {name:name, display_name: display_name, 'token': token, age: age, user_role:user_role, user_status:user_status}, request_from='api')
    return jsonify({'message': f'New user named {name} added with {token}'})

@app.route('/api/'+cfg.API_VERSION+'/new_product', methods=['POST'])
@require_api_key
def api_new_product(user_obj):            
    json_data = request.get_json()
    # json_data = json.loads(json_str)
    name, category, stores = json_data['name'], json_data['category'], json_data['stores']
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    token = cfg.PRODUCT_UUID_PREFIX + generate_random_string(15)
            
    try:
        cursor.execute(''' SET sql_mode = 'STRICT_ALL_TABLES' ''')    

        # check whether category exists or not
        category_id = create_if_not_exist('product_category', 'Name', category, 'ID')

        cursor.execute(''' INSERT INTO products (`Name`,`Created By`,`Category`, `UUID`) VALUES(%s,%s, %s, %s)''', (name, user_obj['id'], category_id, token))    
        product_id = cursor.lastrowid
        
        for store in stores:
            cursor.execute(''' INSERT INTO product_stores (`Product ID`,`Created By`,`Name`, `URL`) VALUES(%s,%s, %s, %s)''', (product_id, user_obj['id'], store['name'], store['url']))    

        mysql.connection.commit()
    except MySQLdb.Error as e:
        print(type(e))
        return jsonify({'message':'sorry'})
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")
        return jsonify({'message': 'Sorry something went wrong'})
    finally:        
        cursor.close()            
    return jsonify({'message': f'New user named {name} added with {token}'})

@app.route('/api/'+cfg.API_VERSION+'/users', methods=['GET'])
@require_api_key
def api_all_users(user_obj):
    print('all users', user_obj)
    cursor = mysql.connection.cursor()
    cursor.execute(''' SELECT `Name`, `Display Name`, `Age` FROM users''')
    rv = cursor.fetchall()    
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({'message': f'Hello, {rv}!'})

@app.route('/api/'+cfg.API_VERSION+'/products', methods=['GET'])
@require_api_key
def all_products(user_obj):    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f"SELECT p.ID, p.Name, p.UUID, ps.Name, ps.URL FROM products AS p LEFT JOIN product_stores AS ps ON p.ID = ps.`Product ID`")
    rv = cursor.fetchall()    
    mysql.connection.commit()
    cursor.close()
    
    return jsonify({'message': f'Hello, {rv}!'})

def generate_random_string(length=12):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(secrets.choice(characters) for _ in range(length))
    return random_string

def add_log(user_obj, funcname):                
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)            
    user_id = user_obj['id']
    try:
        cursor.execute(''' SET sql_mode = 'STRICT_ALL_TABLES' ''')    
        cursor.execute(''' INSERT INTO system_notes (`User ID`,`Action`) VALUES(%s,%s)''', (user_id, funcname))    
        mysql.connection.commit()
    except MySQLdb.Error as e:
        print(e)        
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")        
    finally:        
        cursor.close()   

def create_if_not_exist(tablename, columnname, value, return_value):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    category_id = 0
    try:
        cursor.execute(''' SET sql_mode = 'STRICT_ALL_TABLES' ''')    
        cursor.execute(f"SELECT `{return_value}` FROM {tablename} WHERE `{columnname}` = '{value}'")
        rv = cursor.fetchone()
        print(rv)
        if rv is None or len(rv) == 0:            
            cursor.execute(f"INSERT INTO {tablename} (`{columnname}`) VALUES ('{value}')")
            category_id = cursor.lastrowid
        else:
            category_id = rv['ID']
        mysql.connection.commit()
    except MySQLdb.Error as e:
        print(e)        
    except Exception as err:
        print(f"Unexpected {err}, {type(err)}")        
    finally:        
        cursor.close()  
    return category_id

def get_index_from_products(id, array):
    for elm, i in enumerate(array):
        if i["ID"] == id:
            return elm
    return False

def run_mysql_command(cmd, insert_cmd=False, one_row=False):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    res = ""
    try:
        cursor.execute(''' SET sql_mode = 'STRICT_ALL_TABLES' ''')    
        cursor.execute(cmd)
        if insert_cmd:
            res = cursor.lastrowid
        else:
            if one_row:
                res = cursor.fetchone()
            else:
                res = cursor.fetchall()
    except Exception as err:                
        print(cmd)
        print(err)
    finally:        
        mysql.connection.commit()
        cursor.close()
    
    return res

@app.context_processor
def inject_user():
    return dict(logged_in_user={'user_id':session.get('user_id'), 'user_name':session.get('user_name'), 'user_role':session.get('user_role'), 'user_role_text':session.get('user_role_text')})

def _create_new_product(logged_in_user_id, product_info, request_from):
    print(product_info)
    ''' Insert A Product'''
    puid = cfg.PRODUCT_UUID_PREFIX + generate_random_string(15)
    
    cmd = f"INSERT INTO `flask_testing_db`.`products` (`Name`, `Created By`,`Category`, `UUID`) VALUES ('{pn}',{user_id},{pc}, '{puid}');"
    pid = run_mysql_command(cmd, insert_cmd=True)
    
    ''' Insert Product Store rows'''
    for store in pStores:                
        cmd = f"INSERT INTO product_stores (`Product ID`,`Created By`,`Store ID`, `URL`) VALUES({pid}, {user_id}, {store['Store ID']}, '{store['Store URL']}')"    
        run_mysql_command(cmd)

    ''' Insert Product Tags'''            
    for tag in tags:
        check_cmd = f"SELECT id FROM tags WHERE `tag name` = '{tag}'"
        tagId = run_mysql_command(check_cmd, one_row=True)
        if not tagId:
            cmd = f"INSERT INTO tags (`Tag Name`) VALUES ('{tag}');"
            tagId = run_mysql_command(cmd, insert_cmd=True)
        else:
            tagId = tagId['id']
        cmd = f"INSERT INTO product_tags (`Tag ID`, `Product ID`) VALUES ({tagId}, {pid})"
        run_mysql_command(cmd)

def _create_new_user(logged_in_user_id, user_info, request_from):    
    cmd = sql.new_user_query(logged_in_user_id, user_info)    
    run_mysql_command(cmd, insert_cmd=True)

def _update_user(logged_in_user_id, user_id, user_info, request_from):
    print(user_info)
    cmd = sql.update_user_query_from_id(logged_in_user_id, user_id, user_info)    
    run_mysql_command(cmd, insert_cmd=True)

def _make_html_from_template(tid, reviews=[], summary={}):
    template_db_res = run_mysql_command(sql.get_template_from_tid(tid), one_row=True)
    content_html = template_db_res['Content']

    content_html = content_html.replace("{{ProductName}}", str(summary['Name']))
    content_html = content_html.replace("{{OverallRate}}", str(summary['overall_rate']))
    content_html = content_html.replace("{{NumberOfReviews}}", str(summary['number_of_reviews']))
    return content_html
# @app.errorhandler(Exception)
# def handle_exception(e):
#     print(e)
#     return redirect(url_for('admin_page_error', err=e))

if __name__ == '__main__':
    app.run(debug=True)


