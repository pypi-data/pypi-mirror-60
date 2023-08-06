from typing import Union

from jigu.util import hash_amino
from jigu.core import Block

class BlocksIterator(object):
    def __init__(self, blocks, start, stop, step):
        self.blocks = blocks
        self.i = start
        t = len(blocks)
        if stop:
            if stop >= 0:
                self.stop = stop
            else:
                self.stop = t + stop
        else:
            self.stop = t
        self.step = step if step else 1

    def __iter__(self):
        return self

    def __next__(self):
        if self.i >= self.stop:
            raise StopIteration()
        else:
            self.i += self.step
            return self.blocks[self.i]


class Blocks(object):
    def __init__(self, terra):
        self.terra = terra

    def __getitem__(self, key: Union[int, slice]):
        if isinstance(key, int):
            if key >= 0:
                block_data = self.terra._tendermint.get_block(height=key + 1)
            else:
                max_height = len(self)
                block_data = self.terra._tendermint.get_block(
                    height=max_height + key + 1
                )
            return Block.from_dict(block_data, self.terra)
        elif isinstance(key, slice):
            return BlocksIterator(self, key.start, key.stop, key.step)
        else:
            raise TypeError(
                "invalid type for blocks[key], `key` must be <int> or <slice>"
            )

    def __len__(self):
        block = self.terra._tendermint.get_block()
        return int(block["header"]["height"])
