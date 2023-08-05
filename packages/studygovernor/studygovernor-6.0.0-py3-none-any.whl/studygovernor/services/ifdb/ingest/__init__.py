from .aneurysms import Aneurysm
from .corticalinfarcts import CorticalInfarcts
from .cysts import Cysts
from .tumors import Tumors
from .pituitary import Pituitary
from .calcifications import Calcifications
from .otherifs import OtherIfs
from .lacunarinfarcts import LacunarInfarcts
from .microbleeds import Microbleeds


ingestion_adapters = [Aneurysm, CorticalInfarcts, Cysts, Tumors, Pituitary, Calcifications, OtherIfs, LacunarInfarcts, Microbleeds]