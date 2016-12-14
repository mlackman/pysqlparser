from collections import namedtuple
from pysqlparser import ddlparser as parser
from pysqlparser.ddlparser import Table


ExpectedColumn = namedtuple('ExpectedColumn', 'name type length is_primary_key is_foreign_key references')

def assert_table(table, table_name, schema, column_count, columns):
  assert table.name == table_name
  assert table.schema == schema
  assert len(table.columns), column_count

  for index, expected_column in enumerate(columns):
    column = table.columns[index]
    assert column.name == expected_column.name
    assert column.data_type.type == expected_column.type
    assert column.data_type.length == expected_column.length
    assert column.is_primary_key == expected_column.is_primary_key

def test_parsing_1():
  table = parser.parse('create TABLE jee (name char);')

  assert_table(table, table_name='jee', schema=None, column_count=1, columns=(ExpectedColumn('name', 'char', None, False, False, None),))

def test_parsing_2():
  table = parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char, age int, PRIMARY KEY(name));')
  assert_table(table, table_name='jee', schema='prh', column_count=2,
      columns=(ExpectedColumn('age', 'int', None, False, False, None), ExpectedColumn('name', 'char', None, True, False, None) ))

def test_parsing_3():
  table = parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char, age int PRIMARY KEY);')
  assert_table(table, table_name='jee', schema='prh', column_count=2,
      columns=(ExpectedColumn('age', 'int', None, True, False, None),ExpectedColumn('name', 'char', None, False, False, None)))

def test_parsing_4():
  table = parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name varchar(20) PRIMARY KEY, age int);')
  assert_table(table, table_name='jee', schema='prh', column_count=2,
      columns=(ExpectedColumn('age', 'int', None, False, False, None), ExpectedColumn('name', 'varchar', 20, True, False, None)))

def test_parsing_foreign_key_1():
  table = parser.parse("""
    CREATE TABLE IF NOT EXISTS prh.jee (name varchar(20) references prh.sometable (id));
  """)
  references = table.columns[0].references
  assert len(references) == 1
  reference = references[0]
  assert reference.table_name == 'prh.sometable'
  assert len(reference.columns) == 1
  assert reference.columns[0] == 'id'

def test_parsing_foreign_key_2():
  table = parser.parse("""
    CREATE TABLE IF NOT EXISTS prh.jee (
      name varchar(20) references prh.sometable (id),
      postcode char
    );
  """)
  references = table.columns[1].references
  assert len(references) == 1
  reference = references[0]
  assert reference.table_name == 'prh.sometable'
  assert len(reference.columns) == 1
  assert reference.columns[0] == 'id'
  assert len(table.columns) == 2

def test_parsing_foreign_key_with_column_name_list():
  table = parser.parse("""
    CREATE TABLE IF NOT EXISTS prh.jee (
      name varchar(20) references prh.sometable (id, od, ed)
    );
  """)
  references = table.columns[0].references
  assert len(references) == 1
  reference = references[0]
  assert reference.table_name == 'prh.sometable'
  assert len(reference.columns) == 3
  assert reference.columns == ['id', 'od', 'ed']
  assert len(table.columns) == 1




