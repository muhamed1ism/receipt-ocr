from sqlmodel import String, cast, col, func


def call_ilike(column, query: str):
    return column.ilike(f"%{query}%")


# Compare column string from db with query
def col_ilike(column, query: str):
    return call_ilike(col(column), query)


# Cast date to string and compare date column with query
def date_ilike(column, query: str):
    return call_ilike(func.to_char(column, "DD. MM. YYYY. HH24:MI:SS"), query)


# Cast column data to string and compare with query
def cast_ilike(column, query: str):
    return call_ilike(cast(column, String), query)


# Compare unaccent column string with unaccent query
def unaccent_ilike(column, query: str):
    return func.unaccent(column).ilike(func.unaccent(f"%{query}%"))
