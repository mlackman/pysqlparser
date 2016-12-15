from pysqlparser.ply import yacc
from pysqlparser import lexer
import collections


class Table(object):

  def __init__(self, name=None, schema=None):
    self.name = name
    self.schema = schema
    self._columns = []

  @property
  def columns(self):
    return self._columns

  @property
  def fullname(self):
    if self.schema:
      return "{schema}.{table_name}".format(schema=self.schema, table_name=self.name)
    else:
      return self.name

  @columns.setter
  def columns(self,column_or_columns):
    if isinstance(column_or_columns, collections.Iterable):
      self._columns.extend(column_or_columns)
    else:
      self._columns.append(column_or_columns)
    # HAXOR
    self._set_columns_with_primary_key_info(self._columns)

  def add_column(self, name, data_type, is_primary_key=None, references=None):
    self._columns.append(Column(name, is_primary_key, data_type, references))

  def _set_columns_with_primary_key_info(self, column_definitions):
    primary_keys = []
    foreign_keys = []
    self._columns, primary_keys, foreign_keys = self._filter_columns_primary_keys_and_foreign_keys(column_definitions)

    self._update_primary_key_info_to_columns(primary_keys)
    self._update_foreign_key_info_to_columns(foreign_keys)


  def _filter_columns_primary_keys_and_foreign_keys(self, column_definitions):
    columns =      filter(lambda col_def: not self._is_primary_or_foreign_key(col_def), column_definitions)
    primary_keys = filter(lambda col_def: isinstance(col_def, PrimaryKey), column_definitions)
    foreign_keys = filter(lambda col_def: isinstance(col_def, ForeignKey), column_definitions)
    return list(columns), primary_keys, foreign_keys

  def _is_primary_or_foreign_key(self, column_definition):
    return isinstance(column_definition, PrimaryKey) or isinstance(column_definition, ForeignKey)

  def _update_primary_key_info_to_columns(self, primary_keys):
    for primary_key in primary_keys:
      for column in self._columns:
        if column.name == primary_key.column_name:
          column.is_primary_key = True

  def _update_foreign_key_info_to_columns(self, foreign_keys):
    for foreign_key in foreign_keys:
      for column in self._columns:
        if column.name == foreign_key.column_name:
          column.references.append(foreign_key.reference)

  def __str__(self):
    columns_str = ', '.join([str(column) for column in self._columns])
    d = self.__dict__
    d['columns_str'] = columns_str
    if self.schema:
      return 'table: {schema}.{name} columns: {columns_str}'.format(**d)
    else:
      return 'table: {name} columns: {columns_str}'.format(**d)

class Column(object):

  def __init__(self, name=None, is_primary_key=None, data_type=None, references=None):
    self.name = name
    self.data_type = data_type
    self.is_primary_key = is_primary_key or False
    self.references = references or []

  def __str__(self):
    return '[Column: name: {name} type: {data_type}, primary key: {is_primary_key}, is_foreign_key: {is_foreign_key}]'.format(**self.__dict__)

  @property
  def is_foreign_key(self):
    return self.references != []

class DataType(object):

  def __init__(self, type=None, length=None):
    self.type = type
    self.length = length

  def __str__(self):
    return self.type if self.length == None else self.type + '(' + str(self.length) + ')'

class Reference(object):

  def __init__(self, table_name, columns):
    self.table_name = table_name
    self.columns = columns

class PrimaryKey(object):
  """Helper class to parse bnf"""

  def __init__(self, name):
    self.column_name = name

class ForeignKey(object):

  def __init__(self, column_name, reference):
    self.column_name = column_name
    self.reference = reference

tokens = lexer.tokens

def p_table_definitions(p):
  """table_definitions : table_definition
                       | table_definition table_definitions"""
  table_definitions = []
  if len(p) > 2:
    table_definitions.extend(p[2])
  table_definitions.append(p[1])
  p[0] = table_definitions

def p_table_definition(p):
  """table_definition : CREATE TABLE table_name LPAREN column_definitions RPAREN SEMICOLON
                      | CREATE TABLE IF NOT EXISTS table_name LPAREN column_definitions RPAREN SEMICOLON"""

  if len(p) == 8:
    table = p[3]
    table.columns = p[5]
    p[0] = table
  else:
    table = p[6]
    table.columns = p[8]
    p[0] = table

def p_table_name(p):
  """table_name : IDENTIFIER
                | schema DOT IDENTIFIER"""

  table = Table()
  if len(p) == 4:
    table.schema = p[1]
    table.name = p[3]
  else:
    table.name = p[1]
  p[0] = table

def p_schema(p):
  """schema : IDENTIFIER"""
  p[0] = p[1]

def p_column_definitions(p):
  """column_definitions : column_definition
                        | primary_key_definition
                        | foreign_key_definition
                        | column_definition COMMA column_definitions"""
  if isinstance(p[1], PrimaryKey) or isinstance(p[1], ForeignKey):
    p[0] = p[1]
  elif len(p) == 2: # column_definition
    p[0] = p[1]
  else:
    if isinstance(p[3], collections.Iterable) and not isinstance(p[3], str):
      p[3].append(p[1])
      p[0] = p[3]
    else:
      p[0] = [p[3],p[1]]

def p_column_definition(p):
  """column_definition : IDENTIFIER data_type
                       | IDENTIFIER data_type reference_definition
                       | IDENTIFIER data_type PRIMARY KEY
  """
  column = Column(name=p[1], data_type=p[2])
  if len(p) >= 4:
    if isinstance(p[3], Reference):
      column.references.append(p[3])
    else:
      column.is_primary_key = True
  p[0] = column

def p_primary_key_definition(p):
  """primary_key_definition : PRIMARY KEY LPAREN IDENTIFIER RPAREN"""
  p[0] = PrimaryKey(p[4])

def p_reference_definition(p):
  """reference_definition : REFERENCES table_name LPAREN column_name_list RPAREN
                          | REFERENCES table_name"""
  table = p[2]
  columns = [] if len(p) == 3 else p[4]
  p[0] = Reference(table.fullname, columns)

def p_foreign_key_definition(p):
  """foreign_key_definition : FOREIGN KEY LPAREN IDENTIFIER RPAREN reference_definition"""
  foreign_key = ForeignKey(p[4], p[6])
  p[0] = foreign_key

def p_column_name_list(p):
  """column_name_list : IDENTIFIER
                      | IDENTIFIER COMMA column_name_list
  """
  column_names = [p[1]]
  if len(p) > 2:
    column_names.extend(p[3])
  p[0] = column_names

def p_data_type(p):
  """data_type : type
               | type LPAREN NUMBER RPAREN
  """
  if len(p) != 2:
    data_type = p[1]
    data_type.length = p[3]
  p[0] = p[1]

def p_type(p):
  """type : IDENTIFIER"""
  p[0] = DataType(type=p[1])

def p_error(p):
  print(p)
  print("Syntax error in input!")


parser = yacc.yacc(debug=True)


def parse(data):
  parser = yacc.yacc(debug=True)
  return parser.parse(data)

if __name__ == '__main__':
  print(parser.parse('create TABLE jee (name char);'))
  print(parser.parse('CREATE TABLE prh.jee (name varchar(256));'))
  print(parser.parse('CREATE TABLE prh.jee (name varchar(256), id int, code char);'))
  print(parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char, age int, PRIMARY KEY(name));'))
  print(parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char, age int PRIMARY KEY);'))
  print(parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char PRIMARY KEY, age int);'))

