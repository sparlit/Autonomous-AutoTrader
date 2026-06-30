filepath = 'src/python/hive/coordinator.py'
with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if 'self.registry.stop_all()' in line:
        new_lines.append("        if hasattr(self, 'web_dash'): self.web_dash.terminate()\n")
        new_lines.append("        if hasattr(self, 'native_dash'): self.native_dash.terminate()\n")
    new_lines.append(line)

with open(filepath, 'w') as f:
    f.writelines(new_lines)
