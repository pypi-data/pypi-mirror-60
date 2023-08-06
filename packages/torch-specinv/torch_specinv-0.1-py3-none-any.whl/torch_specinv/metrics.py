import torch


def spectral_convergence(input: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    r"""
    The Spectral Convergence score is calculated as follow:

    .. math::
        \mathcal{C}(\mathbf{S}_i, \mathbf{S}_t)=\frac{\|\mathbf{S}_i-\mathbf{S}_t\|_{Fro}}{\|\mathbf{S}_t\|_{Fro}}

    Returns:
        scalar output in db scale.
    """
    return 20 * ((input - target).norm().log10() - target.norm().log10())


def SNR(input, target):
    r"""
    The Signal-to-Noise Ratio (SNR) is calculated as follow:

    .. math::
        SNR(\mathbf{\hat{S}}, \mathbf{S})=
        10\log_{10}\frac{1}{\sum (\frac{\hat{s}}{\|\mathbf{\hat{S}}\|_{Fro}} - \frac{s}{\|\mathbf{S}\|_{Fro}})^2}

    Returns:
        scalar output.
    """
    return -10 * (input / input.norm() - target / target.norm()).pow(2).sum().log10()


def SER(input, target):
    r"""
    The Signal-to-Error Ratio (SER) is calculated as follow:

    .. math::
        SER(\mathbf{\hat{S}}, \mathbf{S})=
        10\log_{10}\frac{\sum \hat{s}^2}{\sum (\hat{s} - s)^2}

    Returns:
        scalar output.
    """
    return 10 * (input.pow(2).sum().log10() - (input - target).pow(2).sum().log10())
