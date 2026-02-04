import subprocess
from default_app import app_data

output = subprocess.check_output(["mpremote"], text=True)
print(output)

# print(result)