import re

with open('apps_script/Re.js', 'r') as f:
    content = f.read()

# Fix doGet to inject action: 'save'
old_get = """       const mockEvent = {
           postData: {
               contents: JSON.stringify(data)
           }
       };"""
       
new_get = """       data.action = 'save';
       const mockEvent = {
           postData: {
               contents: JSON.stringify(data)
           }
       };"""

# I previously overwrote doGet completely in test_get.py!
# I need to restore the correct doGet first!
