from canoser import Struct, Uint64, Uint8, bytes_to_int_list
from libra.hasher import gen_hasher
from libra.language_storage import TypeTag
from libra.account_config import SentPaymentEvent, ReceivedPaymentEvent
from libra.event import EventKey

class ContractEvent(Struct):
    _fields = [
        ('key', EventKey),
        ('event_seq_num', Uint64), # change sequence_number to event_seq_num
        ('type_tag', TypeTag),
        ('event_data', [Uint8])
    ]

    @classmethod
    def from_proto(cls, event_proto):
        ret = cls()
        ret.key = bytes_to_int_list(event_proto.key)
        ret.event_seq_num = event_proto.sequence_number
        ret.type_tag = TypeTag.deserialize(event_proto.type_tag)
        ret.event_data = bytes_to_int_list(event_proto.event_data)
        if ret.type_tag.Struct and ret.type_tag.value.is_pay_tag():
            if ret.type_tag.value.name == "SentPaymentEvent":
                ret.event_data_decode = SentPaymentEvent.deserialize(event_proto.event_data)
            elif ret.type_tag.value.name == "ReceivedPaymentEvent":
                ret.event_data_decode = ReceivedPaymentEvent.deserialize(event_proto.event_data)
            else:
                raise AssertionError(f"Unknown event: {ret.type_tag.value}")
        return ret

    @classmethod
    def from_proto_event_with_proof(cls, event_with_proof):
        ret = cls.from_proto(event_with_proof.event)
        ret.transaction_version = event_with_proof.transaction_version
        ret.event_index = event_with_proof.event_index
        return ret

    def to_json_serializable(self):
        amap = super().to_json_serializable()
        if hasattr(self, 'transaction_version'):
            amap["transaction_version"] = self.transaction_version
        if hasattr(self, 'event_index'):
            amap["event_index"] = self.event_index
        if hasattr(self, 'event_data_decode'):
            amap["event_data_decode"] = self.event_data_decode.to_json_serializable()
        return amap

    def hash(self):
        shazer = gen_hasher(b"ContractEvent::libra_types::contract_event")
        shazer.update(self.serialize())
        return shazer.digest()
