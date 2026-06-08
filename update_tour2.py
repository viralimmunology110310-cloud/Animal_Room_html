import re

with open('index.html', 'r') as f:
    code = f.read()

old_tour = re.search(r"function startTour\(\) \{.*?\n\}", code, flags=re.DOTALL)

new_tour = """function startTour() {
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
          description: '환영합니다! 각 요소와 버튼이 어떤 역할을 하는지 상세히 안내해 드릴게요.<br><br><b>다음 ❯</b> 버튼을 눌러주세요.'
        }
      },
      {
        element: '.top-right',
        popover: {
          title: '1. 상단 컨트롤 메뉴',
          description: '우측 상단의 버튼들을 누르면 다음과 같은 기능이 실행됩니다:<br><br>• <b>선택 모드</b>: 여러 케이지를 클릭해 한 번에 다룹니다. (Ctrl 키로 다중 선택 가능)<br>• <b>요일 배정</b>: 케이지의 요일별 배경 색상을 지정합니다.<br>• <b>Strain 매칭표</b>: 품종별 기호와 이름을 커스텀합니다.<br>• <b>행 호버 연동</b>: 체크 시 오른쪽 리스트에 마우스를 올리면 메인 보드의 케이지가 깜빡입니다.',
          side: 'bottom', align: 'end'
        }
      },
      {
        element: '#btn-batch',
        popover: {
          title: '2. 선택 모드 고급 팁',
          description: '선택 모드일 때는 여러 케이지를 묶어서 한 번에 이동하거나 삭제할 수 있습니다.<br><br>💡 <b>단축키 지원</b>: Ctrl+X (잘라내기), Ctrl+C (복사), Ctrl+V (붙여넣기) 뿐만 아니라, <b>Ctrl+Z (실행 취소) 및 Ctrl+Y (다시 실행)</b> 기능도 완벽하게 지원합니다!',
          side: 'bottom', align: 'center'
        }
      },
      {
        element: '#config-box',
        popover: {
          title: '3. 랙 줄 수 설정',
          description: '이곳에서 Rack A~E의 <b>세로 줄 수(층 수)</b>를 변경할 수 있습니다. 랙의 크기가 달라지면 숫자를 조절하여 실제 배치와 일치시키세요.',
          side: 'top', align: 'start'
        }
      },
      {
        element: '#room-map',
        popover: {
          title: '4. 랙(Rack) 이동 및 공간 맵',
          description: 'A부터 E까지의 <b>알파벳 버튼을 클릭</b>하여 화면 중앙에 표시될 랙을 전환할 수 있습니다. 각 랙이 얼마나 찼는지 <b>공간 사용률</b>도 막대 그래프로 한눈에 확인 가능합니다.',
          side: 'right', align: 'start'
        }
      },
      {
        element: '#main-grid',
        popover: {
          title: '5. 메인 케이지 보드',
          description: '• <b>빈 공간 클릭</b>: 해당 위치에 새로운 케이지를 생성합니다.<br>• <b>케이지 클릭</b>: 케이지의 정보(Mating/Breeding 등)를 수정합니다.<br>• <b>케이지 드래그</b>: 케이지를 꾹 눌러 빈 공간으로 이동시킵니다.<br>💡 <b>휴지통</b>: 케이지를 꾹 누른 채 우측 하단 모서리로 끌고 가면 숨겨진 <b>휴지통 아이콘</b>이 나타나 삭제할 수 있습니다.',
          side: 'right', align: 'center'
        }
      },
      {
        element: '#pane-splitter',
        popover: {
          title: '6. 화면 크기 조절바',
          description: '이 <b>가운데 선</b>을 클릭한 채로 좌우로 끌어보세요. 왼쪽의 케이지 보드와 오른쪽 데이터 리스트의 비율을 내 모니터 크기에 맞춰 자유롭게 조절할 수 있습니다.',
          side: 'left', align: 'center'
        }
      },
      {
        element: '.sheet-pane',
        popover: {
          title: '7. 오른쪽 데이터 리스트',
          description: '구글 시트와 100% 동일하게 연동되는 실제 데이터 영역입니다.<br>• <b>행 클릭</b>: 해당 케이지의 정보 수정 창이 열립니다.<br>• <b>마우스 올리기(태블릿은 터치)</b>: 왼쪽 메인 보드에서 해당 케이지가 붉게 깜빡거리며 위치를 찾아줍니다!',
          side: 'left', align: 'start'
        }
      },
      {
        element: '.btn-log-view',
        popover: {
          title: '8. 로그 / 복구 시스템',
          description: '상단의 <b>[📄 로그 / 복구]</b> 버튼을 누르면 데이터 수정 기록이 나타납니다. 큰 실수를 했다면 이곳에서 <b>[🚨 데이터 긴급 복구]</b> 버튼을 눌러 과거 시점으로 되돌릴 수 있습니다.',
          side: 'bottom', align: 'center'
        }
      },
      {
        popover: {
          title: '🎉 가이드 완료!',
          description: '이제 Small Animal Room 시스템의 모든 고급 기능을 다룰 수 있습니다. 우측 하단의 전구 💡 버튼을 누르면 이 가이드를 언제든 다시 볼 수 있습니다.'
        }
      }
    ]
  });
  driverObj.drive();
}"""

if old_tour:
    code = code.replace(old_tour.group(0), new_tour)
    code = code.replace("const APP_VERSION = 'v2.7.15';", "const APP_VERSION = 'v2.7.16';")
    with open('index.html', 'w') as f:
        f.write(code)
    print("Tour updated 2")
else:
    print("Tour not found")
