#!/usr/bin/env python
RCedh=True
RCedA=Exception
RCedB=str
RCedy=len
RCedi=isinstance
RCedm=dict
RCedN=hasattr
RCedw=int
RCedv=False
RCedp=bytes
import os
import sys
import json
import uuid
import logging
import tempfile
import subprocess
import boto3
import shutil
import requests
from six.moves.socketserver import ThreadingMixIn
from six.moves.BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
LOG=logging.getLogger('local_daemon')
DEFAULT_PORT_LOCAL_DAEMON=4535
DEFAULT_PORT_S3=4572
DEFAULT_PORT_EC2=4597
ENDPOINT_S3='http://localhost:%s'%DEFAULT_PORT_S3
ENDPOINT_EC2='http://localhost:%s'%DEFAULT_PORT_EC2
BUCKET_MARKER_LOCAL='__local__'
os.environ['AWS_ACCESS_KEY_ID']='test'
os.environ['AWS_SECRET_ACCESS_KEY']='test'
class ThreadedHTTPServer(ThreadingMixIn,HTTPServer):
 daemon_threads=RCedh
class RequestHandler(BaseHTTPRequestHandler):
 def do_POST(self):
  self.read_content()
  try:
   result=self.handle_request()
   self.send_response(200)
  except RCedA as e:
   error_string=RCedB(e)
   result=json.dumps({'error':error_string})
   self.send_response(500)
  self.send_header('Content-Length','%s'%RCedy(result)if result else 0)
  self.end_headers()
  if RCedy(result or ''):
   self.wfile.write(to_bytes(result))
 def handle_request(self):
  request=self.request_json
  result='{}'
  operation=request.get('op')
  if operation=='getos':
   result={'result':get_os()}
  elif operation=='shell':
   command=request.get('command')
   result=run_shell_cmd(command)
  elif operation=='s3:download':
   result=s3_download(request)
  elif operation=='kill':
   log('Terminating local daemon process')
   os._exit(0)
  else:
   result={'error':'Unsupported operation "%s"'%operation}
  result=json.dumps(result)if RCedi(result,RCedm)else result
  return result
 def read_content(self):
  if RCedN(self,'data_bytes'):
   return
  content_length=self.headers.get('Content-Length')
  self.data_bytes=self.rfile.read(RCedw(content_length))
  self.request_json={}
  try:
   self.request_json=json.loads(self.data_bytes)
  except RCedA:
   pass
def s3_download(request):
 bucket=request['bucket']
 key=request['key']
 tmp_dir=os.environ.get('TMPDIR')or tempfile.mkdtemp()
 target_file=os.path.join(tmp_dir,request.get('file_name')or 's3file.%s'%RCedB(uuid.uuid4()))
 if not os.path.exists(target_file)or request.get('overwrite'):
  if bucket==BUCKET_MARKER_LOCAL:
   shutil.copy(key,target_file)
  else:
   s3=boto3.client('s3',endpoint_url=ENDPOINT_S3)
   log('Downloading S3 file s3://%s/%s to %s'%(bucket,key,target_file))
   s3.download_file(bucket,key,target_file)
 return{'local_file':target_file}
def run_shell_cmd(command):
 try:
  return{'result':run(command)}
 except RCedA as e:
  error_string=RCedB(e)
  if RCedi(e,subprocess.CalledProcessError):
   error_string='%s: %s'%(error_string,e.output)
  return{'error':error_string}
def get_os():
 if is_mac_os():
  return 'macos'
 if is_linux():
  return 'linux'
 return 'windows'
def run(cmd):
 log('Running command: %s'%cmd)
 return to_str(subprocess.check_output(cmd,stderr=subprocess.STDOUT,shell=RCedh))
def log(*args):
 print(*args)
 sys.stdout.flush()
def is_mac_os():
 try:
  out=to_str(subprocess.check_output('uname -a',shell=RCedh))
  return 'Darwin' in out
 except subprocess.CalledProcessError:
  return RCedv
def is_linux():
 try:
  out=to_str(subprocess.check_output('uname -a',shell=RCedh))
  return 'Linux' in out
 except subprocess.CalledProcessError:
  return RCedv
def to_bytes(obj):
 return obj.encode('utf-8')if RCedi(obj,RCedB)else obj
def to_str(obj):
 return obj.decode('utf-8')if RCedi(obj,RCedp)else obj
def start_server(port):
 try:
  requests.post('http://localhost:%s'%port,data='{"op":"kill"}')
 except RCedA:
  pass
 try:
  log('Starting local daemon server on port %s'%port)
  httpd=ThreadedHTTPServer(('0.0.0.0',port),RequestHandler)
  httpd.serve_forever()
 except RCedA:
  log('Local daemon server already running, or port %s not available'%port)
  pass
def main():
 logging.basicConfig()
 port=DEFAULT_PORT_LOCAL_DAEMON
 start_server(port)
def start_in_background():
 from localstack.config import TMP_FOLDER
 from localstack.utils.common import run
 log_file=os.path.join(TMP_FOLDER,'localstack_daemon.log')
 LOG.info('Logging local daemon output to %s'%log_file)
 cmd='python %s'%__file__
 run(cmd,outfile=log_file,asynchronous=RCedh)
if __name__=='__main__':
 main()
# Created by pyminifier (https://github.com/liftoff/pyminifier)
