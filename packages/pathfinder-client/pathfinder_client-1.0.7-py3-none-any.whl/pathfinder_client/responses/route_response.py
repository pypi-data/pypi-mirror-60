from typing import List


from .base_response import BaseResponse


class RouteResponse(BaseResponse):
    points: List[List[float]]
    segment_lengths: List[float]
    total_length: float
