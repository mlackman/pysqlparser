from ply import yacc
import lexer


tokens = lexer.tokens
precedence = (
)

def p_table_definition(p):
  """table_definition : CREATE TABLE table_name LPAREN column_definitions RPAREN SEMICOLON
                      | CREATE TABLE IF NOT EXISTS table_name LPAREN column_definitions RPAREN SEMICOLON"""
  if len(p) == 8:
    p[0] = (p[1].upper(), p[2].upper(), p[3], p[5])
  else:
    p[0] = (p[1].upper(), p[2].upper(), p[6], p[8])

def p_table_name(p):
  """table_name : IDENTIFIER
                | schema_table_name"""

  if isinstance(p[1], dict):
    p[0] = p[1]
  else:
    p[0] = dict(table_name=p[1])

def p_schema_table_name(p):
  """schema_table_name : schema DOT table_name"""
  p[1].update(p[3])
  p[0] = p[1]

def p_schema(p):
  """schema : IDENTIFIER"""
  p[0] = dict(schema=p[1])

def p_column_definitions(p):
  """column_definitions : column_definition
                        | column_definition_with_primary_key
                        | primary_key_definition
                        | column_definition COMMA column_definitions"""
  if len(p) == 2:
    p[0] = (p[1])
  else:
    p[0] = p[1], p[3]

def p_column_defintion_with_primary_key(p):
  """column_definition_with_primary_key : column_definition PRIMARY KEY
                                        | column_definition PRIMARY KEY COMMA column_definitions
  """
  if len(p) == 4:
    p[1]['primary_key'] = True
    p[0] = p[1]
  else:
    p[1]['primary_key'] = True
    p[0] = p[1], p[5]


def p_column_definition(p):
  """column_definition : IDENTIFIER data_type"""
  d = dict(column_name=p[1])
  d.update(p[2])
  p[0] = d

def p_primary_key_definition(p):
  """primary_key_definition : PRIMARY KEY LPAREN IDENTIFIER RPAREN"""
  p[0] = dict(primary_key=p[4])

def p_data_type(p):
  """data_type : type
               | type LPAREN NUMBER RPAREN
  """
  if len(p) == 2:
    p[0] = p[1]
  else:
    p[1]['length'] = p[3]
    p[0]=p[1]

def p_type(p):
  """type : IDENTIFIER"""
  p[0] = dict(type = p[1])

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
  print(parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char, age int, PRIMARY KEY(name));'))
  print(parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char, age int PRIMARY KEY);'))
  print(parser.parse('CREATE TABLE IF NOT EXISTS prh.jee (name char PRIMARY KEY, age int);'))

