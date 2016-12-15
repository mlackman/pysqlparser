from pysqlparser.ply import lex


tokens = [
  'IDENTIFIER',
  'DOT',
  'LPAREN',
  'RPAREN',
  'SEMICOLON',
  'NUMBER',
  'COMMA',
  'COMMENT',
]

t_DOT           = r'\.'
t_LPAREN        = r'\('
t_RPAREN        = r'\)'
t_SEMICOLON     = r';'
t_COMMA         = r','

reserved = {
  'create':'CREATE',
  'table':'TABLE',
  'if':'IF',
  'not':'NOT',
  'exists':'EXISTS',
  'primary':'PRIMARY',
  'key':'KEY',
  'references':'REFERENCES',
  'foreign':'FOREIGN'
}


tokens += list(reserved.values())

# Error handling rule
def t_error(t):
  print("Illegal character '%s'" % t.value[0])
  t.lexer.skip(1)

t_ignore  = ' \t\n'

def t_COMMENT(t):
  r'(/\*.*\*/)|(\#.*)|(--.*)' # ignore /* jee */
  pass

def t_NUMBER(t):
  r'\d+'
  t.value = int(t.value)
  return t

def t_IDENTIFIER(t):
  r'(?i)[a-z_0-9]+'
  t.type = reserved.get(t.value.lower(), 'IDENTIFIER')
  return t

# Build the lexer
lexer = lex.lex()

if __name__ == '__main__':

  data = """create table prh.company (id varchar(256), jee char(300));"""
  lexer.input(data)

  # Tokenize
  for token in lexer:
    print(token.type, token.value)

