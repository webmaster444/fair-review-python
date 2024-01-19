VERSION = 1.0
API_VERSION = 'v1'

MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWORD = ''
MYSQL_DB = 'flask_testing_db'
APP_SECRET_KEY = 'Z);y4(6e1UK6'
API_TOKEN_PREFIX = "TEST_"
DEFAULT_USER_ROLE = 2
DEFAULT_USER_STATUS = 1
SESSION_TYPE = 'filesystem'
SESSION_SECRET_KEY = 'Z);y4(6e1UK6'
PRODUCT_UUID_PREFIX = "PDT_"
USER_ROLES = {
    'ADMIN': 1,
    'FREE': 2,
    'PREMIUM': 3,
    'ENTERPRISE': 4,
    'SHOP_OWNER':5
}

DEFAULT_CSS = '''

'''

DEFAULT_TEMPLATE_HTML = '''
<div class="fr-review-wrapper"><div class="fr-review-summary-wrapper">{{AuthorName}} - {{AuthorJob}} - {{OverallRate}} - {{NumberOfReviews}}</div><div></div></div>
'''

CSV_IMPORTABLE_RECORD_TYPES = ["Product","Review"]

UPLOAD_FOLDER = "F:\\Working\\Python\\Flask\\uploads"

### This is for Import/Export CSV
CSV_PRODUCT_COLUMNS = [{"label": "Name","slug":"productName", "required": True},{"label": "ID","slug":"productID","required": False},{"label": "Category","slug":"productCategory","required": True},{"label":"Store Name","slug":"productStoreName", "required":False },{"label":"Store URL","slug":"productStoreURL", "required":False}]
CSV_REVIEWS_COLUMNS = [{"label":"Title","slug":"reviewTitle", "required":True},{"label":"Content","slug":"reviewContent","required":False},{"label":"Rate","slug":"reviewRate","required":True},{"label":"Thumbs Up","slug":"reviewThumbsUp","required":True},{"label":"Thumbs Down","slug":"reviewThumbsDown","required":True},{"label":"Writer Name","slug":"reviewWriterName","required":True},{"label":"Writer Position","slug":"reviewWriterPosition","required":False},{"label":"Product ID","slug":"reviewProductID","required":False}, {"label":"ID","slug":"reviewID","required":False}, {"label":"Product Name","slug":"reviewProductName","required":True}, {"label":"Store Name","slug":"reviewStoreName", "required":False}, {"label":"Product URL","slug":"reviewProductURL", "required":False}]
