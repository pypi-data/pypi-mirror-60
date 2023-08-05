# borrow from https://github.com/RobinBruegger/RevTorch/blob/master/revtorch/revtorch.py
# until https://github.com/RobinBruegger/RevTorch/issues/3 is resolved 
import torch
from torch import nn
import sys
import random

class ReversibleBlock(nn.Module):
    def __init__(self, f_block, g_block, split_along_dim=1, fix_random_seed = False):
        super(ReversibleBlock, self).__init__()
        self.f_block = f_block
        self.g_block = g_block
        self.split_along_dim = split_along_dim
        self.fix_random_seed = fix_random_seed
        self.random_seeds = {}

    def set_seed(self, namespace, new = False):
        if not self.fix_random_seed:
            return
        if new:
            self.random_seeds[namespace] = random.randint(0, sys.maxsize)
        torch.manual_seed(self.random_seeds[namespace])

    def forward(self, x):
        x1, x2 = torch.chunk(x, 2, dim=self.split_along_dim)
        y1, y2 = None, None
        with torch.no_grad():
            self.set_seed('f', new=True)
            y1 = x1 + self.f_block(x2)
            self.set_seed('g', new=True)
            y2 = x2 + self.g_block(y1)

        return torch.cat([y1, y2], dim=self.split_along_dim)

    def backward_pass(self, y, dy):
        y1, y2 = torch.chunk(y, 2, dim=self.split_along_dim)
        del y

        dy1, dy2 = torch.chunk(dy, 2, dim=self.split_along_dim)
        del dy

        y1.requires_grad = True
        y2.requires_grad = True

        with torch.enable_grad():
            self.set_seed('g')
            gy1 = self.g_block(y1)
            gy1.backward(dy2)

        with torch.no_grad():
            x2 = y2 - gy1
            del y2, gy1
            dx1 = dy1 + y1.grad
            del dy1
            y1.grad = None

        with torch.enable_grad():
            x2.requires_grad = True
            self.set_seed('f')
            fx2 = self.f_block(x2)
            fx2.backward(dx1)

        with torch.no_grad():
            x1 = y1 - fx2
            del y1, fx2

            dx2 = dy2 + x2.grad
            del dy2
            x2.grad = None

            x = torch.cat([x1, x2.detach()], dim=self.split_along_dim)
            dx = torch.cat([dx1, dx2], dim=self.split_along_dim)

        return x, dx

class _ReversibleModuleFunction(torch.autograd.function.Function):
    @staticmethod
    def forward(ctx, x, reversible_blocks):
        assert (isinstance(reversible_blocks, nn.ModuleList))
        for block in reversible_blocks:
            assert (isinstance(block, ReversibleBlock))
            x = block(x)
        ctx.y = x.detach()
        ctx.reversible_blocks = reversible_blocks
        return x

    @staticmethod
    def backward(ctx, dy):
        y = ctx.y
        del ctx.y
        for i in range(len(ctx.reversible_blocks) - 1, -1, -1):
            y, dy = ctx.reversible_blocks[i].backward_pass(y, dy)
        del ctx.reversible_blocks
        return dy, None

class ReversibleSequence(nn.Module):
    def __init__(self, reversible_blocks):
        super(ReversibleSequence, self).__init__()
        self.reversible_blocks = reversible_blocks

    def forward(self, x):
        x = _ReversibleModuleFunction.apply(x, self.reversible_blocks)
        return x