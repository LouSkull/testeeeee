def check(version):
  from include.utils.http import get
  response = get("https://pastebin.com/raw/DiGfV4qv")
  response_value = float(response)

  if response_value == version:
    return True
  else:
    return False
  