# Si mysqlclient no se pudo instalar (común en Windows), se usa PyMySQL como alternativa.
try:
    import MySQLdb  # noqa: F401
except ImportError:
    try:
        import pymysql
        pymysql.version_info = (2, 2, 1, 'final', 0)
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
