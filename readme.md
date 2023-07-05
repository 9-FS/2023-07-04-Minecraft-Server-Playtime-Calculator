---
Topic: "Minecraft Server Playtime Calculator"
Author: "구FS"
---
<link href="./doc_templates/md_style.css" rel="stylesheet"></link>
<body>

# <p style="text-align: center;">Minecraft Server Playtime Calculator</p>
<br>
<br>

- [1. General](#1-general)

## 1. General

This bot loads all log files from `config.json`, `log_path` and then calculates the total player playtime by summing up the timespans between "{player} joined the game" and "{player} left the game" entries. Finally, the results of all offline players are periodically written into objective `player_playtime`.

<div style="page-break-after: always;"></div>

</body>