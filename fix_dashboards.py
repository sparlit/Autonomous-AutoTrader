import sys
import os

filepath = 'src/python/hive/coordinator.py'
with open(filepath, 'r') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if 'asyncio.create_task(self.watchdog.run())' in line:
        new_lines.append("\n")
        new_lines.append("        # 10450: Launch Monitoring Dashboards\n")
        new_lines.append("        self.web_dash = WebDashboard(ipc=self.ipc, port=self.config.bridge.dashboard_port)\n")
        new_lines.append("        self.web_dash.start()\n")
        new_lines.append("\n")
        new_lines.append("        self.native_dash = NativeDashboard(ipc=self.ipc)\n")
        new_lines.append("        self.native_dash.start()\n")

with open(filepath, 'w') as f:
    f.writelines(new_lines)
