# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: fleetspeak/src/osquery/proto/fleetspeak_osquery/osquery.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='fleetspeak/src/osquery/proto/fleetspeak_osquery/osquery.proto',
  package='fleetspeak.osquery',
  syntax='proto3',
  serialized_options=None,
  serialized_pb=_b('\n=fleetspeak/src/osquery/proto/fleetspeak_osquery/osquery.proto\x12\x12\x66leetspeak.osquery\"\xd9\x01\n\x0cLoggedResult\x12\x33\n\x04type\x18\x01 \x01(\x0e\x32%.fleetspeak.osquery.LoggedResult.Type\x12\x35\n\x08\x63ompress\x18\x02 \x01(\x0e\x32#.fleetspeak.osquery.CompressionType\x12\x0c\n\x04\x64\x61ta\x18\x03 \x01(\x0c\"O\n\x04Type\x12\x0b\n\x07UNKNOWN\x10\x00\x12\n\n\x06STRING\x10\x01\x12\x0c\n\x08SNAPSHOT\x10\x02\x12\n\n\x06HEALTH\x10\x03\x12\x08\n\x04INIT\x10\x04\x12\n\n\x06STATUS\x10\x05\"\xe5\x01\n\x07Queries\x12\x39\n\x07queries\x18\x01 \x03(\x0b\x32(.fleetspeak.osquery.Queries.QueriesEntry\x12=\n\tdiscovery\x18\x02 \x03(\x0b\x32*.fleetspeak.osquery.Queries.DiscoveryEntry\x1a.\n\x0cQueriesEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x1a\x30\n\x0e\x44iscoveryEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"`\n\x03Row\x12-\n\x03row\x18\x01 \x03(\x0b\x32 .fleetspeak.osquery.Row.RowEntry\x1a*\n\x08RowEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\"-\n\x04Rows\x12%\n\x04rows\x18\x01 \x03(\x0b\x32\x17.fleetspeak.osquery.Row\"w\n\x0cQueryResults\x12\x12\n\nquery_name\x18\x01 \x01(\t\x12\x0e\n\x06status\x18\x02 \x01(\x03\x12\x35\n\x08\x63ompress\x18\x03 \x01(\x0e\x32#.fleetspeak.osquery.CompressionType\x12\x0c\n\x04Rows\x18\x04 \x01(\x0c*5\n\x0f\x43ompressionType\x12\x10\n\x0cUNCOMPRESSED\x10\x00\x12\x10\n\x0cZCOMPRESSION\x10\x01\x62\x06proto3')
)

_COMPRESSIONTYPE = _descriptor.EnumDescriptor(
  name='CompressionType',
  full_name='fleetspeak.osquery.CompressionType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNCOMPRESSED', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ZCOMPRESSION', index=1, number=1,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=803,
  serialized_end=856,
)
_sym_db.RegisterEnumDescriptor(_COMPRESSIONTYPE)

CompressionType = enum_type_wrapper.EnumTypeWrapper(_COMPRESSIONTYPE)
UNCOMPRESSED = 0
ZCOMPRESSION = 1


_LOGGEDRESULT_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='fleetspeak.osquery.LoggedResult.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='UNKNOWN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STRING', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SNAPSHOT', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='HEALTH', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='INIT', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STATUS', index=5, number=5,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=224,
  serialized_end=303,
)
_sym_db.RegisterEnumDescriptor(_LOGGEDRESULT_TYPE)


_LOGGEDRESULT = _descriptor.Descriptor(
  name='LoggedResult',
  full_name='fleetspeak.osquery.LoggedResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='type', full_name='fleetspeak.osquery.LoggedResult.type', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='compress', full_name='fleetspeak.osquery.LoggedResult.compress', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='fleetspeak.osquery.LoggedResult.data', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _LOGGEDRESULT_TYPE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=86,
  serialized_end=303,
)


_QUERIES_QUERIESENTRY = _descriptor.Descriptor(
  name='QueriesEntry',
  full_name='fleetspeak.osquery.Queries.QueriesEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='fleetspeak.osquery.Queries.QueriesEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='fleetspeak.osquery.Queries.QueriesEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=439,
  serialized_end=485,
)

_QUERIES_DISCOVERYENTRY = _descriptor.Descriptor(
  name='DiscoveryEntry',
  full_name='fleetspeak.osquery.Queries.DiscoveryEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='fleetspeak.osquery.Queries.DiscoveryEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='fleetspeak.osquery.Queries.DiscoveryEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=487,
  serialized_end=535,
)

_QUERIES = _descriptor.Descriptor(
  name='Queries',
  full_name='fleetspeak.osquery.Queries',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='queries', full_name='fleetspeak.osquery.Queries.queries', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='discovery', full_name='fleetspeak.osquery.Queries.discovery', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_QUERIES_QUERIESENTRY, _QUERIES_DISCOVERYENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=306,
  serialized_end=535,
)


_ROW_ROWENTRY = _descriptor.Descriptor(
  name='RowEntry',
  full_name='fleetspeak.osquery.Row.RowEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='fleetspeak.osquery.Row.RowEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='fleetspeak.osquery.Row.RowEntry.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=591,
  serialized_end=633,
)

_ROW = _descriptor.Descriptor(
  name='Row',
  full_name='fleetspeak.osquery.Row',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='row', full_name='fleetspeak.osquery.Row.row', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_ROW_ROWENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=537,
  serialized_end=633,
)


_ROWS = _descriptor.Descriptor(
  name='Rows',
  full_name='fleetspeak.osquery.Rows',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='rows', full_name='fleetspeak.osquery.Rows.rows', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=635,
  serialized_end=680,
)


_QUERYRESULTS = _descriptor.Descriptor(
  name='QueryResults',
  full_name='fleetspeak.osquery.QueryResults',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='query_name', full_name='fleetspeak.osquery.QueryResults.query_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='status', full_name='fleetspeak.osquery.QueryResults.status', index=1,
      number=2, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='compress', full_name='fleetspeak.osquery.QueryResults.compress', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='Rows', full_name='fleetspeak.osquery.QueryResults.Rows', index=3,
      number=4, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=682,
  serialized_end=801,
)

_LOGGEDRESULT.fields_by_name['type'].enum_type = _LOGGEDRESULT_TYPE
_LOGGEDRESULT.fields_by_name['compress'].enum_type = _COMPRESSIONTYPE
_LOGGEDRESULT_TYPE.containing_type = _LOGGEDRESULT
_QUERIES_QUERIESENTRY.containing_type = _QUERIES
_QUERIES_DISCOVERYENTRY.containing_type = _QUERIES
_QUERIES.fields_by_name['queries'].message_type = _QUERIES_QUERIESENTRY
_QUERIES.fields_by_name['discovery'].message_type = _QUERIES_DISCOVERYENTRY
_ROW_ROWENTRY.containing_type = _ROW
_ROW.fields_by_name['row'].message_type = _ROW_ROWENTRY
_ROWS.fields_by_name['rows'].message_type = _ROW
_QUERYRESULTS.fields_by_name['compress'].enum_type = _COMPRESSIONTYPE
DESCRIPTOR.message_types_by_name['LoggedResult'] = _LOGGEDRESULT
DESCRIPTOR.message_types_by_name['Queries'] = _QUERIES
DESCRIPTOR.message_types_by_name['Row'] = _ROW
DESCRIPTOR.message_types_by_name['Rows'] = _ROWS
DESCRIPTOR.message_types_by_name['QueryResults'] = _QUERYRESULTS
DESCRIPTOR.enum_types_by_name['CompressionType'] = _COMPRESSIONTYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

LoggedResult = _reflection.GeneratedProtocolMessageType('LoggedResult', (_message.Message,), {
  'DESCRIPTOR' : _LOGGEDRESULT,
  '__module__' : 'fleetspeak.src.osquery.proto.fleetspeak_osquery.osquery_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.osquery.LoggedResult)
  })
_sym_db.RegisterMessage(LoggedResult)

Queries = _reflection.GeneratedProtocolMessageType('Queries', (_message.Message,), {

  'QueriesEntry' : _reflection.GeneratedProtocolMessageType('QueriesEntry', (_message.Message,), {
    'DESCRIPTOR' : _QUERIES_QUERIESENTRY,
    '__module__' : 'fleetspeak.src.osquery.proto.fleetspeak_osquery.osquery_pb2'
    # @@protoc_insertion_point(class_scope:fleetspeak.osquery.Queries.QueriesEntry)
    })
  ,

  'DiscoveryEntry' : _reflection.GeneratedProtocolMessageType('DiscoveryEntry', (_message.Message,), {
    'DESCRIPTOR' : _QUERIES_DISCOVERYENTRY,
    '__module__' : 'fleetspeak.src.osquery.proto.fleetspeak_osquery.osquery_pb2'
    # @@protoc_insertion_point(class_scope:fleetspeak.osquery.Queries.DiscoveryEntry)
    })
  ,
  'DESCRIPTOR' : _QUERIES,
  '__module__' : 'fleetspeak.src.osquery.proto.fleetspeak_osquery.osquery_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.osquery.Queries)
  })
_sym_db.RegisterMessage(Queries)
_sym_db.RegisterMessage(Queries.QueriesEntry)
_sym_db.RegisterMessage(Queries.DiscoveryEntry)

Row = _reflection.GeneratedProtocolMessageType('Row', (_message.Message,), {

  'RowEntry' : _reflection.GeneratedProtocolMessageType('RowEntry', (_message.Message,), {
    'DESCRIPTOR' : _ROW_ROWENTRY,
    '__module__' : 'fleetspeak.src.osquery.proto.fleetspeak_osquery.osquery_pb2'
    # @@protoc_insertion_point(class_scope:fleetspeak.osquery.Row.RowEntry)
    })
  ,
  'DESCRIPTOR' : _ROW,
  '__module__' : 'fleetspeak.src.osquery.proto.fleetspeak_osquery.osquery_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.osquery.Row)
  })
_sym_db.RegisterMessage(Row)
_sym_db.RegisterMessage(Row.RowEntry)

Rows = _reflection.GeneratedProtocolMessageType('Rows', (_message.Message,), {
  'DESCRIPTOR' : _ROWS,
  '__module__' : 'fleetspeak.src.osquery.proto.fleetspeak_osquery.osquery_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.osquery.Rows)
  })
_sym_db.RegisterMessage(Rows)

QueryResults = _reflection.GeneratedProtocolMessageType('QueryResults', (_message.Message,), {
  'DESCRIPTOR' : _QUERYRESULTS,
  '__module__' : 'fleetspeak.src.osquery.proto.fleetspeak_osquery.osquery_pb2'
  # @@protoc_insertion_point(class_scope:fleetspeak.osquery.QueryResults)
  })
_sym_db.RegisterMessage(QueryResults)


_QUERIES_QUERIESENTRY._options = None
_QUERIES_DISCOVERYENTRY._options = None
_ROW_ROWENTRY._options = None
# @@protoc_insertion_point(module_scope)
