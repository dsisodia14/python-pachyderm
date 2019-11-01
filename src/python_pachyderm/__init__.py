import string as string
import importlib as importlib
import enum as enum
from google.protobuf.internal.enum_type_wrapper import EnumTypeWrapper as _EnumTypeWrapper

from .client import Client
from grpc import RpcError

__all__ = ["Client", "RpcError"]


def _import_protos(path):
    """
    Imports items selectively from the auto-generated proto package.

    Importing is done dynamically so we can selectively blacklist items. We
    also dynamically define enums that build on top of the auto-generated
    protobuf enums, to create a more pythonic API.

    More broadly, the dark magic in here allows us to maintain parity with
    Pachyderm protobufs when they change, without having to maintain a manual
    mapping of protobuf to python_pachyderm values.
    """

    g = globals()
    module = importlib.import_module(path)
    uppercase_letters = set(string.ascii_uppercase)
    lowercase_letters = set(string.ascii_lowercase)

    is_importable = lambda k: k[0] in uppercase_letters and any(c in lowercase_letters for c in k[1:])

    def import_item(g, module, key):
        value = getattr(module, key)

        if isinstance(value, _EnumTypeWrapper):
            # Dynamically define an enum class that is exported
            enum_values = enum._EnumDict()
            enum_values.update(dict(value.items()))
            enum_class = type(key, (enum.IntEnum,), enum_values)
            g[key] = enum_class
        else:
            # Export the value
            g[key] = value

        __all__.append(key)

    for key in dir(module):
        if is_importable(key):
            import_item(g, module, key)
        elif key.startswith("google_dot_protobuf_dot_"):
            sub_module = getattr(module, key)
            for key in dir(sub_module):
                if is_importable(key):
                    import_item(g, sub_module, key)


_import_protos("python_pachyderm.proto.pfs.pfs_pb2")
_import_protos("python_pachyderm.proto.pps.pps_pb2")
_import_protos("python_pachyderm.proto.version.versionpb.version_pb2")
_import_protos("python_pachyderm.proto.transaction.transaction_pb2")
_import_protos("python_pachyderm.proto.admin.admin_pb2")
