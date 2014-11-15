import os, time
path_to_watch = r"C:\Users\joze1\Dropbox\PrintQueue"
before = dict ([(f, None) for f in os.listdir (path_to_watch)])
while 1:
  time.sleep (10)
  after = dict ([(f, None) for f in os.listdir (path_to_watch)])
  added = [f for f in after if not f in before]
  removed = [f for f in before if not f in after]
  if added:
    for f in added:
      print(r"""C:\Users\joze1\Dropbox\PrintQueue\print.bat "C:\Users\joze1\Dropbox\PrintQueue\%s" """ % f)
      os.system(r"""C:\Users\joze1\Dropbox\PrintQueue\print.bat "C:\Users\joze1\Dropbox\PrintQueue\%s" """ % f)
  if removed: print("Removed: ", ", ".join (removed))
  before = after