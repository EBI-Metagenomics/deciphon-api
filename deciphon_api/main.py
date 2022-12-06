from deciphon_api.app import get_app
from deciphon_api.config import get_config
from deciphon_api.depo import get_depo
from deciphon_api.sched import get_sched

__all__ = ["app"]

config = get_config()
sched = get_sched()
depo = get_depo()
app = get_app()
