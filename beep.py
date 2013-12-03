import sys

if sys.platform == "win32":    

   import winsound

   def beep():
       winsound.Beep(2000, 500) 

else:

   import alsaaudio
   import base64

   wave = base64.decodestring(
   """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""")

   d = alsaaudio.PCM()
   d.setchannels(1)
   d.setrate(8000)
   d.setformat(alsaaudio.PCM_FORMAT_S16_LE)

   def beep():
      global d
      global wave
      d.write(wave) 

   

   


