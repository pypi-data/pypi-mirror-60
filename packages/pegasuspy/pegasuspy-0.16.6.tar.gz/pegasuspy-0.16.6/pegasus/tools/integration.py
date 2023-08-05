from harmonypy import run_harmony
from anndata import AnnData

def integrate_data(
    data: AnnData,
    method: str = "harmony",
    rep: str = "pca",
    batch_key: str = "Channel",
) -> None:


def harmony(
    data: AnnData,
    rep: str = "pca",
    batch_key: str = "Channel",
) -> None:
