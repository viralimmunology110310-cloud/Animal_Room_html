with open('index.html', 'r') as f:
    code = f.read()

import re

# We will replace the title string completely to use JS document.write or we just replace the hardcoded v2.7.12
# The title looks like: <h1 onclick="alert('현재 로드된 브라우저 버전: ' + APP_VERSION)">Small Animal Room Status <span style="font-size:14px; color:var(--mating-color); font-weight:bold; margin-left:6px; cursor:pointer;" title="버전 확인">v2.7.5</span></h1>

new_title = """<h1 onclick="alert('현재 로드된 브라우저 버전: ' + APP_VERSION)">Small Animal Room Status <span id="title-version-span" style="font-size:14px; color:var(--mating-color); font-weight:bold; margin-left:6px; cursor:pointer;" title="버전 확인">v2.7.13</span></h1>"""

code = re.sub(
    r"<h1 onclick=\"alert\('현재 로드된 브라우저 버전: ' \+ APP_VERSION\)\">Small Animal Room Status <span.*?</span></h1>",
    new_title,
    code
)

# Add a tiny script at the end of body to ensure it always matches APP_VERSION
sync_script = """<script>
document.getElementById('title-version-span').innerText = APP_VERSION;
</script>
</body>"""

code = code.replace("</body>", sync_script)
code = code.replace("const APP_VERSION = 'v2.7.12';", "const APP_VERSION = 'v2.7.13';")

with open('index.html', 'w') as f:
    f.write(code)
print("Title fixed")
