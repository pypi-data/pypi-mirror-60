__version__ = '0.5.0'
git_version = '14d65951ce87c8c2eb1547a39ce42fbafc599eab'
from torchvision.extension import _check_cuda_version
if _check_cuda_version() > 0:
    cuda = _check_cuda_version()
