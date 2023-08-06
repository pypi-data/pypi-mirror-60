from typing import Any, Dict

from .protocol import Endpoints, InfoCommandBase, ProtoConstants, get_json_obj


class GetPowerStateCommand(InfoCommandBase):
    def __init__(self, device_type: str) -> None:
        super(GetPowerStateCommand, self).__init__()
        InfoCommandBase.url.fset(self, Endpoints.ENDPOINTS[device_type]["POWER"])

    def process_response(self, json_obj: Dict[str, Any]) -> bool:
        items = get_json_obj(json_obj, ProtoConstants.RESPONSE_ITEMS)
        is_awake = False
        if len(items) > 0:
            is_awake = 1 == get_json_obj(items[0], ProtoConstants.Item.VALUE)

        return is_awake
