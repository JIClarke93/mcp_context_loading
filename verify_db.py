"""Quick script to verify database schema."""

from sqlalchemy import create_engine, inspect

from rdb.config import settings

engine = create_engine(settings.database_url, echo=False)
inspector = inspect(engine)

print("Database Tables:")
print("=" * 50)
for table_name in inspector.get_table_names():
    print(f"\n{table_name.upper()}")
    print("-" * 50)
    for column in inspector.get_columns(table_name):
        nullable = "NULL" if column["nullable"] else "NOT NULL"
        print(f"  {column['name']:20s} {str(column['type']):20s} {nullable}")

    # Show indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print("\n  Indexes:")
        for idx in indexes:
            cols = ", ".join(idx["column_names"])
            unique = "UNIQUE" if idx["unique"] else ""
            print(f"    {idx['name']}: ({cols}) {unique}")

    # Show foreign keys
    fks = inspector.get_foreign_keys(table_name)
    if fks:
        print("\n  Foreign Keys:")
        for fk in fks:
            print(f"    {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

print("\n" + "=" * 50)
print(f"Total tables: {len(inspector.get_table_names())}")
