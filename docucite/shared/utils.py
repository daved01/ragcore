from typing import Any


def slice_list(input_list: list[Any], slice_size: int) -> list[list[Any]]:
    num_slices = (len(input_list) // slice_size) + (len(input_list) % slice_size > 0)
    return [
        input_list[i * slice_size : (i + 1) * slice_size] for i in range(num_slices)
    ]
