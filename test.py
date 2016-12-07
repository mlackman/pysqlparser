import ddlparser as parser


def test_parsing():
  assert parser.parse('create TABLE jee (name char);') == ('CREATE', 'TABLE', {'table_name':'jee'}, (('column_name', 'name'), ('data_type', 'char')))
  print(parser.parse('CREATE TABLE prh.jee (name varchar(256));'))
  print(parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char, age int, PRIMARY KEY(name));'))
  print(parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char, age int PRIMARY KEY);'))
  print(parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char PRIMARY KEY, age int);'))

