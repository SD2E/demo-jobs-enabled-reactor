class CatalogError(Exception):
    pass

class CatalogQueryError(CatalogError):
    # Errors making a query to the database or collection
    pass

class CatalogUpdateFailure(CatalogError):
    # Errors arising when the Data Catalog can't be updated
    pass


class CatalogDataError(CatalogError):
    # Errors arising from computing or validating metadata
    pass


class CatalogDatabaseError(CatalogError):
    # Errors reading to or writing from backing store
    pass
