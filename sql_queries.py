ALL_CATEGORIES = "SELECT * FROM product_category"
ALL_STORES = "SELECT * FROM stores"
ALL_PRODUCTS = "SELECT p.ID, p.Name, p.Category, p.UUID, ps.ID, ps.URL, pc.Name, s.Name FROM products AS p LEFT JOIN product_stores AS ps ON p.ID = ps.`Product ID` LEFT JOIN product_category AS pc ON pc.ID = p.Category LEFT JOIN stores AS s ON s.ID = ps.`Store ID`"
ALL_USERS = "SELECT `Name`, `User ID` FROM users WHERE `status` = 1"
ALL_REVIEWS = "SELECT pr.ID, pr.Title, pr.Content, pr.`Thumbs Up`, pr.`Thumbs Down`,pr.Rate, pr.Approved, pr.`Writer Name`, pr.`Writer Position`, p.Name AS `Product Name`, s.Name AS `Store Name`, ps.URL AS `Product Store URL` FROM product_reviews AS pr LEFT JOIN products AS p ON pr.`Product ID` = p.ID LEFT JOIN stores AS s ON pr.`Product Store ID` = s.ID LEFT JOIN product_stores AS ps ON ps.`Store ID` = s.ID AND pr.`Product ID` = ps.`Product ID`"

ALL_USER_STATUES = "SELECT * FROM user_status"
ALL_USER_ROLES = "SELECT * FROM user_roles"
ALL_PRODUCTS_NAMES = "SELECT * FROM products"
ALL_USERS_TABLE = "SELECT u.Name, u.`User ID` as 'userID', u.`Display Name` as 'displayName', u.Name, u.Status as 'userStatusValue', us.Status AS 'userStatusText', u.`User Role` as 'userRoleValue', ur.`Role Name` AS 'userRoleText', u.Age FROM users AS u LEFT JOIN user_status AS us ON u.Status = us.ID LEFT JOIN user_roles AS ur ON ur.ID = u.`User Role`"

ALL_OPEN_TICKETS = "SELECT t.*, ts.Status AS 'StatusName', tc.Name AS 'CategoryName', u.Name AS 'CreatorName' FROM tickets AS t LEFT JOIN ticket_status AS ts ON t.Status = ts.ID LEFT JOIN ticket_category AS tc ON t.Category = tc.ID LEFT JOIN users AS u ON t.`Created By` = u.`User ID` WHERE t.`Status` != 1"

ALL_TEMPLATES = "SELECT * FROM templates"

ALL_USERS_WIDGET = "SELECT COUNT(DISTINCT(u.`User ID`)) AS `Count`,ur.`Role Name` FROM users AS u LEFT JOIN user_roles AS ur ON ur.ID = u.`User Role` GROUP BY u.`User Role`"

ALL_SYSTEM_NOTES_BY_DATE = "SELECT DATE(`Log Date`) AS grouped_date, COUNT(*) AS total_records FROM system_notes GROUP BY grouped_date;"
ALL_SYSTEM_NOTES_BY_FUNC = "SELECT Action, COUNT(*) AS total_records FROM system_notes GROUP BY Action;"
ALL_SYSTEM_NOTES_BY_USER = "SELECT COUNT(*) AS total_records, u.Name FROM system_notes as l LEFT JOIN users as u ON u.`USER ID` = l.`USER ID` GROUP BY l.`User ID`;"

EXPORT_PRODUCT_CSV_QUERY = "SELECT p.ID, p.Name, p.Category, p.UUID, ps.ID, ps.URL, pc.Name, s.Name FROM products AS p LEFT JOIN product_stores AS ps ON p.ID = ps.`Product ID` LEFT JOIN product_category AS pc ON pc.ID = p.Category LEFT JOIN stores AS s ON s.ID = ps.`Store ID`"
EXPORT_REVIEW_CSV_QUERY = "SELECT pr.ID, pr.Title, pr.Content, pr.`Product ID` as `Product ID`, pr.`Thumbs Up`, pr.`Thumbs Down`,pr.Rate, pr.Approved, pr.`Writer Name`, pr.`Writer Position`, p.Name AS `Product Name`, s.Name AS `Store Name`, ps.URL AS `Product Store URL` FROM product_reviews AS pr LEFT JOIN products AS p ON pr.`Product ID` = p.ID LEFT JOIN stores AS s ON pr.`Product Store ID` = s.ID LEFT JOIN product_stores AS ps ON ps.`Store ID` = s.ID AND pr.`Product ID` = ps.`Product ID`"

def new_user_query(logged_in_user, user_info):
    """ This returns the query for creating a new user (int, obj) -> str
    logged_in_user is User ID of loggedin user and can be null
    user_info is an object contains name, display_name, age, user_role, token and user_status
    """
    name = user_info['name']
    display_name = user_info['display_name']
    age = user_info['age']
    user_role = user_info['user_role']
    token = user_info['token']
    user_status = user_info['user_status']
    return f"INSERT INTO users (`Name`,`Display Name`,`Age`, `User Role`, `User Token`, `Created By`, `Status`) VALUES('{name}','{display_name}', {age}, {user_role}, '{token}', {logged_in_user}, {user_status})"

def update_user_query_from_id(logged_in_user, user_id, user_info):
    """ This returns the query for creating a new user (int, obj) -> str
    logged_in_user is User ID of loggedin user and can be null
    user_info is a object contains name, display_name, age, user_role, token and user_status
    """
    name = user_info['name']
    display_name = user_info['display_name']
    age = user_info['age']
    user_role = user_info['user_role']    
    user_status = user_info['user_status']
    return f"UPDATE `flask_testing_db`.`users` SET `Name` = '{name}',  `Display Name` = '{display_name}',  `Age` = '{age}',    `User Role` = '{user_role}',    `Status` = '{user_status}',  `Created By` = '{logged_in_user}' WHERE `User ID` = '{user_id}'"

def get_user_query_from_id(id):
    return f"SELECT u.Name, u.`Active Template ID` as `Template`, u.`User ID` as 'userID', u.`Display Name` as 'displayName', u.Name, u.Status as 'userStatusValue', us.Status AS 'userStatusText', u.`User Role` as 'userRoleValue', ur.`Role Name` AS 'userRoleText', u.Age FROM users AS u LEFT JOIN user_status AS us ON u.Status = us.ID LEFT JOIN user_roles AS ur ON ur.ID = u.`User Role` WHERE u.`User ID` = {id}"

def get_user_query_from_token(token):
    return f"SELECT u.Name, u.`User ID` as 'userID', u.`Display Name` as 'displayName', u.Name, u.Status as 'userStatusValue', us.Status AS 'userStatusText', u.`User Role` as 'userRoleValue', ur.`Role Name` AS 'userRoleText', u.Age FROM users AS u LEFT JOIN user_status AS us ON u.Status = us.ID LEFT JOIN user_roles AS ur ON ur.ID = u.`User Role` WHERE u.`User Token` = '{token}'"

def get_product_from_id(id):
    return f"SELECT p.ID, p.Name, p.Category, p.UUID, ps.`Store ID` AS StoreID, s.Name, ps.URL, ps.ID AS `psID` FROM products AS p LEFT JOIN product_stores AS ps ON p.ID = ps.`Product ID` LEFT JOIN stores AS s ON s.ID = ps.`Store ID` WHERE p.ID = {id}"

def get_review_from_id(id):
    return f"SELECT pr.`ID`,`Title`,`Content`,pr.`Product ID`,`Product Store ID`, pr.`Created Date`,`Rate`,`Approved`,`Writer Name`,`Writer Position`,`Thumbs Up`,`Thumbs Down`,`Writer User ID`,ps.`Store ID` AS `StoreID`,s.Name AS 'Store Name', ps.URL FROM `flask_testing_db`.`product_reviews` AS pr LEFT JOIN `product_stores` AS ps ON `Product Store ID` = ps.ID LEFT JOIN `users` AS u ON pr.`Writer User ID` = u.`User ID` LEFT JOIN `stores` AS s ON ps.`Store ID` = s.ID WHERE pr.ID = {id}"

def get_product_stores_info_from_pid(pid):
    return f"SELECT ps.*, s.Name AS 'Store Name' FROM  product_stores AS ps LEFT JOIN stores AS s ON ps.`Store ID` = s.ID WHERE `Product ID` = {pid}"

def new_review_query(review_info, logged_in_user_id=None):
    ''''''        
    cmd = f"INSERT INTO `flask_testing_db`.`product_reviews` (`Title`,`Content`,`Product ID`,`Product Store ID`,`Rate`,`Approved`, `Writer Name`, `Writer Position`, `Thumbs Up`, `Thumbs Down`, `Writer User ID`) VALUES ('{review_info['title']}', '{review_info['content']}', {review_info['product_id']}, {review_info['product_store_id']}, {review_info['rate']}, 0, '{review_info['writer_name']}', '{review_info['writer_position']}', '{review_info['thumbs_up']}', '{review_info['thumbs_down']}', {logged_in_user_id})"
    
    if review_info['product_store_id'] == 'None' or logged_in_user_id is None:
        return cmd.replace('None', 'NULL')
    
    return cmd

def update_review_from_id(review_info, review_id, logged_in_user_id=None):
    ''''''    
    cmd = f"UPDATE `flask_testing_db`.`product_reviews` SET `Title` = '{review_info['title']}',`Content` = '{review_info['content']}',`Product ID` = {review_info['product_id']},`Product Store ID` = {review_info['product_store_id']},`Rate` = {review_info['rate']}, `Writer Name` = '{review_info['writer_name']}', `Writer Position` = '{review_info['writer_position']}', `Thumbs Up` = {review_info['thumbs_up']}, `Thumbs Down` = {review_info['thumbs_down']}, `Writer User ID` = {logged_in_user_id} WHERE `ID` = {review_id}"

    if review_info['product_store_id'] == 'None' or logged_in_user_id is None:
        return cmd.replace('None', 'NULL')
    
    return cmd
def get_ticket_from_id(id):
    return f"SELECT t.*, ts.Status AS 'StatusName', tc.Name AS 'CategoryName', u.Name AS 'CreatorName' FROM tickets AS t LEFT JOIN ticket_status AS ts ON t.Status = ts.ID LEFT JOIN ticket_category AS tc ON t.Category = tc.ID LEFT JOIN users AS u ON t.`Created By` = u.`User ID` WHERE t.`ID` = {id}"

def get_messages_from_id(tid, type):
    created_from = 1 if type == "ticket" else 2
    return f"SELECT m.*, u.Name as 'CreatorName' FROM messages AS m LEFT JOIN users AS u ON m.`Created By` = u.`User ID` WHERE `Created From` = {created_from} AND `Related Record ID` = {tid}"

def new_message_query(message_info):
    ''''''
    return f"INSERT INTO `flask_testing_db`.`messages`(`Title`,`Content`,`Created By`,`Created From`,`Related Record ID`) VALUES ('{message_info['Title']}','{message_info['Content']}','{message_info['Created By']}', {message_info['Created From']}, {message_info['Related Record ID']})"

def mark_ticket_solved(tid):
    return f"UPDATE `flask_testing_db`.`tickets` SET `Status` = 1 WHERE `ID` = {tid}"

def get_product_tags_from_pid(pid):
    return f"SELECT GROUP_CONCAT(tags.`tag name`) AS 'tags' FROM product_tags LEFT JOIN tags ON `tag id` = tags.ID WHERE `product id` = {pid}"

def search_products(name="", rate="", tags=[]):
    '''Return sql query for search products(str, list)->list'''
    tag_str = ""
    for t in tags:
        tag_str += 't.`Tag Name` = "' + t + '" OR '

    tag_str = tag_str[:-4]
    
    search_criteria = []

    where_statement = ""
    if name != "":
        search_criteria.append(f" p.name LIKE '%{name}%' ")
    
    if len(tags) != 0:
        search_criteria.append(tag_str)
    
    having_statement = ""
    having_criteria = []
    if rate != "":
        having_criteria.append(f" overall_rate > {rate} ")

    if len(having_criteria) != 0:
        having_statement = " HAVING " + (" AND ").join(having_criteria)

    if len(search_criteria) != 0:
        where_statement = " WHERE " + (" AND ").join(search_criteria)
        
    return f"SELECT p.ID, p.Name, GROUP_CONCAT(DISTINCT(t.`Tag Name`)) AS tags, CONVERT(COUNT(pr.Title) / (CASE WHEN COUNT(DISTINCT(t.`Tag Name`)) = 0 THEN 1 ELSE COUNT(DISTINCT(t.`Tag Name`)) END),SIGNED) AS number_of_reviews, AVG(pr.rate) AS overall_rate FROM products p LEFT JOIN product_reviews pr ON p.ID = pr.`Product ID` LEFT JOIN product_tags pt ON p.ID = pt.`Product ID` LEFT JOIN tags t ON pt.`Tag ID` = t.ID {where_statement} GROUP BY p.ID {having_statement} ORDER BY number_of_reviews DESC;"

def get_reviews_from_pid(pid):
    return f"SELECT pr.ID, pr.Title, pr.Content, pr.`Thumbs Up`, pr.`Thumbs Down`,pr.Rate, pr.Approved, pr.`Writer Name`, pr.`Writer Position`, p.Name AS `Product Name`, s.Name AS `Store Name`, ps.URL AS `Product Store URL` FROM product_reviews AS pr LEFT JOIN products AS p ON pr.`Product ID` = p.ID LEFT JOIN stores AS s ON pr.`Product Store ID` = s.ID LEFT JOIN product_stores AS ps ON ps.`Store ID` = s.ID AND pr.`Product ID` = ps.`Product ID` WHERE p.ID = {pid}"

def get_review_summary_from_pid(pid):
    return f"SELECT p.ID, p.Name, GROUP_CONCAT(DISTINCT(t.`Tag Name`)) AS tags, CONVERT(COUNT(pr.Title) / (CASE WHEN COUNT(DISTINCT(t.`Tag Name`)) = 0 THEN 1 ELSE COUNT(DISTINCT(t.`Tag Name`)) END),SIGNED) AS number_of_reviews, AVG(pr.rate) AS overall_rate FROM products p LEFT JOIN product_reviews pr ON p.ID = pr.`Product ID` LEFT JOIN product_tags pt ON p.ID = pt.`Product ID` LEFT JOIN tags t ON pt.`Tag ID` = t.ID WHERE p.ID = {pid} GROUP BY p.ID ORDER BY number_of_reviews DESC;"

def get_product_id_from_puid(puid):
    return f"SELECT id FROM products WHERE UUID = '{puid}'"

def get_templates_from_uid(uid):
    return f"SELECT * FROM templates WHERE `Created By` = {uid}"

def new_template_query(tid, name, content, user_id):
    # return f"INSERT INTO `flask_testing_db`.`templates` (`Name`,`Created By`,`Content`) VALUES ('{name}','{user_id}','{content}');"
    return f"INSERT INTO `templates`(`ID`,`Name`, `Created By`, `Content`) VALUES ({tid}, '{name}', {user_id},'{content}' ) ON DUPLICATE KEY UPDATE `Name`='{name}', `Content` = '{content}'"

def get_template_from_tid(tid):
    return f"SELECT * from templates WHERE ID = {tid}"

def get_system_notes_func_by_user(uid):
    return f"SELECT Action, COUNT(*) AS total_records FROM system_notes WHERE `USER ID` = {uid} GROUP BY Action;"
if __name__ == "__main__":
    print(search_products("pt"))