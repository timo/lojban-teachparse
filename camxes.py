#!/bin/env python
import os
import subprocess

def find_camxes():
  return os.path.expanduser("~/lojban/lojban_peg_parser.jar")

def find_vlatai():
  return "vlatai"

camxesinstances = {}

def call_camxes(text, arguments=()):
  global camxesinstances
  arguments = tuple(arguments)
  if arguments in camxesinstances:
    sp = camxesinstances[arguments]
  else:
    camxesPath = find_camxes()
    sp = subprocess.Popen(["java", "-jar", camxesPath] + list(arguments),
                          stdin = subprocess.PIPE, stdout=subprocess.PIPE)
    # eat the "hello" line for each of the arguments
    for arg in arguments:
      a = sp.stdout.readline()
    camxesinstances[arguments] = sp
  sp.stdin.write(text)
  sp.stdin.write("\n")
  a = sp.stdout.readline()
  #newline = sp.stdout.readline()
  return a

def call_vlatai(text):
  vp = find_vlatai()
  vi = subprocess.Popen([vp], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
  vi.stdin.write(text)
  vi.stdin.write("\n")
  vi.stdin.close()
  res = vi.stdout.readline()
  data = [txt.strip() for txt in res.split(":")]
  return data

def selmaho(text):
  makfa = subprocess.Popen(["makfa", "selmaho", text], stdout=subprocess.PIPE)
  res = makfa.stdout.read().strip().split()
  print res
  word = res[0]
  selmaho = res[2]
  if "..." in selmaho:
      selmaho = selmaho.split("...")
  else:
      selmaho = [selmaho]
  links = res[3:]
  print (word, selmaho, links)
  return (word, selmaho, links)
