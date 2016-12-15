from pysqlparser.ddlparser import DataType


def test_formatting_data_type_without_lenght():
  d = DataType(type='char')
  assert str(d) == 'char'

def test_formatting_data_type_with_length():
  d = DataType(type='char', length=10)
  assert str(d) == 'char(10)'




