from pysqlparser import ddlparser as parser


def assert_table(table, table_name, schema, column_count, columns):
  assert table.name == table_name
  assert table.schema == schema
  assert len(table.columns), column_count
  for index, expected_column in enumerate(columns):
    column_name, data_type, length, is_primary_key = expected_column
    column = table.columns[index]
    assert column.name == column_name
    assert column.data_type.type == data_type
    assert column.data_type.length == length
    assert column.is_primary_key == is_primary_key



def test_parsing_1():
  table = parser.parse('create TABLE jee (name char);')
  assert_table(table, table_name='jee', schema=None, column_count=1, columns=(('name', 'char', None, False),))

def test_parsing_2():
  table = parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char, age int, PRIMARY KEY(name));')
  assert_table(table, table_name='jee', schema='prh', column_count=2, columns=(('age', 'int', None, False), ('name', 'char', None, True) ))

def test_parsing_3():
  table = parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char, age int PRIMARY KEY);')
  assert_table(table, table_name='jee', schema='prh', column_count=2, columns=(('age', 'int', None, True), ('name', 'char', None, False)))

def test_parsing_4():
  table = parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name varchar(20) PRIMARY KEY, age int);')
  assert_table(table, table_name='jee', schema='prh', column_count=2, columns=(('name', 'varchar', 20, True),('age', 'int', None, False)))

