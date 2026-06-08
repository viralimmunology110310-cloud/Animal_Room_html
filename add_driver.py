with open('index.html', 'r') as f:
    code = f.read()

# 1. Inject CSS and Script tags in <head>
head_injection = """    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/driver.js@1.0.1/dist/driver.css"/>
    <script src="https://cdn.jsdelivr.net/npm/driver.js@1.0.1/dist/driver.js.iife.js"></script>
    <style>
        /* Driver.js Custom Theme */
        .driverjs-theme {
            border: 2px solid #FF375F !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 30px rgba(255, 55, 95, 0.2) !important;
            padding: 20px !important;
        }
        .driver-popover-title {
            color: #FF375F !important;
            font-size: 18px !important;
            font-weight: 700 !important;
            margin-bottom: 10px !important;
        }
        .driver-popover-description {
            font-size: 14px !important;
            line-height: 1.5 !important;
        }
        .driver-popover-progress-text {
            color: #888 !important;
            font-size: 12px !important;
        }
        .driver-active-element {
            outline: 4px solid #FF375F !important;
            outline-offset: 4px !important;
            border-radius: 4px !important;
        }
        
        /* Floating Help Button */
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
        }
    </style>
"""
code = code.replace("</head>", head_injection + "</head>")

# 2. Inject FAB Button in body
fab_injection = """
<button class="help-fab" onclick="startTour()" title="사용법 가이드">💡</button>
"""
code = code.replace("</body>", fab_injection + "\n</body>")

# 3. Inject JS logic for startTour()
tour_js = """
<script>
function startTour() {
  const driver = window.driver.js.driver;
  const driverObj = driver({
    showProgress: true,
    nextBtnText: '다음 ❯',
    prevBtnText: '❮ 이전',
    doneBtnText: '완료',
    popoverClass: 'driverjs-theme',
    steps: [
      {
        popover: {
          title: '🐰 Small Animal Room 가이드',
          description: '환영합니다! 처음 오신 분들을 위해 <b>핵심 기능</b>을 빠르게 안내해 드릴게요.<br><br><b>다음 ❯</b> 버튼을 눌러주세요.'
        }
      },
      {
        element: '.top-right',
        popover: {
          title: '1. 상단 컨트롤 패널',
          description: '여러 케이지를 한 번에 지우거나 움직일 수 있는 <b>선택(Batch) 모드</b>를 켤 수 있으며, 데이터 패널과 메인 보드 간 <b>호버 연동</b> 기능을 On/Off 할 수 있습니다.',
          side: 'bottom', align: 'end'
        }
      },
      {
        element: '#config-box',
        popover: {
          title: '2. 품종 설정 및 휴지통',
          description: '버튼 색상에 맞는 <b>품종(Strain)</b> 코드를 생성 및 관리할 수 있습니다.<br>케이지를 버릴 땐 우측의 <b>휴지통 아이콘</b>으로 드래그 앤 드롭 하시면 됩니다!',
          side: 'top', align: 'start'
        }
      },
      {
        element: '#room-map',
        popover: {
          title: '3. 연구실 배치도 (Room Map)',
          description: 'A부터 E까지의 <b>Rack 버튼</b>을 클릭하면 화면에 해당 랙이 나타납니다. 한눈에 <b>공간 사용률</b>을 파악할 수 있는 미니맵 역할을 합니다.',
          side: 'right', align: 'start'
        }
      },
      {
        element: '#main-grid',
        popover: {
          title: '4. 메인 보드 (Rack Grid)',
          description: '빈 공간의 <b>+ 버튼</b>을 눌러 새 케이지를 생성하거나, 존재하는 케이지를 꾹 눌러 <b>자유롭게 이동</b>할 수 있습니다.',
          side: 'right', align: 'center'
        }
      },
      {
        element: '#pane-splitter',
        popover: {
          title: '5. 화면 크기 조절바',
          description: '화면이 좁게 느껴진다면, 이 <b>가운데 선</b>을 잡고 좌우로 끌어보세요. 왼쪽 보드와 오른쪽 시트의 비율을 마음대로 조절할 수 있습니다.',
          side: 'left', align: 'center'
        }
      },
      {
        element: '.sheet-pane',
        popover: {
          title: '6. 데이터 시트 패널',
          description: '구글 시트와 실시간 연동되는 정보들입니다. 표의 행에 <b>마우스를 올리거나(모바일은 터치)</b> 하면, 왼쪽 메인 보드에서 그 케이지가 <b>붉은색으로 깜빡이며</b> 내 위치를 알려줍니다!',
          side: 'left', align: 'start'
        }
      },
      {
        popover: {
          title: '🎉 가이드 완료!',
          description: '이 외에도 화면 맨 오른쪽 끝자락에 마우스를 가져가면 <b>Mating/Breeding 색상 매치 패널</b>이 열립니다.<br><br>이제 시스템을 직접 다뤄보세요!'
        }
      }
    ]
  });
  driverObj.drive();
}
</script>
"""
code = code.replace("</body>", tour_js + "\n</body>")
code = code.replace("const APP_VERSION = 'v2.7.13';", "const APP_VERSION = 'v2.7.14';")

with open('index.html', 'w') as f:
    f.write(code)

print("Driver.js walkthrough added")
