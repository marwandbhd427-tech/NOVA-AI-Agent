import os,platform,shutil
from datetime import datetime
def system_info():return {'python':platform.python_version(),'platform':platform.platform(),'machine':platform.machine(),'cwd':os.getcwd(),'disk_free_bytes':shutil.disk_usage(os.getcwd()).free,'time':datetime.now().isoformat()}
