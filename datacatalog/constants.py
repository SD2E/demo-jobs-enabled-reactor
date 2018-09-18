from uuid import uuid3, NAMESPACE_DNS

DNS_FOR_NAMESPACE = 'sd2e.org'
UUID_NAMESPACE = uuid3(NAMESPACE_DNS, DNS_FOR_NAMESPACE)
STORAGE_ROOT = 'uploads/'

class Constants():
    DNS_FOR_NAMESPACE = 'sd2e.org'
    MOCK_DNS_FOR_NAMESPACE = 'sd2e.club'
    UUID_NAMESPACE = uuid3(NAMESPACE_DNS, DNS_FOR_NAMESPACE)
    UUID_MOCK_NAMESPACE = uuid3(NAMESPACE_DNS, MOCK_DNS_FOR_NAMESPACE)
    STORAGE_ROOT = 'uploads/'
    PRODUCTS_ROOT = 'products'
    ABACO_HASHIDS_SALT = 'eJa5wZlEX4eWU'
    MOCK_IDS_SALT = '97JFXMGWBDaFWt8a4d9NJR7z3erNcAve'
    JOBS_TOKEN_SALT = '3MQXA&jk/-![^7+3'
class Enumerations():
    LABPATHS = ('ginkgo', 'transcriptic', 'biofab', 'emerald')
    LABNAMES = ('Ginkgo', 'Transcriptic', 'UW_BIOFAB', 'Emerald')
    CHALLENGE_PROBLEMS = ('yeast-gates', 'novel-chassis')

class Mappings():
    LABPATHS = {'ginkgo': 'Ginkgo', 'transcriptic': 'Transcriptic', 'biofab': 'UW_BIOFAB', 'emerald': 'Emerald'}
