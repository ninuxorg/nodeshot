from nodeshot.core.base.utils import choicify


POLARIZATIONS = {
    'horizonal': 1,
    'vertical': 2,
    'circular': 3,
    'linear': 4,
    'dual_linear': 5
}

POLARIZATION_CHOICES = choicify(POLARIZATIONS)
