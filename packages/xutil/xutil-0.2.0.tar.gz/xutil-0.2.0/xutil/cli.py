import os, sys, argparse, re
from xutil import log


def pykill(*args_):
  "Kill processes based on name"

  import psutil

  args = sys.argv[1:] or args_
  if not args:
    log('~Need one argument to kill processes!')
    return

  kw = args[0]
  user = os.getenv('USER')
  skip_list = set(['login'])
  this_pid = os.getpid()

  procs_matched = []
  for proc in psutil.process_iter():
    pid = proc.pid
    name = proc.name()

    if not kw.strip(
    ) or user != proc.username() or name in skip_list or pid == this_pid:
      continue
    cmdline = ' '.join(proc.cmdline())

    try:
      if kw.lower() in cmdline.lower():
        proc.terminate()
        log('+Killed {} : {}'.format(pid, cmdline))
        procs_matched.append(proc)
    except Exception as E:
      log('-Could not kill {} : {}'.format(pid, name))
      log(E)

    if len(procs_matched) == 0:
      log('-Did not match any process name.')


def create_profile():
  "Create profile.yaml if it does not exists"
  from xutil.helpers import get_profile
  get_profile(create_if_missing=True)
  log('+YAML Profile located @ {}'.format(os.environ['PROFILE_YAML']))



def alias_cli():
  "Install alias"
  from xutil.helpers import get_home_path, get_dir_path, get_script_path
  from xutil.diskio import read_file, write_file
  from shutil import copyfile
  ans = input("Install 'alias.sh' in home directory (Y to proceed)? ")
  if ans.lower() != 'y':
    return

  src_path = get_dir_path() + '/alias.sh'
  dst_path = get_home_path() + '/.xutil.alias.sh'
  bash_profile_path = get_home_path() + '/.bashrc'

  # log('src_path -> ' + src_path)
  # log('dst_path -> ' + dst_path)
  copyfile(src_path, dst_path)

  bash_prof_text = read_file(bash_profile_path)

  if not dst_path in bash_prof_text:
    bash_prof_text = '{}\n\n. {}\n'.format(bash_prof_text, dst_path)
    write_file(bash_profile_path, bash_prof_text)
    log('+Updated ' + bash_profile_path)


def exec_sql():
  from xutil.database.etl import SqlCmdParser
  SqlCmdParser()

def profile_entry():
  from xutil.helpers import load_profile, save_profile
  from collections import OrderedDict
  import urllib.parse as urlparse
  import yaml


  parser = argparse.ArgumentParser(description='Profile Entry Maker')
  parser.add_argument('--url', help='the URL')
  parser.add_argument('--name', help='Database Name')
  parser.add_argument('--url_type', help='Type of URL (SQL Alchemy is default)')
  parser.add_argument('--add', action='store_true', help='Whether to add to current profile.yaml')
  args = parser.parse_args()

  if not (args.url and args.name):
    raise Exception("Need to provide --url and --name")
  
  url_vars = urlparse.urlparse(args.url)

  prof = {}

  prof['name'] = args.name
  prof['host'] = url_vars.hostname
  prof['port'] = url_vars.port
  prof['user'] = url_vars.username
  prof['password'] = url_vars.password
  prof['database'] = url_vars.path[1:]
  prof['type'] = url_vars.scheme

  if 'postgres' in prof['type']:
    prof['type'] = 'postgresql'
  if 'mssql' in prof['type']:
    prof['type'] = 'sqlserver'
  if 'oracle' in prof['type']:
    prof['type'] = 'oracle'
  
  if prof['type'] in ('postgresql', 'redshift'):
    prof['sslmode'] = 'require'
    prof['url'] = f"jdbc:postgresql://{prof['host']}:{prof['port']}/{prof['database']}"
    prof['sa_url'] = args.url

  if args.add:
    profile_yaml = load_profile()
    profile_yaml['databases'][args.name] = prof
    save_profile(profile_yaml)
    log('+ Set "{}" in profile.yaml'.format(args.name))
  else:
    print(yaml.dump({args.name : prof}))

def exec_etl():
  from xutil.database.etl import EtlCmdParser
  EtlCmdParser()


def ipy_imports(launch_spark=False):
  from xutil.helpers import (log, get_exception_message, get_error_str, get_profile)
  from xutil.database.base import get_conn
  from xutil.diskio import (write_csv, read_csv, read_file, write_file,
                            get_hdfs)
  from jmespath import search
  from pathlib import Path
  from collections import Counter, namedtuple, OrderedDict
  import time, datetime

  if launch_spark:
    from xutil.database.spark import Spark
    parser = argparse.ArgumentParser(description='Spark IPython')
    parser.add_argument(
      '--master', help='Master string for Spark Instance')
    parser.add_argument(
      '--profile', help='Database profile name from PROFILE_YAML')
    args = parser.parse_args()
    dbs = get_profile(create_if_missing=True)['databases']
    if args.profile and args.profile in dbs and dbs[args.profile]['type'].lower() in ('hive', 'spark'):
      conn = get_conn(args.profile)
      globals()['sparko'] = conn.sparko
    elif args.profile:
      log(Exception('Profile {} not found or incompatible.'.format(args.profile)))
      sys.exit(1)
    else:
      globals()['sparko'] = Spark(master=args.master)
    globals()['sc'] = sparko.sc
    globals()['spark'] = sparko.spark

  ldict = locals()
  for name in ldict:
    var = ldict[name]
    if callable(var) or isinstance(var, __builtins__.__class__):
      # is a function or class or module
      globals()[name] = var


def ipy(launch_spark=False):
  import IPython
  ipy_imports(launch_spark=launch_spark)
  IPython.embed(using=False) # https://github.com/ipython/ipython/issues/11523


def ipy_spark():
  ipy(launch_spark=True)