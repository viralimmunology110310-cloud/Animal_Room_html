import re

with open('index.html', 'r') as f:
    code = f.read()

css_old = """        /* Floating Help Button */
        .help-fab {
            position: fixed;
            bottom: 25px;
            right: 25px;
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #FF375F, #FF6B8B);
            color: white;
            border: none;
            box-shadow: 0 6px 20px rgba(255, 55, 95, 0.4);
            font-size: 26px;
            cursor: pointer;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        }
        .help-fab:hover {
            transform: scale(1.1) translateY(-5px);
            box-shadow: 0 10px 25px rgba(255, 55, 95, 0.6);
        }
        .help-fab:active {
            transform: scale(0.95);
        }"""

css_new = """        /* Floating Help Button Wrapper */
        .help-fab-wrapper {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 120px;
            height: 120px;
            z-index: 9999;
            display: flex;
            align-items: flex-end;
            justify-content: flex-start;
            padding: 25px;
            /* To allow touch devices to trigger hover on tap */
            cursor: default;
        }
        .help-fab {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #FF375F, #FF6B8B);
            color: white;
            border: none;
            box-shadow: 0 6px 20px rgba(255, 55, 95, 0.4);
            font-size: 26px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            pointer-events: none; /* Disables clicking while hidden */
        }
        .help-fab-wrapper:hover .help-fab, .help-fab-wrapper:active .help-fab {
            transform: translateY(0);
            opacity: 1;
            pointer-events: auto; /* Re-enables clicking when visible */
        }
        .help-fab-wrapper .help-fab:hover {
            transform: scale(1.1) translateY(-5px);
            box-shadow: 0 10px 25px rgba(255, 55, 95, 0.6);
        }
        .help-fab-wrapper .help-fab:active {
            transform: scale(0.95);
        }"""

code = code.replace(css_old, css_new)

html_old = """<button class="help-fab" onclick="startTour()" title="사용법 가이드">💡</button>"""
html_new = """<div class="help-fab-wrapper" ontouchstart=""><button class="help-fab" onclick="startTour()" title="사용법 가이드">💡</button></div>"""
code = code.replace(html_old, html_new)

code = code.replace("const APP_VERSION = 'v2.7.16';", "const APP_VERSION = 'v2.7.17';")

with open('index.html', 'w') as f:
    f.write(code)
print("FAB updated")
